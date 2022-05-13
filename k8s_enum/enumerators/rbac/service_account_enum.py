from k8s_enum.enumerators.base_enum import BaseEnum, filter_by_namespace
from dataclasses import dataclass, field


@dataclass
class ServiceAccount:
    name: str
    namespace: str
    attached_roles: list[str] = field(default_factory=lambda: [])
    attached_cluster_roles: list[str] = field(default_factory=lambda: [])


class ServiceAccountEnumerator(BaseEnum):
    def __init__(self, enum_client):
        super().__init__(enum_client, "Service Accounts")

    def enumerate(self, enum_client):
        service_accounts = enum_client.v1_core.list_service_account_for_all_namespaces()
        role_bindings = enum_client.v1_rbac.list_role_binding_for_all_namespaces()
        cluster_role_bindings = enum_client.v1_rbac.list_cluster_role_binding()

        enumerated_service_accounts = []

        for sa in service_accounts.items:
            enumerated_service_accounts.append(
                ServiceAccount(sa.metadata.name, namespace=sa.metadata.namespace)
            )

        for rb in role_bindings.items:
            for subject in rb.subjects:
                if subject.kind == "ServiceAccount":
                    for sa in enumerated_service_accounts:
                        if (
                            sa.name == subject.name
                            and sa.namespace == subject.namespace
                        ):
                            if rb.role_ref.name not in sa.attached_roles:
                                sa.attached_roles.append(rb.role_ref.name)

        for cb in cluster_role_bindings.items:
            if cb.subjects:
                for subject in cb.subjects:
                    if subject.kind == "ServiceAccount":
                        for sa in enumerated_service_accounts:
                            if (
                                sa.name == subject.name
                                and sa.namespace == subject.namespace
                            ):
                                if cb.role_ref.name not in sa.attached_cluster_roles:
                                    sa.attached_cluster_roles.append(cb.role_ref.name)

        return enumerated_service_accounts

    def create_rows(self):
        rows = []
        headers = [
            "Service Account",
            "Namespace",
            "Attached Roles",
            "Attached Cluster Roles",
        ]
        for sa in self.items:
            attached_roles = sa.attached_roles
            attached_roles_str = "".join(
                "- " + str(role) + "\n" for role in attached_roles
            )
            attached_cluster_roles = sa.attached_cluster_roles
            attached_cluster_roles_str = "".join(
                "- " + str(role) + "\n" for role in attached_cluster_roles
            )
            rows.append(
                [sa.name, sa.namespace, attached_roles_str, attached_cluster_roles_str]
            )
        return [[rows, headers, "grid"]]


def enumerate(enum_client, namespace_filter=None, role_filter=None):
    enumerator = ServiceAccountEnumerator(enum_client)
    filter_by_namespace(enumerator.items, namespace_filter)
    enumerator.to_table()
