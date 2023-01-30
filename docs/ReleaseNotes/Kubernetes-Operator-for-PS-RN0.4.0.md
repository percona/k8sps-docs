# *Percona Operator for MySQL* 0.4.0

* **Date**

    January 30, 2023

* **Installation**

    [Installing Percona Operator for MySQL](../index.md#advanced-installation-guides)

!!! note

    Version 0.4.0 of the Percona Operator for MySQL is **a tech preview release** and it is **not recommended for production environments**. **As of today, we recommend using** [Percona Operator for MySQL based on Percona XtraDB Cluster](https://docs.percona.com/percona-operator-for-mysql/pxc/index.html), which is production-ready and contains everything you need to quickly and consistently deploy and scale MySQL clusters in a Kubernetes-based environment, on-premises or in the cloud.

## Release Highlights

* This is maintenance release, where we fixed 15 bugs and focused on improving existing features like backups and support for various replication topologies

* Starting from now it [becomes possible](backups.md#restore-the-cluster-from-a-previously-saved-backup) to restore backups to a new cluster, which means bootstrapping the new cluster without an existing backup object.

* This release also includes fixes to the following CVEs (Common Vulnerabilities and Exposures): CVE-2022-40897 (the denial of service vulnerability in Python Packaging Authority setuptools, the operator and mysql-router images are affected), as well as CVE-2022-32149 and CVE-2022-27664 (the denial of service vulnerability in golang binaries, percona-toolkit image used by the Operator is affected). Users of previous Operator versions are advised to upgrade to the version 0.4.0.

## New Features

* {{ k8spsjira(113) }}: Allow [using templates](../options.md/auto-tuning-mysql-options) to define `innodb_buffer_pool_size` when the Operator performs auto-tuning based on container memory limits 

## Improvements

* {{ k8spsjira(90) }}: Add sanity checks for backups: make sure that there is no pre-existing backup with the same name in the cloud storage and that the created backup is not empty
* {{ k8spsjira(130) }}: Standardize cluster and components service [exposure](../expose.md) to have unification of the expose configuration across all Percona Operators
* {{ k8spsjira(95) }}: With [backupSource support](../backups.md#restore-the-cluster-from-a-previously-saved-backup) for restores users are now able to restore database from object storage directly without the need to have ps-backup Custom Resource
* {{ k8spsjira(207) }}: Allow to disable both Orchestrator and HAProxy, starting only a single-node Percona Server for MySQL without replication. Can be useful for development and testing purposes

## Bugs Fixed

* {{ k8spsjira(155) }}: Fix the bug where replicasServiceType option could not be set to LoadBalancer
* {{ k8spsjira(151) }} and {{ k8spsjira(156) }}: Fix the bug which prevented starting a cluster with the `replicasServiceType` option set to `LoadBalancer` or `NodePort`
* {{ k8spsjira(159) }}: Fix the bug which caused expose options `trafficPolicy`, `loadBalancerSourceRanges` and `annotations` being ignored by the Operator 
* {{ k8spsjira(164) }}: The Operator now does not attempt to start Percona Monitoring and Management (PMM) client sidecar if the corresponding secret does not contain the `pmmserver` or `pmmserverkey` key 
* {{ k8spsjira(174) }}: Fix the bug due to which the activated `delete-backup` finalizer prevented deleting failed backups
* {{ k8spsjira(175) }}: Fix the bug due to which the `delete-backup` finalizer was unable to delete backups on Azure blob storage and Google Cloud Storage
* {{ k8spsjira(176) }}: Fix the bug due to which backup deletion was failing if the cluster was deleted before
* {{ k8spsjira(178) }}: Fix the bug where annotations and trafficPolicy didn’t work for HAProxy
* {{ k8spsjira(179) }}: Fix the bug due to which cluster configured for Group Replication would break and get stuck in the "initializing" status if its primary Pod was deleted
* {{ k8spsjira(180) }}: Fix the bug due to which the `delete-mysql-pods-in-order` finalizer was throwing errors to log instead of info messages
* {{ k8spsjira(183) }}: Fix the bug where the cluster didn't get ready status on Minikube, even when all the Pods were up and running
* {{ k8spsjira(194) }}: Fix the bug which made it impossible for both Percona Operator for MongoDB and Percona Operator for MySQL based on Percona Server for MySQL to be successfully installed in one Namespace
* {{ k8spsjira(195) }}: Fix the bug where the cluster based on Group Replication didn't get ready status, even when all the Pods were up and running
* {{ k8spsjira(202) }}: Fix the bug due to which cluster topology couldn’t be safely changed during the restore process, with replica source change possible making the replica stuck in CrashLoopBackOff

## Supported Platforms

The following platforms were tested and are officially supported by the Operator
0.3.0:

* [Google Kubernetes Engine (GKE)](https://cloud.google.com/kubernetes-engine) 1.23 - 1.25
* [Amazon Elastic Container Service for Kubernetes (EKS)](https://aws.amazon.com) 1.21 - 1.24
* [Minikube](https://minikube.sigs.k8s.io/docs/) 1.28 (based on Kubernetes 1.25)

This list only includes the platforms that the Percona Operators are specifically tested on as part of the release process. Other Kubernetes flavors and versions depend on backward compatibility offered by Kubernetes itself.
