# *Percona Operator for MySQL* 0.8.0

* **Date**

    July 16, 2024

* **Installation**

    [Installing Percona Operator for MySQL](../System-Requirements.md#installation-guidelines)

Percona Operator for MySQL allows users to deploy MySQL clusters with both asynchronous and group replication topology. This release includes various stability improvements and bug fixes, getting the Operator closer to the General Availability stage. Version 0.8.0 of the Percona Operator for MySQL is still **a tech preview release** and it is **not recommended for production environments**. **As of today, we recommend using** [Percona Operator for MySQL based on Percona XtraDB Cluster](https://docs.percona.com/percona-operator-for-mysql/pxc/index.html), which is production-ready and contains everything you need to quickly and consistently deploy and scale MySQL clusters in a Kubernetes-based environment, on-premises or in the cloud.

## Highlights

### Fixing the overloaded allowUnsafeConfigurations flag

In the previous Operator versions `allowUnsafeConfigurations` Custom Resource option was used to allow configuring a cluster with unsafe parameters, such as starting it with unsafe number of MySQL or proxy instances. In fact, setting this option to `true` resulted in a wide range of reduced safety features without the user's explicit intent.

With this release, a separate `unsafeFlags` Custom Resource section is introduced for the fine-grained control of the safety loosening features:

```yaml
unsafeFlags:
  mysqlSize: true
  proxy: true
  proxySize: true
  orchestrator: true
  orchestratorSize: true
```

### Other improvements


## New features

* {{ k8spsjira(149) }}: HAProxy - customizable health checks and timeouts
* {{ k8spsjira(43) }}: Improve CR status
* {{ k8spsjira(186) }} and {{ k8spsjira(370) }}: Removing `allowUnsafeConfigurations` Custom Resource option in favor of fine-grained safety control in the `unsafeFlags` subsection
* {{ k8spsjira(241) }}: Support cluster wide
* {{ k8spsjira(347) }}: [investigation] Check new PS Binlog Server

## Improvements

* {{ k8spsjira(345) }}: Add AWS ELB annotation example to default cr.yaml
* {{ k8spsjira(338) }}: [investigation] Cluster creation (from existing PVCs) FullClusterCrachDetected error status
* {{ k8spsjira(334) }}: Add domain-qualified finalizer names
* {{ k8spsjira(333) }}: improve delete-mysql-pods-in-order finalizer in group replication

## Bugs Fixed

* {{ k8spsjira(366) }}: Operator panics after deleting cluster
* {{ k8spsjira(346) }}: Allow the cluster started with 1 node to scale up
* {{ k8spsjira(341) }}: delete-backup finalizer should be ignored for failed backups
* {{ k8spsjira(340) }}: xtrabackup container is missing security context
* {{ k8spsjira(310) }}: tls certificate issuer name is not aligned with other operators
* {{ k8spsjira(301) }}: multiple errors on mysql pod delete
* {{ k8spsjira(304) }}: [investigation] operator logs flooded with router error messages after full cluster crash
* {{ k8spsjira(307) }}: missing log messages on smart update

## Deprecation and removal

* Starting from now, `allowUnsafeConfigurations` Custom Resource option is deprecated in favor of a number of options under the `unsafeFlags` subsection. Setting `allowUnsafeConfigurations` won't have any effect; upgrading existing clusters with `allowUnsafeConfigurations=true` will cause everything under [unsafeFlags](../operator.md#operator-unsafeflags-section) set to true and [TLS funuctionality disabled](../TLS.md#run-percona-server-for-mongodb-without-tls)

## Supported Platforms

The Operator was developed and tested with Percona Server for MySQL 8.0.36-28.
Other options may also work but have not been tested. Other software components include:

* Orchestrator 3.2.6-12
* MySQL Router 8.0.36
* XtraBackup 8.0.35-31
* Percona Toolkit 3.5.7
* HAProxy 2.8.5
* PMM Client 2.42.0

The following platforms were tested and are officially supported by the Operator
0.8.0:

* [Google Kubernetes Engine (GKE) :octicons-link-external-16:](https://cloud.google.com/kubernetes-engine) 1.27 - 1.29
* [Amazon Elastic Container Service for Kubernetes (EKS) :octicons-link-external-16:](https://aws.amazon.com) 1.27 - 1.30
* [Minikube :octicons-link-external-16:](https://minikube.sigs.k8s.io/docs/) 1.33.1 (based on Kubernetes 1.30.0)

This list only includes the platforms that the Percona Operators are specifically tested on as part of the release process. Other Kubernetes flavors and versions depend on backward compatibility offered by Kubernetes itself.
