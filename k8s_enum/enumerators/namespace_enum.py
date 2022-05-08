from k8s_enum.enumerators.base_enum import BaseEnum, filter_by_namespace


class Namespace:
    def __init__(self, namespace: str):
        self.namespace = namespace


class NamespaceEnumerator(BaseEnum):
    def __init__(self, enum_client):
        self.items = self.enumerate(enum_client)
        self.header = "Namespaces"

    def enumerate(self, enum_client):
        namespaces = enum_client.v1_core.list_namespace()
        enumerated_namespaces = []
        enumerated_namespaces = [Namespace(ns.metadata.name) for ns in namespaces.items]
        return enumerated_namespaces

    def create_rows(self):
        rows = []
        headers = ["Namespaces"]
        for ns in self.items:
            rows.append([ns.namespace])
        return [[rows, headers, "grid"]]


def enumerate(enum_client, namespace_filters=[]):
    enumerator = NamespaceEnumerator(enum_client)
    filter_by_namespace(enumerator.items, namespace_filters)
    enumerator.to_table()
