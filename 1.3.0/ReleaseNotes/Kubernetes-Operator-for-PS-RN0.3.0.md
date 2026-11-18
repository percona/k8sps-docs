> For the complete documentation index, see [llms.txt](https://docs.percona.com/percona-operator-for-mysql/1.3.0/llms.txt).

# *Percona Operator for MySQL* 0.3.0

- **Date**

  September 30, 2022

- **Installation**

  [Installing Percona Operator for MySQL](https://docs.percona.com/percona-operator-for-mysql/1.3.0/System-Requirements.html#installation-guidelines)

Note

Version 0.3.0 of the Percona Operator for MySQL is **a tech preview release** and it is **not recommended for production environments**. **As of today, we recommend using** [Percona Operator for MySQL based on Percona XtraDB Cluster](https://docs.percona.com/percona-operator-for-mysql/pxc/index.html), which is production-ready and contains everything you need to quickly and consistently deploy and scale MySQL clusters in a Kubernetes-based environment, on-premises or in the cloud.

## Release Highlights

- You can now use the [HAProxy load balancer](https://docs.percona.com/percona-operator-for-mysql/1.3.0/expose.html#use-haproxy) in front of the cluster configured for the asynchronous replication. The feature is turned on by default, allowing HAProxy to route traffic and monitor the health of the nodes
- Starting from this release, the Operator [automatically generates](https://docs.percona.com/percona-operator-for-mysql/1.3.0/tls-cert-manager.html) TLS certificates and turns on transport encryption by default at cluster creation time. This includes both external certificates which allow users to connect to a cluster via the encrypted channel, and internal ones used for communication between MySQL nodes

## New Features

- [K8SPS-17](https://jira.percona.com/browse/K8SPS-17) The new sidecar container for MySQL Pods integrates the Percona Toolkit’s pt-heartbeat tool, which provides reliable monitoring of the MySQL replication lag and allows Orchestrator to block primary promotion of the extra slow instances (ones with the lag greater than 10 minutes)
- [K8SPS-105](https://jira.percona.com/browse/K8SPS-105) Provide the backup and restore functionality for clusters with Group Replication
- [K8SPS-112](https://jira.percona.com/browse/K8SPS-112) Use HAProxy to simplify the exposure and enable load balancing for the asynchronous MySQL cluster

## Improvements

- [K8SPS-23](https://jira.percona.com/browse/K8SPS-23) Add [cert-manager support](https://docs.percona.com/percona-operator-for-mysql/1.3.0/tls-cert-manager.html) to generate and update TLS certificates automatically
- [K8SPS-31](https://jira.percona.com/browse/K8SPS-31) Show `ready` state in the custom resource output produced by the `kubectl get ps` command only after all LoadBalancers are ready
- [K8SPS-59](https://jira.percona.com/browse/K8SPS-59) Add `mysql.primaryServiceType` Custom Resource option to configure the primary exposure type in one place instead of exposing all Pods with specific Service type
- [K8SPS-88](https://jira.percona.com/browse/K8SPS-88) Allow configuring `prefix` field for backup storages via the [backup.s3.prefix](https://docs.percona.com/percona-operator-for-mysql/1.3.0/operator.html#backupstoragesstorage-names3prefix) Custom Resource option
- [K8SPS-93](https://jira.percona.com/browse/K8SPS-93) Avoid running multiple backups on the same Pod by either scheduling new backup to another Node or blocking it until the running one finishes
- [K8SPS-97](https://jira.percona.com/browse/K8SPS-97) [S3 backup finalizer](https://docs.percona.com/percona-operator-for-mysql/1.3.0/backups-ondemand.html) now triggers the actual deletion of backup files from the S3 bucket when there is a manual or scheduled removal of the corresponding backup object
- [K8SPS-103](https://jira.percona.com/browse/K8SPS-103) Show MySQL Router and Orchestrator statuses in the Custom Resource through the `kubectl` command
- [K8SPS-104](https://jira.percona.com/browse/K8SPS-104) Avoid using the root user in backup containers to run XtraBackup with the lowest possible privileges for higher security and isolation of the cluster components
- [K8SPS-115](https://jira.percona.com/browse/K8SPS-115) Make it possible [to use API Key](https://docs.percona.com/percona-operator-for-mysql/1.3.0/monitoring.html#install-pmm-client) to authorize within Percona Monitoring and Management Server as a more convenient and modern alternative password-based authentication
- [K8SPS-119](https://jira.percona.com/browse/K8SPS-119) and [K8SPS-150](https://jira.percona.com/browse/K8SPS-150) Allow to specify custom init images for the cluster components (MySQL, Orchestrator, Router, HAProxy, etc.) to simplify customizing images by the end users
- [K8SPS-138](https://jira.percona.com/browse/K8SPS-138) Expose MySQL default and administrative connection ports via MySQL Router
- [K8SPS-145](https://jira.percona.com/browse/K8SPS-145) Add `delete-mysql-pods-in-order` finalizer to control the proper Pods deletion order in case of the cluster deletion event
- [K8SPS-152](https://jira.percona.com/browse/K8SPS-152) Allow configuring the Orchestrator exposure via the [orchestrator.expose.type](https://docs.percona.com/percona-operator-for-mysql/1.3.0/operator.html#orchestratorexposetype) option in Custom Resource

## Bugs Fixed

- [K8SPS-91](https://jira.percona.com/browse/K8SPS-91) Fix a bug that caused backups to run even if user disabled them
- [K8SPS-92](https://jira.percona.com/browse/K8SPS-92) Fixed a bug where backup did not throw error in logs in case of incorrect S3 credentials, making the impression that everything is working fine
- [K8SPS-114](https://jira.percona.com/browse/K8SPS-114) Fix a bug due to which setting `primaryServiceType` to `LoadBalancer` with asynchronous replication resulted in no STATE and ENDPOINT in the custom resource output produced by the `kubectl get ps` command
- [K8SPS-121](https://jira.percona.com/browse/K8SPS-121) Fix a bug where XtraBackup process erroneously continued running on the appropriate Node instead of being killed on backup Pod termination, e.g. with `kubectl delete ps-backup` command
- [K8SPS-125](https://jira.percona.com/browse/K8SPS-125) Fix a bug where the Operator was erroneously removing cluster Secret in case of the Custom Resource deletion, causing change of all passwords if user creates the new one
- [K8SPS-132](https://jira.percona.com/browse/K8SPS-132) Fix a bug which made MySQL client quickly reaching connections limit on EKS due to the large number of connection attempts done by the AWS healthchecks that could not access MySQL Router

## Deprecation and removal

- [K8SPS-49](https://jira.percona.com/browse/K8SPS-49) The `clustercheck` system user was removed and is no longer automatically created by default; starting from now, the `monitor` user is used for probes-related functionality

## Supported Platforms

The following platforms were tested and are officially supported by the Operator 0.3.0:

- [Google Kubernetes Engine (GKE)](https://cloud.google.com/kubernetes-engine) 1.22 - 1.25
- [Amazon Elastic Container Service for Kubernetes (EKS)](https://aws.amazon.com) 1.20 - 1.23
- [Minikube](https://minikube.sigs.k8s.io/docs/) 1.27 (based on Kubernetes 1.25)

This list only includes the platforms that the Percona Operators are specifically tested on as part of the release process. Other Kubernetes flavors and versions depend on backward compatibility offered by Kubernetes itself.
