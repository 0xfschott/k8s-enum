from importlib import import_module
from typing import Any

ENUMERATORS = {
    "nodes": "k8s_enum.enumerators.node_enum",
    "namespaces": "k8s_enum.enumerators.namespace_enum",
    "pods": "k8s_enum.enumerators.pod_enum",
    "secrets": "k8s_enum.enumerators.secret_enum",
    "service_accounts": "k8s_enum.enumerators.rbac.service_account_enum",
    "users": "k8s_enum.enumerators.rbac.user_enum",
    "groups": "k8s_enum.enumerators.rbac.group_enum",
    "roles": "k8s_enum.enumerators.rbac.role_enum",
    "cluster_roles": "k8s_enum.enumerators.rbac.cluster_role_enum",
}


def load_enumerators(enumerators: list[str] = []) -> Any:
    if "all" in enumerators:
        enumerators = [enumerator for enumerator in ENUMERATORS]
    return [import_module(ENUMERATORS[enumerator]) for enumerator in enumerators]
