from k8s_enum.enumerators.base_enum import BaseEnum
from dataclasses import dataclass, field
from typing import Any

@dataclass
class Role:
    name: str
    namespace: str
    rules: list[str] = field(default_factory=lambda: [])


class Enumerator(BaseEnum):
    def __init__(self, enum_client) -> None:
        super().__init__(enum_client, "Roles")

    def enumerate(self, enum_client) -> list[Role]:
        roles = enum_client.v1_rbac.list_role_for_all_namespaces()

        enumerated_roles = []

        for role in roles.items:
            enumerated_roles.append(
                Role(
                    role.metadata.name,
                    namespace=role.metadata.namespace,
                    rules=role.rules,
                )
            )

        return enumerated_roles

    def create_rows(self) -> list[list[Any]]:
        rows = []
        headers = ["Name", "Namespace", "Rules"]
        for role in self.items:
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
