# System requirements


--8<-- "Kubernetes-Operator-for-PS-RN{{release}}.md:software"


## Supported platforms

Percona Operators are designed for compatibility with all [CNCF-certified :octicons-link-external-16:](https://www.cncf.io/training/certification/software-conformance/) Kubernetes distributions. Our release process includes targeted testing and validation on major cloud provider platforms and OpenShift, as detailed below for Operator version {{ release }}:

--8<-- "Kubernetes-Operator-for-PS-RN{{release}}.md:platforms"

Other Kubernetes platforms may also work but have not been tested.

## Resource limits

A cluster running an officially supported platform contains at least three
Nodes, with the following resources:

* 2GB of RAM,
* 2 CPU threads per Node for Pods provisioning,
* at least 60GB of available storage for Persistent Volumes provisioning.
