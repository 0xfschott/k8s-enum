from k8s_enum.enumerators.base_enum import BaseEnum
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Group:
    name: str
    attached_roles: list[str] = field(default_factory=lambda: [])
    attached_cluster_roles: list[str] = field(default_factory=lambda: [])


class Enumerator(BaseEnum):
    def __init__(self, enum_client) -> None:
        super().__init__(enum_client, "Groups")

    def enumerate(self, enum_client) -> list[Group]:
        role_bindings = enum_client.v1_rbac.list_role_binding_for_all_namespaces()
        cluster_role_bindings = enum_client.v1_rbac.list_cluster_role_binding()

        enumerated_groups: list[Group] = []

        for rb in role_bindings.items:
            for subject in rb.subjects:
                if subject.kind == "Group":
                    if len(enumerated_groups) == 0:
                        enumerated_groups.append(
                            Group(subject.name, attached_roles=[rb.role_ref.name])
                        )
                    for group in enumerated_groups:
                        if group.name == subject.name:
                            if rb.role_ref.name not in group.attached_roles:
                                group.attached_roles.append(rb.role_ref.name)
                        elif not any(g.name == subject.name for g in enumerated_groups):
                            enumerated_groups.append(
                                Group(subject.name, attached_roles=[rb.role_ref.name])
                            )

        for cb in cluster_role_bindings.items:
            if cb.subjects:
                for subject in cb.subjects:
                    if subject.kind == "Group":
                        for group in enumerated_groups:
                            if group.name == subject.name:
                                if cb.role_ref.name not in group.attached_cluster_roles:
                                    group.attached_cluster_roles.append(
                                        cb.role_ref.name
                                    )

        return enumerated_groups

    def create_rows(self) -> list[list[Any]]:
        rows = []
        headers = ["Group", "Attached Roles", "Attached Cluster Roles"]
        for group in self.items:
            attached_roles = group.attached_roles
            attached_roles_str = "".join(
                "- " + str(role) + "\n" for role in attached_roles
            )
            attached_cluster_roles = group.attached_cluster_roles
            attached_cluster_roles_str = "".join(
                "- " + str(role) + "\n" for role in attached_cluster_roles
            )
            rows.append([group.name, attached_roles_str, attached_cluster_roles_str])
        return [[rows, headers, "grid"]]
