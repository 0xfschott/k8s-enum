CNI_PLUGINS = ["calico", "flannel", "cilium", "weave", "canal"]


def find_cni_plugin(v1_core):
    pods = v1_core.list_pod_for_all_namespaces()
    for pod in pods.items:
        try:
            pod_prefix = pod.metadata.name.split("-")[0]
            if pod_prefix.lower() in CNI_PLUGINS:
                return pod_prefix.lower()
        except:
            pass
    return "kubenet"
