from k8s_enum.enumerators.base_enum import BaseEnum, filter_by_namespace


class User:
    def __init__(self, name, attached_roles=[], attached_cluster_roles=[]) -> None:
        self.name = name
        self.attached_roles = attached_roles[:]
        self.attached_cluster_roles = attached_cluster_roles[:]


class UserEnumerator(BaseEnum):
    def __init__(self, enum_client):
        super().__init__(enum_client)
        self.header = "Users"

    def enumerate(self, enum_client):
        role_bindings = enum_client.v1_rbac.list_role_binding_for_all_namespaces()
        cluster_role_bindings = enum_client.v1_rbac.list_cluster_role_binding()

        enumerated_users = []

        for rb in role_bindings.items:
            for subject in rb.subjects:
                if subject.kind == "User":
                    if len(enumerated_users) == 0:
                        enumerated_users.append(
                            User(subject.name, attached_roles=[rb.role_ref.name])
                        )
                    for user in enumerated_users:
                        if user.name == subject.name:
                            if rb.role_ref.name not in user.attached_roles:
                                user.attached_roles.append(rb.role_ref.name)
                        elif not any(u.name == subject.name for u in enumerated_users):
                            enumerated_users.append(
                                User(subject.name, attached_roles=[rb.role_ref.name])
                            )

        for cb in cluster_role_bindings.items:
            if cb.subjects:
                for subject in cb.subjects:
                    if subject.kind == "User":
                        for user in enumerated_users:
                            if user.name == subject.name:
                                if cb.role_ref.name not in user.attached_cluster_roles:
                                    user.attached_cluster_roles.append(cb.role_ref.name)
        return enumerated_users

    def create_rows(self):
        rows = []
        headers = ["User", "Attached Roles", "Attached Cluster Roles"]
        for user in self.items:
            attached_roles = user.attached_roles
            attached_roles_str = "".join(
                "- " + str(role) + "\n" for role in attached_roles
            )
            attached_cluster_roles = user.attached_cluster_roles
            attached_cluster_roles_str = "".join(
                "- " + str(role) + "\n" for role in attached_cluster_roles
            )
            rows.append([user.name, attached_roles_str, attached_cluster_roles_str])
        return [[rows, headers, "grid"]]


def enumerate(enum_client, namespace_filters=[str]):
    enumerator = UserEnumerator(enum_client)
    filter_by_namespace(enumerator.items, namespace_filters)
    enumerator.to_table()
