# *Percona Operator for MySQL* 0.8.0

* **Date**

    July 16, 2024

* **Installation**

    [Installing Percona Operator for MySQL](../System-Requirements.md#installation-guidelines)

Percona Operator for MySQL allows users to deploy MySQL clusters with both asynchronous and group replication topology. This release includes various stability improvements and bug fixes, getting the Operator closer to the General Availability stage. Version 0.8.0 of the Percona Operator for MySQL is still **a tech preview release** and it is **not recommended for production environments**. **As of today, we recommend using** [Percona Operator for MySQL based on Percona XtraDB Cluster](https://docs.percona.com/percona-operator-for-mysql/pxc/index.html), which is production-ready and contains everything you need to quickly and consistently deploy and scale MySQL clusters in a Kubernetes-based environment, on-premises or in the cloud.

## Highlights

### Supporting cluster-wide Operator installation

Starting from now, the Operator [can be installed](../cluster-wide.md) in multi-namespace (so-called “cluster-wide”) mode, enabling management of Percona Server for MySQL clusters across multiple namespaces from a single Operator. This functionality, already available for other Percona Operators, brings greater flexibility and efficiency to managing MySQL databases on Kubernetes.

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

## New features

* {{ k8spsjira(149) }}: Custom Resource options now include [customizable health checks and timeouts](../operator.md#proxyhaproxyreadinessprobestimeoutseconds) for HAProxy
* {{ k8spsjira(186) }} and {{ k8spsjira(370) }}: Removing `allowUnsafeConfigurations` Custom Resource option in favor of fine-grained safety control in the `unsafeFlags` subsection
* {{ k8spsjira(241) }}: Support for the [cluster-wide Operator mode](../cluster-wide.md) allowing one Operator to watch for Percona Server for MySQL Custom Resources in several namespaces

## Improvements

* {{ k8spsjira(334) }}: Finalizers were renamed to contain fully qualified domain names (FQDNs), avoiding potential conflicts with other finalizer names in the same Kubernetes environment
* {{ k8spsjira(333) }}: improve `delete-mysql-pods-in-order` finalizer to take into account possible change of the primary instance in group replication
* {{ k8spsjira(340) }}: A `securityContext` of the `xtrabackup` container [can now be configured](../operator.md#backupcontainersecuritycontext) allowing administrators to define security profiles for the container 
* {{ k8spsjira(43) }}: Custom Resource status obtained with the `kubectl get ps` command now takes into account both group and asynchronous replication, and doesn’t report the cluster as ready if the replication is broken

## Bugs Fixed

* {{ k8spsjira(366) }}: Fix a bug where cluster deletion caused the Operator panic due to querying a non-existing Custom Resource
* {{ k8spsjira(346) }}: Fix a bug where the cluster started with 1 node and dataset bigger than 100 GB was unable to scale up because of too short bootstrap timeout
* {{ k8spsjira(341) }}: Fix a bug where failed backup deletion got stuck because of being blocked by the `delete-backup` finalizer
* {{ k8spsjira(310) }}: TLS certificate and issuer names generated by the Operator are now aligned with other Percona Operators to streamline coherent user experience
* {{ k8spsjira(301) }}: Fix a bug that caused multiple error messages to appear in logs on MySQL Pod deletion
* {{ k8spsjira(307) }}:  Fix a bug where updating database with SmartUpdate strategy didn’t produce log messages about updated primary Pod and about finishing the update process

## Deprecation and removal

* Starting from now, `allowUnsafeConfigurations` Custom Resource option is deprecated in favor of a number of options under the `unsafeFlags` subsection. Setting `allowUnsafeConfigurations` won't have any effect; upgrading existing clusters with `allowUnsafeConfigurations=true` will cause everything under [unsafeFlags](../operator.md#operator-unsafeflags-section) set to true
* Finalizers were renamed to contain fully qualified domain names:

    * `delete-mysql-pods-in-order` renamed to `percona.com/delete-mysql-pods-in-order`
    * `delete-ssl` renamed to `percona.com/delete-ssl`
    * `delete-backup` renamed to `percona.com/delete-backup`

## Supported Platforms

The Operator was developed and tested with Percona Server for MySQL 8.0.36-28.
Other options may also work but have not been tested. Other software components include:

* Orchestrator 3.2.6-12
* MySQL Router 8.0.36
* XtraBackup 8.0.35-31
* Percona Toolkit 3.6.0
* HAProxy 2.8.5
* PMM Client 2.42.0

The following platforms were tested and are officially supported by the Operator
0.8.0:

* [Google Kubernetes Engine (GKE) :octicons-link-external-16:](https://cloud.google.com/kubernetes-engine) 1.27 - 1.29
* [Amazon Elastic Container Service for Kubernetes (EKS) :octicons-link-external-16:](https://aws.amazon.com) 1.27 - 1.30
* [Minikube :octicons-link-external-16:](https://minikube.sigs.k8s.io/docs/) 1.33.1 (based on Kubernetes 1.30.0)

This list only includes the platforms that the Percona Operators are specifically tested on as part of the release process. Other Kubernetes flavors and versions depend on backward compatibility offered by Kubernetes itself.
