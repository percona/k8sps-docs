# *Percona Operator for MySQL* 0.5.0

* **Date**

    March 30, 2023

* **Installation**

    [Installing Percona Operator for MySQL](../index.md#advanced-installation-guides)

!!! note

    Version 0.5.0 of the Percona Operator for MySQL is **a tech preview release** and it is **not recommended for production environments**. **As of today, we recommend using** [Percona Operator for MySQL based on Percona XtraDB Cluster](https://docs.percona.com/percona-operator-for-mysql/pxc/index.html), which is production-ready and contains everything you need to quickly and consistently deploy and scale MySQL clusters in a Kubernetes-based environment, on-premises or in the cloud.

## Release Highlights

* The Operator is now able to query Version Service and automatically get the latest version of the software compatible with it, as other Percona Operators are doing; the Smart Upgrade functionality is not yet here, but will be implemented in consequent releases

* The [Telemetry functionality](../telemetry.md) implemented in this release allows Operator to capture anonymous versions and usage statistics used by Percona to improve the Operator; see our [official documentation](../telemetry.md) to find out what exactly is collected and how to disable this feature, if needed

## New Features

* {{ k8spsjira(63) }}: Version Service support for the Operator allows now to get version number updates for the various components of the cluster

* {{ k8spsjira(141) }}: Add capturing [anonymous telemetry and usage data](../telemetry.md) following the way of other Percona Operators

## Improvements

* {{ k8spsjira(166) }}: Operator behaves unexpectedly due to incomplete TLS section enabled for active mysql cluster
* {{ k8spsjira(187) }}: Allow running only one backup at the same time
* {{ k8spsjira(217) }}: MySQL Router - Flexible configuration
* {{ k8spsjira(229) }}: Improve security and meet compliance requirements by building the Operator based on Red Hat Universal Base Image (UBI) 9 instead of UBI 8

* {{ k8spsjira(240) }}: Use TLS encryption for system users

* {{ k8spsjira(243) }}: Update default configuration for HaProxy

* {{ k8spsjira(245) }}: Operator doesn't generate missing passwords

* {{ k8spsjira(246) }}: remove cluster.local suffix

* {{ k8spsjira(251) }}: Update go version to 1.20

## Bugs Fixed

* {{ k8spsjira(231) }}: Missing grants for the replication user
* {{ k8spsjira(157) }} configuration-hash annotation in mysql pod definition is empty
* {{ k8spsjira(158) }}: cert manager certificate renew is not working after delete+apply
* {{ k8spsjira(167) }}: operator ignores the haproxy with group replication 
* {{ k8spsjira(168) }}: The lack of external cert issuer prevents operator from cluster creation
* {{ k8spsjira(170) }}: TLS secrets are not removed with cert-manager certificates removal
* {{ k8spsjira(185) }}: Some cluster connections don't use TLS
* {{ k8spsjira(209) }}: service left when haproxy disabled
* {{ k8spsjira(213) }}: Pmmserverkey was't deleted but became empty
* {{ k8spsjira(214) }}: cluster with disabled orchestrator never becomes ready
* {{ k8spsjira(219) }}: CR status getting stuck on GR scale-down
* {{ k8spsjira(220) }}: Backup fails when storage credentials or parameters contain special characters
* {{ k8spsjira(222) }}: Too many aborted connections in MySQL logs
* {{ k8spsjira(225) }}: Prohibit restore creation without destination or backupName
* {{ k8spsjira(226) }}: Fail backup with wrong clusterName or storageName immediately
* {{ k8spsjira(227) }}: Can't change label/annotation value in service
* {{ k8spsjira(235) }}: helm chart - fix orchestrator service account/role creation

## Supported Platforms

The following platforms were tested and are officially supported by the Operator
0.5.0:

* [Google Kubernetes Engine (GKE)](https://cloud.google.com/kubernetes-engine) 1.23 - 1.25
* [Amazon Elastic Container Service for Kubernetes (EKS)](https://aws.amazon.com) 1.21 - 1.24
* [Minikube](https://minikube.sigs.k8s.io/docs/) 1.28 (based on Kubernetes 1.25)

This list only includes the platforms that the Percona Operators are specifically tested on as part of the release process. Other Kubernetes flavors and versions depend on backward compatibility offered by Kubernetes itself.
