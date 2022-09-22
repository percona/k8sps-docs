# *Percona Operator for MySQL* 0.2.0


* **Date**

    June 30, 2022



* **Installation**

    [Installing Percona Operator for MySQL](https://www.percona.com/doc/kubernetes-operator-for-mysql/ps/index.html#advanced-installation-guides)


**NOTE**: Version 0.2.0 of the Percona Operator for MySQL is **a tech preview release** and it is **not recommended for production environments**. **As of today, we recommend using** [Percona Operator for MySQL based on Percona XtraDB Cluster](https://www.percona.com/doc/kubernetes-operator-for-pxc/index.html), which is production-ready and contains everything you need to quickly and consistently deploy and scale MySQL clusters in a Kubernetes-based environment, on-premises or in the cloud.

## Release Highlights


* With this release, the Operator turns to a simplified naming convention and
changes its official name to **Percona Operator for MySQL**


* This release brings initial [implementation of Group Replication](../operator.md#mysql-clustertype) between Percona Server for MySQL instances. Group Replication works in conjunction with MySQL Router, which is used instead of Orchestrator and also provides load balancing


* Now the Operator [is capable of making backups](../backups.md#backups). Backups are stored on the cloud outside the Kubernetes cluster: [Amazon S3, or S3-compatible storage](https://en.wikipedia.org/wiki/Amazon_S3#S3_API_and_competing_services) is supported, as well as [Azure Blob Storage](https://azure.microsoft.com/en-us/services/storage/blobs). Currently, backups work with asynchronous replication; support for backups with Group Replication is coming

## New Features


* [K8SPS-32](https://jira.percona.com/browse/K8SPS-32): Orchestrator is now highly available, allowing you to deploy a cluster without a single point of failure


* [K8SPS-53](https://jira.percona.com/browse/K8SPS-53) and [K8SPS-54](https://jira.percona.com/browse/K8SPS-54): You can now backup and restore your MySQL database with the Operator


* [K8SPS-55](https://jira.percona.com/browse/K8SPS-55) and [K8SPS-82](https://jira.percona.com/browse/K8SPS-82): Add Group Replication support and deploy MySQL Router proxy for load-balancing the traffic


* [K8SPS-56](https://jira.percona.com/browse/K8SPS-56): Automatically tune `buffer_pool_size` and `max_connections` options based on the resources provisioned for MySQL container if custom MySQL config is not provided

## Improvements


* [K8SPS-39](https://jira.percona.com/browse/K8SPS-39): Show endpoint in the Custom Resource status to quickly identify endpoint URI, or public IP address in case of the LoadBalancer


* [K8SPS-47](https://jira.percona.com/browse/K8SPS-47): Expose MySQL Administrative Connection Port and MySQL Server X Protocol in Services

## Bugs Fixed


* [K8SPS-58](https://jira.percona.com/browse/K8SPS-58): Fix a bug that caused cluster failure if MySQL initialization took longer than the startup probe delay


* [K8SPS-70](https://jira.percona.com/browse/K8SPS-70): Fix a bug that caused cluster crash if secretsName option was changed to another Secrets object with different passwords


* [K8SPS-78](https://jira.percona.com/browse/K8SPS-78): Make the Operator throw an error at cluster creation time if the storage is not specified

## Supported Platforms

The following platforms were tested and are officially supported by the Operator
0.2.0:


* [Google Kubernetes Engine (GKE)](https://cloud.google.com/kubernetes-engine) 1.21 - 1.23


* [Amazon Elastic Container Service for Kubernetes (EKS)](https://aws.amazon.com) 1.19 - 1.22


* [Minikube](https://minikube.sigs.k8s.io/docs/) 1.26 (based on Kubernetes 1.24)

This list only includes the platforms that the Percona Operators are specifically tested on as part of the release process. Other Kubernetes flavors and versions depend on backward compatibility offered by Kubernetes itself.
