import requests as rq
import json
import argparse
import sys
import configparser
import io

QUIET=False

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    NC='\033[0m'
    GREEN='\033[1;32m'
    RED='\033[1;31m'


class ZT_Network(object):

    def __init__(self,json_data):
        self.id=json_data['id']
        self.clock = json_data['clock']
        self.name = json_data['config']['name']

class ZT_API(object):

    def __init__(self,token,nf):
        pre_head= "bearer " + token
        self.header = { "Authorization": pre_head }
        self.net_conf_file=nf

    def list_networks(self):
        n=rq.get("https://my.zerotier.com/api/network",headers=self.header).json()
        networks=[]
        for i in n:
            j= ZT_Network(i)
            networks.append(j)
        return networks

    def create_network(self,network_name):
        n=json.load(open(self.net_conf_file,'r'))
        n['config']['name']=network_name
        net=ZT_Network(rq.post("https://my.zerotier.com/api/network",headers=self.header,json=n).json())
        if net.id:
            if QUIET:
                print(net.id)
            else:
                print(f"{bcolors.GREEN}Success!{bcolors.NC} {net.name} was created with the id {bcolors.RED}{net.id}{bcolors.NC}")
        else:
            if QUIET:
                print("Failure")
            else:
                print(f"{bcolors.RED}Failure!{bcolors.NC} Could not create network")
            sys.exit(1)

    def delete_network(self,network_name):
        nets=self.list_networks()
        net_id=""
        for i in nets:
            if i.name == network_name:
                net_id=i.id
        if net_id =="":
            if QUIET:
                print("Failure")
            else:
                print(f"{bcolors.RED}Failure:{bcolors.NC} {bcolors.OKBLUE}{network_name}{bcolors.NC} network was not found.")
            return
        r=rq.delete(f"https://my.zerotier.com/api/network/{net_id}",headers=self.header)
        if r.status_code == 200:
            if QUIET:
                print("Sucess")
            else:
                print(f"{bcolors.GREEN}Success!{bcolors.NC} {network_name} was deleted.")
        else:
            if QUIET:
                print("Failure")
            else:
                print(f"{bcolors.RED}Failure!{bcolors.NC} Deletion of {network_name} failed.")
            sys.exit(1)

def main ():
    global QUIET
    config=configparser.ConfigParser()
    config.read('.zt.ini')
    token=config["api"]["token"]
    if not token:
        print(f"{bcolors.RED}API Token Not Set!{bcolors.NC}\nPlease set the token in the \'.zt.ini\' file.")
        sys.exit(1)
    new_network_default=config["api"]["new_network_config"]
    parser=argparse.ArgumentParser(description="ZeroTier Administration script:",epilog="Make sure that the .zt.ini file is set with your ZeroTier API token.")
    parser.add_argument("-c", "--create",help="Create a new ZeroTier network",metavar="network_name")
    parser.add_argument("-d", "--delete",help="Delete a ZeroTier network",metavar="network_name")
    parser.add_argument('-l',"--list", action='store_true', help="List all current ZeroTier networks")
    parser.add_argument('--quiet',action="store_true",help="Output only neccessary items (used for chaining with other scripts)")
    args=parser.parse_args()
    if not args.create and not args.delete and not args.list:
        parser.print_help()
        sys.exit(0)
    if args.quiet:
        QUIET=True
    z=ZT_API(token,new_network_default)
    if args.list:
        nets=z.list_networks()
        for i in nets:
            print(f"{bcolors.GREEN}{i.name}{bcolors.NC} : {bcolors.RED}{i.id}{bcolors.NC}")
    elif args.create:
        z.create_network(args.create)
    elif args.delete:
        z.delete_network(args.delete)

   
    
if __name__ == "__main__":
    main()