from k8s_enum.enumerators.base_enum import BaseEnum, filter_by_namespace


class Namespace:
    def __init__(self, name: str):
        self.name = name


class NamespaceEnumerator(BaseEnum):
    def __init__(self, v1_core):
        self.namespaces = self.enumerate(v1_core)
        self.header = "Namespaces"

    def enumerate(self, v1_core):
        namespaces = v1_core.list_namespace()
        enumerated_namespaces = []
        enumerated_namespaces = [Namespace(ns.metadata.name) for ns in namespaces.items]
        return enumerated_namespaces

    def create_rows(self):
        rows = []
        headers = ["Namespaces"]
        for ns in self.namespaces:
            rows.append([ns.name])
        return [[rows, headers, "grid"]]


def enumerate(enum_client, namespace_filters=[]):
    enumerator = NamespaceEnumerator(enum_client.v1_core)
    enumerator.to_table()
