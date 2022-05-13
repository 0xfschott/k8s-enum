from k8s_enum.enumerators.base_enum import BaseEnum, filter_by_role_prefix
from dataclasses import dataclass, field


@dataclass
class ClusterRole:
    name: str
    rules: list[str] = field(default_factory=lambda: [])


class ClusterRoleEnumerator(BaseEnum):
    def __init__(self, enum_client):
        super().__init__(enum_client, "Cluster Roles")

    def enumerate(self, enum_client):
        cluster_roles = enum_client.v1_rbac.list_cluster_role()

        enumerated_cluster_roles = []

        for role in cluster_roles.items:
            enumerated_cluster_roles.append(
                ClusterRole(role.metadata.name, rules=role.rules)
            )

        return enumerated_cluster_roles

    def create_rows(self):
        rows = []
        headers = ["Name", "Rules"]
        for role in self.items:
            rules = role.rules
            rules_str = ""
            for rule in rules:
                rule.resource_names = (
                    [None] if rule.resource_names == None else rule.resource_names
                )
                rule.resources = [None] if rule.resources == None else rule.resources
                permutations = [
                    (x, y, z)
                    for x in rule.resource_names
                    for y in rule.resources
                    for z in rule.verbs
                ]
                for p in permutations:
                    res_name = p[0] + ":" if p[0] != None else ""
                    rules_str += "- " + str(p[2]) + " " + res_name + str(p[1]) + "\n"
            rows.append([role.name, rules_str])
        return [[rows, headers, "grid"]]


def enumerate(enum_client, namespace_filter=None, role_filter=None):
    enumerator = ClusterRoleEnumerator(enum_client)
    filter_by_role_prefix(enumerator.items, role_filter)
    enumerator.to_table()
