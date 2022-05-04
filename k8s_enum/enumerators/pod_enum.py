from typing import List
from k8s_enum.enumerators.base_enum import BaseEnum, filter_by_namespace
from k8s_enum.enumerators.rbac.service_account_enum import (
    ServiceAccountEnumerator,
    ServiceAccount,
)
from termcolor import colored
from dataclasses import dataclass
from k8s_enum.enumerators.utils import colored_if_true


@dataclass
class ContainerSecurityContext:
    privileged: bool
    allowPrivilegeEscalation: bool
    capabilities: list[str]
    readOnlyRootFileSystem: bool
    runAsGroup: int
    runAsNonRoot: bool
    runAsUser: int


@dataclass
class PodSecurityContext:
    fs_group: int
    fs_group_change_policy: str
    read_only_root_file_system: bool
    run_as_group: int
    run_as_non_root: bool
    run_as_user: int

    def to_string(self):
        str = f"readOnlyRootFileSystem: {colored_if_true(self.read_only_root_file_system, self.read_only_root_file_system is False, 'yellow')} \n"
        str += f"runAsNonRoot: {colored_if_true(self.run_as_non_root, self.run_as_non_root is False, 'yellow')} \n"
        str += f"runAsUser: {colored_if_true(self.run_as_user, self.run_as_user == 0, 'yellow')} \n"
        str += f"runAsGroup: {colored_if_true(self.run_as_group, self.run_as_group == 0, 'yellow')}"


@dataclass
class PodHostFlags:
    host_ipc: bool
    host_network: bool
    host_pid: bool
    host_paths: list[str]

    def to_string(self):
        h_str = (
            f"Host IPC: {colored_if_true(self.host_ipc, self.host_ipc, 'yellow')} \n"
            if self.host_ipc
            else ""
        )
        h_str += (
            f"Host Network: {colored_if_true(self.host_network, self.host_network, 'yellow')} \n"
            if self.host_network
            else ""
        )
        h_str += (
            f"Host PID: {colored_if_true(self.host_pid, self.host_pid, 'yellow')} \n"
            if self.host_pid
            else ""
        )
        h_str += "Host Paths:\n" if self.host_paths else ""
        h_str += "".join(
            colored("  - " + str(path.path), "yellow") + "\n"
            for path in self.host_paths
        )
        return h_str


@dataclass
class Container:
    name: str
    image: str
    security: ContainerSecurityContext

    def to_string(self) -> str:
        container_str = f"- Name: {self.name}"
        container_str += f"  Image:{self.image}"
        container_str += ""
        container_str = "".join(
            "- " + str(container.image) + "\n" for container in pod.containers
        )
        return container_str


@dataclass
class Pod:
    name: str
    namespace: str
    ip_address: str
    hot_pod: bool
    pod_host_flags: PodHostFlags
    security_context: PodSecurityContext
    containers: list[Container]
    attached_service_accounts: list[ServiceAccount]


class PodEnumerator(BaseEnum):
    def __init__(self, enum_client, service_accounts=None):
        self.service_accounts = service_accounts
        if self.service_accounts == None:
            self.service_accounts = ServiceAccountEnumerator(
                enum_client
            ).service_accounts

        super().__init__(enum_client)
        self.header = "Pods"

    def enumerate(self, enum_client):
        pods = enum_client.v1_core.list_pod_for_all_namespaces()

        enumerated_pods = []
        for pod in pods.items:
            hot_pod = False
            attached_service_accounts = []
            for sa in self.service_accounts:
                if (
                    sa.name == pod.spec.service_account
                    and sa.namespace == pod.metadata.namespace
                ):
                    attached_service_accounts.append(sa)

            for asa in attached_service_accounts:
                if len(asa.attached_roles) > 0:
                    hot_pod = True
                    break

            host_paths = [
                volume.host_path
                for volume in pod.spec.volumes
                if volume.host_path != None
            ]

            enumerated_pods.append(
                Pod(
                    pod.metadata.name,
                    namespace=pod.metadata.namespace,
                    ip_address=pod.status.pod_ip,
                    hot_pod=hot_pod,
                    security_context=None,
                    pod_host_flags=PodHostFlags(
                        host_ipc=pod.spec.host_ipc,
                        host_network=pod.spec.host_network,
                        host_pid=pod.spec.host_pid,
                        host_paths=host_paths,
                    ),
                    containers=[
                        Container(c.name, c.image, None) for c in pod.spec.containers
                    ],
                    attached_service_accounts=attached_service_accounts,
                )
            )
        return enumerated_pods

    def create_rows(self):
        rows = []
        for pod in self.items:
            headers = [
                "Pod",
                "Namespace",
                "IP Address",
                "Service Accounts",
                "Hot Pod",
                "Host Flags",
                "Images",
            ]

            service_accounts_str = "".join(
                "- " + sa.namespace + ":" + sa.name + "\n"
                for sa in pod.attached_service_accounts
            )
            rows.append(
                [
                    pod.name,
                    pod.namespace,
                    pod.ip_address,
                    service_accounts_str,
                    colored_if_true(pod.hot_pod, pod.hot_pod, "yellow"),
                    pod.pod_host_flags.to_string(),
                    "",
                ]
            )
        return [[rows, headers, "grid"]]


def enumerate(enum_client, namespace_filters=[]):
    enumerator = PodEnumerator(enum_client)
    filter_by_namespace(enumerator.items, namespace_filters)
    enumerator.to_table()
