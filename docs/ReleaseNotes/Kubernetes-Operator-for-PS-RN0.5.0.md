# *Percona Operator for MySQL* 0.5.0

* **Date**

    March 30, 2023

* **Installation**

    [Installing Percona Operator for MySQL](../index.md#advanced-installation-guides)

!!! note

    Version 0.5.0 of the Percona Operator for MySQL is **a tech preview release** and it is **not recommended for production environments**. **As of today, we recommend using** [Percona Operator for MySQL based on Percona XtraDB Cluster](https://docs.percona.com/percona-operator-for-mysql/pxc/index.html), which is production-ready and contains everything you need to quickly and consistently deploy and scale MySQL clusters in a Kubernetes-based environment, on-premises or in the cloud.

## Release Highlights

* The Operator is now able to query Version Service and automatically get the latest version of the software compatible with it, as other Percona Operators are doing; the Smart Upgrade functionality is not yet here but will be implemented in consequent releases

* The [Telemetry functionality](../telemetry.md) implemented in this release allows the Operator to capture anonymous versions and usage statistics used by Percona to improve the Operator; see our [official documentation](../telemetry.md) to find out what exactly is collected and how to disable this feature, if needed

## New Features

* {{ k8spsjira(63) }}: Version Service support for the Operator allows now to get version number updates for the various components of the cluster

* {{ k8spsjira(141) }}: Add capturing [anonymous telemetry and usage data](../telemetry.md) following the way of other Percona Operators

## Improvements

* {{ k8spsjira(166) }}: The Operator now updates certificates at all changes in the Custom Resource `tls` section: this fixes the previous behavior, along to which it didn't do anything related to TLS certificates in case of existing SSL secrets, even in the case of wrong/incomplete `tls` configuration

* {{ k8spsjira(217) }}: The user is now able to customize the MySQL Router configuration with the new [proxy.router.configuration](../operator.md#proxy-router-configuration) Custom Resource option

* {{ k8spsjira(229) }}: Improve security and meet compliance requirements by building the Operator based on Red Hat Universal Base Image (UBI) 9 instead of UBI 8

* {{ k8spsjira(240) }}: TLS encrypted connection can now be used by the Operator for the system users, if available; particularly, this allows hardening the cluster security by creating users with `REQUIRE SSL`

* {{ k8spsjira(243) }}: Update default configuration for HaProxy **Nothing noticeable for the end-user**

* {{ k8spsjira(245) }}: Starting from now, the Operator will check user Secrets for missing items and generate missing passwords when needed

* {{ k8spsjira(246) }}: DNS names `SERVICE.NAMESPACE.svc` are now used by the cluster components instead of the longer `SERVICE.NAMESPACE.svc.cluster.local` ones

* {{ k8spsjira(251) }}: The Go version was updated to 1.20

## Bugs Fixed

* {{ k8spsjira(231) }}: Fix missing grants for the replication user
* {{ k8spsjira(157) }}  Fix a bug which caused mysql Pod definition to contain empty `configuration-hash` annotation
* {{ k8spsjira(158) }} and {{ k8spsjira(170) }}: The new delete-ssl finalizer can now be used to automatically delete objects created for SSL (Secret, certificate, and issuer) in case of cluster deletion **Improvement?**
* {{ k8spsjira(167) }}: Fix a bug that caused the Operator to silently ignore the HAProxy enabled in the Custom Resource options with group replication instead of throwing an error about the unsupported functionality
* {{ k8spsjira(168) }}: The Operator was completely relying on the `tls.issuerConf` Custom Resource option provided by the user and doing no checks, being unable to create the cluster without throwing a clear error message if the issuer was not existing or ready
* {{ k8spsjira(209) }}: Fix a bug due to which the HAProxy disabling for an existing cluster didn't lead to removal of the appropriate Service
* {{ k8spsjira(213) }}: Fix a bug where the Operator didn't check if the `pmmserverkey` was empty in the Secrets object instead of considering the empty `pmmserverkey` secret as non-existing and printing the appropriate log message
* {{ k8spsjira(214) }}: Fix a bug due to which creating a cluster without Orchestrator caused it to get stuck in the `initialized` status instead of switching to the `ready` one after the cluster creation
* {{ k8spsjira(219) }}: Fix a bug due to which scaling down a cluster with group replication caused it to get stuck in the `initialized` status instead of switching to the `ready` one after the size change
* {{ k8spsjira(220) }}: Fix a bug that caused backups to fail when the storage parameters credentials or parameters (such destination, endpointUrl, etc.) contained special characters
* {{ k8spsjira(222) }}: Too many aborted connections in MySQL logs **ToDo**
* {{ k8spsjira(225) }}: Fix a bug where the backup restore process could be started by the user without the specified `destination` or `backupName` fields, resulting in a cluster failure
* {{ k8spsjira(226) }}: Fix a bug due to which the Operator was trying to make a backup with the wrong `clusterName` or `storageName` options instead of checking their validity first
* {{ k8spsjira(227) }}: Fix a bug that prevented the Operator from changing the MySQL Router Service annotations and labels following the corresponding Custom Resource options change

## Supported Platforms

The following platforms were tested and are officially supported by the Operator
0.5.0:

* [Google Kubernetes Engine (GKE)](https://cloud.google.com/kubernetes-engine) 1.23 - 1.25
* [Amazon Elastic Container Service for Kubernetes (EKS)](https://aws.amazon.com) 1.21 - 1.24
* [Minikube](https://minikube.sigs.k8s.io/docs/) 1.28 (based on Kubernetes 1.25)

This list only includes the platforms that the Percona Operators are specifically tested on as part of the release process. Other Kubernetes flavors and versions depend on backward compatibility offered by Kubernetes itself.
