# *Percona Operator for MySQL* 0.3.0

* **Date**

    September 30, 2022

* **Installation**

    [Installing Percona Operator for MySQL](../index.md#advanced-installation-guides)

!!! note

    Version 0.3.0 of the Percona Operator for MySQL is **a tech preview release** and it is **not recommended for production environments**. **As of today, we recommend using** [Percona Operator for MySQL based on Percona XtraDB Cluster](https://docs.percona.com/percona-operator-for-mysql/pxc/index.html), which is production-ready and contains everything you need to quickly and consistently deploy and scale MySQL clusters in a Kubernetes-based environment, on-premises or in the cloud.

## Release Highlights

* You can now use the [HAProxy load balancer](../expose.md#exposing-cluster-with-haproxy) in front of the cluster configured for the asynchronous replication. The feature is turned on by default, allowing HAProxy to route traffic and monitor the health of the nodes

* Starting from this release, the Operator [automatically generates](../TLS.md#install-and-use-the-cert-manager) TLS certificates and turns on transport encryption by default at cluster creation time. This includes both external certificates which allow users to connect to a cluster via the encrypted channel, and internal ones used for communication between MySQL nodes

## New Features

* {{ k8spsjira(17) }} The new sidecar container for MySQL Pods integrates the Percona Toolkit’s pt-heartbeat tool, which provides reliable monitoring of the MySQL replication lag and allows Orchestrator to block primary promotion of the extra slow instances (ones with the lag greater than 10 minutes)
* {{ k8spsjira(105) }} Provide the backup and restore functionality for clusters with Group Replication
* {{ k8spsjira(112) }} Use HAProxy to simplify the exposure and enable load balancing for the asynchronous MySQL cluster

## Improvements

* {{ k8spsjira(23) }} Add [cert-manager support](../TLS.md#install-and-use-the-cert-manager) to generate and update TLS certificates automatically
* {{ k8spsjira(31) }} Show `ready` state in the custom resource output produced by the `kubectl get ps` command only after all LoadBalancers are ready
* {{ k8spsjira(59) }} Add [mysql.primaryServiceType](../operator.md#mysql-primaryservicetype) Custom Resource option to configure the primary exposure type in one place instead of exposing all Pods with specific Service type
* {{ k8spsjira(88) }} Allow configuring `prefix` field for backup storages via the [backup.s3.prefix](../operator.md#backup-s3-prefix) Custom Resource option
* {{ k8spsjira(93) }} Avoid running multiple backups on the same Pod by either scheduling new backup to another Node or blocking it until the running one finishes
* {{ k8spsjira(97) }} [S3 backup finalizer](../backups.md#finalizers) now triggers the actual deletion of backup files from the S3 bucket when there is a manual or scheduled removal of the corresponding backup object
* {{ k8spsjira(103) }} Show MySQL Router and Orchestrator statuses in the Custom Resource through the `kubectl` command
* {{ k8spsjira(104) }} Avoid using the root user in backup containers to run XtraBackup with the lowest possible privileges for higher security and isolation of the cluster components
* {{ k8spsjira(115) }} Make it possible [to use API Key](../monitoring.md#operator-monitoring-client-token) to authorize within Percona Monitoring and Management Server as a more convenient and modern alternative password-based authentication
* {{ k8spsjira(119) }} and {{ k8spsjira(150) }}	Allow to specify custom init images for the cluster components (MySQL, Orchestrator, Router, HAProxy, etc.) to simplify customizing images by the end users
* {{ k8spsjira(138) }} Expose MySQL default and administrative connection ports via MySQL Router
* {{ k8spsjira(145) }} Add `delete-mysql-pods-in-order` finalizer to control the proper Pods deletion order in case of the cluster deletion event
* {{ k8spsjira(152) }} Allow configuring the Orchestrator exposure via the [orchestrator.expose.type](../operator.md#orchestrator-expose-type) option in Custom Resource

## Bugs Fixed

* {{ k8spsjira(91) }} Fix a bug that caused backups to run even if user disabled them
* {{ k8spsjira(92) }} Fixed a bug where backup did not throw error in logs in case of incorrect S3 credentials, making the impression that everything is working fine
* {{ k8spsjira(114) }} Fix a bug due to which setting `primaryServiceType` to `LoadBalancer` with asynchronous replication resulted in no STATE and ENDPOINT in the custom resource output produced by the `kubectl get ps` command
* {{ k8spsjira(121) }} Fix a bug where XtraBackup process erroneously continued running on the appropriate Node instead of being killed on backup Pod termination, e.g. with `kubectl delete ps-backup` command
* {{ k8spsjira(125) }} Fix a bug where the Operator was erroneously removing cluster Secret in case of the Custom Resource deletion, causing change of all passwords if user creates the new one
* {{ k8spsjira(132) }} Fix a bug which made MySQL client quickly reaching connections limit on EKS due to the large number of connection attempts done by the AWS healthchecks that could not access MySQL Router

## Deprecation and removal

* {{ k8spsjira(49) }} The `clustercheck` system user was removed and is no longer automatically created by default; starting from now, the `monitor` user is used for probes-related functionality

## Supported Platforms

The following platforms were tested and are officially supported by the Operator
0.3.0:

* [Google Kubernetes Engine (GKE)](https://cloud.google.com/kubernetes-engine) 1.22 - 1.25
* [Amazon Elastic Container Service for Kubernetes (EKS)](https://aws.amazon.com) 1.20 - 1.23
* [Minikube](https://minikube.sigs.k8s.io/docs/) 1.27 (based on Kubernetes 1.25)

This list only includes the platforms that the Percona Operators are specifically tested on as part of the release process. Other Kubernetes flavors and versions depend on backward compatibility offered by Kubernetes itself.
