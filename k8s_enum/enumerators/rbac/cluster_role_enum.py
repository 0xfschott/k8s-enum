from k8s_enum.enumerators.base_enum import BaseEnum, filter_by_role_prefix


class ClusterRole:
    def __init__(self, name, *, rules=[]) -> None:
        self.name = name
        self.rules = rules[:]


class ClusterRoleEnumerator(BaseEnum):
    def __init__(self, v1_rbac):
        self.cluster_roles = self.enumerate(v1_rbac)
        self.header = "Cluster Roles"

    def enumerate(self, v1_rbac):
        cluster_roles = v1_rbac.list_cluster_role()

        enumerated_cluster_roles = []

        for role in cluster_roles.items:
            enumerated_cluster_roles.append(
                ClusterRole(role.metadata.name, rules=role.rules)
            )

        return enumerated_cluster_roles

    def create_rows(self):
        rows = []
        headers = ["Name", "Rules"]
        for role in self.cluster_roles:
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
    enumerator = ClusterRoleEnumerator(enum_client.v1_rbac)
    filter_by_role_prefix(enumerator.cluster_roles, role_filter)
    enumerator.to_table()
