from k8s_enum.enumerators.base_enum import BaseEnum
from k8s_enum.enumerators.helpers.cni_plugin import find_cni_plugin
from dataclasses import dataclass
from typing import Any


@dataclass
class Node:
    name: str
    operating_system: str
    operating_system_image: str
    architecture: str
    kernel_version: str
    kubelet_version: str
    container_runtime: str
    addresses: list[tuple[str, str]]
    pod_cidr: str
    cni: str


class Enumerator(BaseEnum):
    def __init__(self, enum_client) -> None:
        super().__init__(enum_client, "Master/Worker-Nodes")

    def enumerate(self, enum_client) -> list[Node]:
        cni_plugin = find_cni_plugin(enum_client.v1_core)
        if cni_plugin != "kubenet":
            pod_cidrs = enumerate_cni_cidrs(enum_client.v1_core, cni_plugin)

        nodes = enum_client.v1_core.list_node()
        enumerated_nodes = []
        for node in nodes.items:
            addresses = [
                (address.type, address.address) for address in node.status.addresses
            ]
            # TODO: respect different CNIs
            if cni_plugin == "kubenet":
                pod_cidr = node.spec.pod_cidr
            else:
                pod_cidr = pod_cidrs[node.metadata.name]

            enumerated_nodes.append(
                Node(
                    node.metadata.name,
                    operating_system=node.status.node_info.operating_system,
                    operating_system_image=node.status.node_info.os_image,
                    architecture=node.status.node_info.architecture,
                    kernel_version=node.status.node_info.kernel_version,
                    kubelet_version=node.status.node_info.kubelet_version,
                    container_runtime=node.status.node_info.container_runtime_version,
                    addresses=addresses,
                    pod_cidr=pod_cidr,
                    cni=cni_plugin,
                )
            )
        return enumerated_nodes

    def create_rows(self) -> list[list[Any]]:
        nodes = []
        for node in self.items:
            rows = []
            headers = [node.name, ""]
            for address in node.addresses:
                rows.append([address[0], address[1]])
            rows.append(
                [
                    "Operating System",
                    f"{node.operating_system} - {node.operating_system_image}",
                ]
            )
            rows.append(["Architecture", node.architecture])
            rows.append(["Kernel version", node.kernel_version])
            rows.append(["Kubelet version", node.kubelet_version])
            rows.append(["Container Runtime", node.container_runtime])
            rows.append(["Pod CIDR", node.pod_cidr])
            rows.append(["CNI", node.cni])
            nodes.append([rows, headers, "fancy_grid"])
        return nodes


def enumerate_cni_cidrs(v1_core, cni_plugin):
    pod_cidrs = {}
    if cni_plugin == "calico":
        calico_ip_info = eval(
            v1_core.api_client.call_api(
                "/apis/crd.projectcalico.org/v1/ipamblocks", "GET", response_type="str"
            )[0]
        )
        for ip in calico_ip_info["items"]:
            pod_cidrs[ip["spec"]["affinity"].split(":")[1]] = ip["spec"]["cidr"]
    return pod_cidrs
