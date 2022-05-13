import os
import argparse
from kubernetes import client, config
from k8s_enum.loader import ENUMERATORS, load_enumerators
from k8s_enum.enumerators.base_enum import filter_by_namespace


print(
    """
    __   ____       ______                    
   / /__( __ )_____/ ____/___  __  ______ ___ 
  / //_/ __  / ___/ __/ / __ \/ / / / __ `__ \\
 / ,< / /_/ (__  ) /___/ / / / /_/ / / / / / /
/_/|_|\____/____/_____/_/ /_/\__,_/_/ /_/ /_/ 
Kubernetes Enumerator                                            
"""
)

# TODO: Move
class EnumClient:
    def __init__(self, config_file=None):
        config.load_kube_config(config_file=config_file)
        self.v1_core = client.CoreV1Api()
        self.v1_rbac = client.RbacAuthorizationV1Api()


parser = argparse.ArgumentParser()
parser.add_argument("-en", "--exclude-namespaces", action="append", default=[])
parser.add_argument("-er", "--exclude-role-prefix", action="append", default=[])
parser.add_argument(
    "resources", choices=["all"] + [enumerator for enumerator in ENUMERATORS], nargs="+"
)
args = parser.parse_args()

# Enable colors for ANSI
if os.name == "nt":
    os.system("color")

enum_client = EnumClient()

filters = {
    "namespace_filter": args.exclude_namespaces,
    "role_filter": args.exclude_role_prefix,
}


def main():
    enumerators = load_enumerators(args.resources)
    for enumerator in enumerators:
        enumerator.enumerate(enum_client, **filters)
