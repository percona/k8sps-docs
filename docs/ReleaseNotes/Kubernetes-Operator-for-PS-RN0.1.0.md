# *Percona Distribution for MySQL Operator based on Percona Server for MySQL* 0.1.0

Kubernetes provides users with a distributed orchestration system that automates
the deployment, management, and scaling of containerized applications. The
Operator extends the Kubernetes API with a new custom resource for deploying,
configuring, and managing the application through the whole life cycle.
You can compare the Kubernetes Operator to a System Administrator who deploys
the application and watches the Kubernetes events related to it, taking
administrative/operational actions when needed.

The already existing [Percona Distribution for MySQL Operator](https://www.percona.com/doc/kubernetes-operator-for-pxc/index.html) is based on Percona XtraDB Cluster. It is feature rich and provides virtually-synchronous replication by utilizing Galera Write-Sets. Sync replication ensures data consistency and proved itself useful for critical applications, especially on Kubernetes.

The new *Percona Distribution for MySQL Operator* is going to run Percona Server for MySQL and provide both regular asynchronous (with [semi-sync :octicons-link-external-16:](https://dev.mysql.com/doc/refman/8.0/en/replication-semisync.html) support) and virtually-synchronous replication based on [Group Replication :octicons-link-external-16:](https://dev.mysql.com/doc/refman/8.0/en/group-replication.html).

**Version 0.1.0 of the Percona Distribution for MySQL Operator based on Percona Server for MySQL is a tech preview release and it is not recommended for production environments.**

You can install *Percona Distribution for MySQL Operator* on Kubernetes,
[Google Kubernetes Engine (GKE) :octicons-link-external-16:](https://cloud.google.com/kubernetes-engine),
[Amazon Elastic Container Service for Kubernetes (EKS) :octicons-link-external-16:](https://aws.amazon.com/eks/),
and [Minikube :octicons-link-external-16:](https://minikube.sigs.k8s.io/docs/).

The features available in this release are the following:


* Deploy asynchronous and semi-sync replication MySQL clusters with Orchestrator on top of it,


* Expose the cluster with regular Kubernetes Services,


* Monitor the cluster with Percona Monitoring and Management,


* Customize MySQL configuration,


* Rotate system user passwords,


* Customize MySQL Pods with sidecar containers.

## Installation

Installation is performed by following the documentation installation instructions for [Kubernetes](../kubernetes.md#install-kubernetes), [Amazon Elastic Kubernetes Service](../eks.md#install-eks) and [Minikube](../minikube.md#install-minikube).
