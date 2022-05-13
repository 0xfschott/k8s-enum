from tabulate import tabulate
from abc import ABC, abstractmethod
from termcolor import colored
from typing import Any


class BaseEnum(ABC):
    def __init__(self, enum_client, header: str):
        self.items = self.enumerate(enum_client)
        self.header = header

    @abstractmethod
    def enumerate(self,  enum_client):
        pass

    @abstractmethod
    def create_rows(self) -> list[list[Any]]:
        pass

    def to_table(self):
        rows = self.create_rows()
        print("\n")
        print(colored(f"[+] {self.header} [+]", "green"))
        if len(rows) > 0:
            for row in rows:
                headers = [colored(header, attrs=["bold"]) for header in row[1]]
                print(tabulate(row[0], headers=headers, tablefmt=row[2]))

    def create_output(self, namespace_filter=None, role_filter=None):
        if namespace_filter:
            self.filter_by_namespace(namespace_filter)
        if role_filter:
            self.filter_by_role_prefix(role_filter)
        self.to_table()

    def filter_by_namespace(self, namespace_filter):
        self.items = [
            res
            for res in self.items
            if not_contains_namespace(res, namespace_filter)
        ]

    def filter_by_role_prefix(self, role_filter):
        self.items = [
            res for res in self.items if not_contains_string(res, role_filter)
        ]


def not_contains_string(res, role_filter):
    if hasattr(res, "name"):
        for role in role_filter:
            if res.name.startswith(role):
                return False
    else:
        return False
    return True


def not_contains_namespace(res, namespace_filter):
    if hasattr(res, "namespace"):
        if res.namespace not in namespace_filter:
            return True
    else:
        return True
    return False
