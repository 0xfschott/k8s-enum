import base64
from k8s_enum.enumerators.base_enum import BaseEnum, filter_by_namespace
from dataclasses import dataclass


@dataclass
class Secret:
    name: str
    namespace: str
    data: dict


class SecretEnumerator(BaseEnum):
    def __init__(self, enum_client):
        super().__init__(enum_client, "Secrets")

    def enumerate(self, enum_client):
        secrets = enum_client.v1_core.list_secret_for_all_namespaces()
        enumerated_secrets = []
        for secret in secrets.items:
            enumerated_secrets.append(
                Secret(
                    secret.metadata.name,
                    namespace=secret.metadata.namespace,
                    data=secret.data,
                )
            )
        return enumerated_secrets

    def create_rows(self):
        rows = []
        for secret in self.items:
            headers = ["Secret", "Namespace", "Data (Limited output)"]
            if secret.data:
                data_str = "".join(
                    "- "
                    + key
                    + ": "
                    + base64.b64decode(secret.data[key]).decode(
                        "utf-8", errors="ignore"
                    )[:25]
                    + "\n"
                    for key in secret.data
                )
            rows.append([secret.name, secret.namespace, data_str])
        return [[rows, headers, "grid"]]


def enumerate(enum_client, namespace_filter=None, role_filter=None):
    enumerator = SecretEnumerator(enum_client)
    filter_by_namespace(enumerator.items, namespace_filter)
    enumerator.to_table()
