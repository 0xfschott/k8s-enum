from k8s_enum.enumerators.base_enum import BaseEnum
from dataclasses import dataclass
from typing import Any


@dataclass
class Namespace:
    namespace: str


class Enumerator(BaseEnum):
    def __init__(self, enum_client) -> None:
        super().__init__(enum_client, "Namespaces")

    def enumerate(self, enum_client) -> list[Namespace]:
        namespaces = enum_client.v1_core.list_namespace()
        enumerated_namespaces = []
        enumerated_namespaces = [Namespace(ns.metadata.name) for ns in namespaces.items]
        return enumerated_namespaces

    def create_rows(self) -> list[list[Any]]:
        rows = []
        headers = ["Namespaces"]
        for ns in self.items:
            rows.append([ns.namespace])
        return [[rows, headers, "grid"]]
