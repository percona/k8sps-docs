# System requirements

The Operator supports Percona Server for MySQL (PS) 8.0.

The Operator was developed and tested with Percona Server for MySQL 8.0.36-28.
Other options may also work but have not been tested. Other software components include:

* Orchestrator 3.2.6-12
* MySQL Router 8.0.36
* XtraBackup 8.0.35-31
* Percona Toolkit 3.6.0
* HAProxy 2.8.5
* PMM Client 2.42.0

## Supported platforms

The following platforms were tested and are officially supported by the Operator
{{ release }}:

* [Google Kubernetes Engine (GKE) :octicons-link-external-16:](https://cloud.google.com/kubernetes-engine) 1.27 - 1.29
* [Amazon Elastic Container Service for Kubernetes (EKS) :octicons-link-external-16:](https://aws.amazon.com) 1.27 - 1.30
* [Minikube :octicons-link-external-16:](https://minikube.sigs.k8s.io/docs/) 1.33.1 (based on Kubernetes 1.30.0)

Other Kubernetes platforms may also work but have not been tested.

## Resource limits

A cluster running an officially supported platform contains at least three
Nodes, with the following resources:

* 2GB of RAM,
* 2 CPU threads per Node for Pods provisioning,
* at least 60GB of available storage for Persistent Volumes provisioning.

## Installation guidelines

Choose how you wish to install the Operator:

* [with Helm](helm.md)
* [on Minikube](minikube.md)
* [on Google Kubernetes Engine (GKE)](gke.md)
* [on Amazon Elastic Kubernetes Service (AWS EKS)](eks.md)
* [in a Kubernetes-based environment](kubernetes.md)
