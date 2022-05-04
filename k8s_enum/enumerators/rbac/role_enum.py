from k8s_enum.enumerators.base_enum import BaseEnum
from k8s_enum.enumerators import SYSTEM_NAMESPACES


class Role:
    def __init__(self, name, *, namespace, rules=[]) -> None:
        self.name = name
        self.namespace = namespace
        self.rules = rules[:]


class RoleEnumerator(BaseEnum):
    def __init__(self, v1_rbac, filter_system_namespaces=False):
        self.roles = self.enumerate(v1_rbac, filter_system_namespaces)
        self.header = "Roles"

    def enumerate(self, v1_rbac, filter_system_namespaces):
        roles = v1_rbac.list_role_for_all_namespaces()

        enumerated_roles = []

        for role in roles.items:
            enumerated_roles.append(
                Role(
                    role.metadata.name,
                    namespace=role.metadata.namespace,
                    rules=role.rules,
                )
            )

        if filter_system_namespaces:
            enumerated_roles = [
                role
                for role in enumerated_roles
                if role.namespace not in SYSTEM_NAMESPACES
            ]
        return enumerated_roles

    def create_rows(self):
        rows = []
        headers = ["Name", "Namespace", "Rules"]
        for role in self.roles:
            rules = role.rules
            rules_str = ""
            for rule in rules:
                rule.resource_names = (
                    [None] if rule.resource_names == None else rule.resource_names
                )
                permutations = [
                    (x, y, z)
                    for x in rule.resource_names
                    for y in rule.resources
                    for z in rule.verbs
                ]
                for p in permutations:
                    res_name = p[0] + ":" if p[0] != None else ""
                    rules_str += "- " + p[2] + " " + res_name + p[1] + "\n"
            rows.append([role.name, role.namespace, rules_str])
        return [[rows, headers, "grid"]]


def enumerate(enum_client, namespace_filters=[]):
    enumerator = RoleEnumerator(enum_client.v1_rbac)
    enumerator.to_table()