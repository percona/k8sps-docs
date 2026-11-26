> For the complete documentation index, see [llms.txt](https://docs.percona.com/percona-operator-for-mysql/1.3.0/llms.txt).

# System requirements

The Operator was developed and tested with the following software:

- Percona Server for MySQL 9.7.2-2.1
- Percona Server for MySQL 8.4.11-11.1
- Percona Server for MySQL 8.0.46-37.1
- XtraBackup 9.7.1-rc1.1
- XtraBackup 8.4.0-7.1
- XtraBackup 8.0.35-36.1
- MySQL Router 9.7.2
- MySQL Router 8.4.11
- MySQL Router 8.0.46
- HAProxy 2.8.29-1
- Orchestrator 3.2.6-24
- Percona Toolkit 3.7.2-1
- Log collector (Fluent Bit) 5.1.4-1
- PMM Client 3.10.0
- Cert Manager 1.21.2
- Percona Binlog Server 0.4.1

Other options may also work but have not been tested.

## Supported platforms

Percona Operators are designed for compatibility with all [CNCF-certified](https://www.cncf.io/training/certification/software-conformance/) Kubernetes distributions. Our release process includes targeted testing and validation on major cloud provider platforms and OpenShift, as detailed below for Operator version 1.3.0:

- [Google Kubernetes Engine (GKE)](https://cloud.google.com/kubernetes-engine) 1.34 - 1.36
- [Amazon Elastic Kubernetes Service (EKS)](https://aws.amazon.com/eks/) 1.34 - 1.37
- [DigitalOcean Kubernetes Service (DOKS)](https://docs.digitalocean.com/products/kubernetes/) 1.37
- [OpenShift](https://www.openshift.com) 4.19 - 4.22
- [Minikube](https://minikube.sigs.k8s.io/docs/) 1.39.0 with Kubernetes v1.37.0

Other Kubernetes platforms may also work but have not been tested.

## Resource limits

A cluster running an officially supported platform contains at least three Nodes, with the following resources:

- 2GB of RAM,
- 2 CPU threads per Node for Pods provisioning,
- at least 60GB of available storage for Persistent Volumes provisioning.

## Installation guidelines

Choose how you wish to install the Operator:

- [with Helm](https://docs.percona.com/percona-operator-for-mysql/1.3.0/helm.md)
- [on Minikube](https://docs.percona.com/percona-operator-for-mysql/1.3.0/minikube.md)
- [on Google Kubernetes Engine (GKE)](https://docs.percona.com/percona-operator-for-mysql/1.3.0/gke.md)
- [on Amazon Elastic Kubernetes Service (AWS EKS)](https://docs.percona.com/percona-operator-for-mysql/1.3.0/eks.md)
- [on DigitalOcean Kubernetes (DOKS)](https://docs.percona.com/percona-operator-for-mysql/1.3.0/doks.md)
- [in a Kubernetes-based environment](https://docs.percona.com/percona-operator-for-mysql/1.3.0/kubernetes.md)
