from tabulate import tabulate
from abc import ABC, abstractmethod
from termcolor import colored


class BaseEnum(ABC):
    def __init__(self, enum_client):
        self.items = self.enumerate(enum_client)

    @abstractmethod
    def enumerate(self):
        pass

    @abstractmethod
    def create_rows(self):
        pass

    def to_table(self):
        rows = self.create_rows()
        print("\n")
        print(colored(f"[+] {self.header} [+]", "green"))
        if len(rows) > 0:
            for row in rows:
                headers = [colored(header, attrs=["bold"]) for header in row[1]]
                print(tabulate(row[0], headers=headers, tablefmt=row[2]))


def filter_by_namespace(enumerated_resources, namespace_filter):
    enumerated_resources[:] = [
        res
        for res in enumerated_resources
        if not_contains_namespace(res, namespace_filter)
    ]


def filter_by_role_prefix(enumerated_resources, role_filter):
    enumerated_resources[:] = [
        res
        for res in enumerated_resources
        if not_contains_string(res, role_filter)
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
