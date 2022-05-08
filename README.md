# k8sEnum
The kubernetes enumerator **k8sEnum** can help to get a quick overview of resources deployed to a Kubernetes cluster and to identify insecure configurations, high privileged service accounts, etc.

![Example output](docs/images/example_output_1.png "Example Output")

## Installation

## Usage
### Enumerate all
```
k8sEnum all
```

### Enumerate specific resources (e.g. only Pods)
```
k8sEnum pods
```

### Filter results (e.g by namespace)
```
k8sEnum --exclude-namespaces default --exclude-namespaces kube-system all
```


