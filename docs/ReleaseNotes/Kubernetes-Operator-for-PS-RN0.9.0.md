# *Percona Operator for MySQL* 0.9.0

* **Date**

    February 11, 2025

* **Installation**

    [Installing Percona Operator for MySQL](../System-Requirements.md#installation-guidelines)

Percona Operator for MySQL allows users to deploy MySQL clusters with both asynchronous and group replication topology. This release includes various stability improvements and bug fixes, getting the Operator closer to the General Availability stage. Version 0.8.0 of the Percona Operator for MySQL is still **a tech preview release** and it is **not recommended for production environments**. **As of today, we recommend using** [Percona Operator for MySQL based on Percona XtraDB Cluster](https://docs.percona.com/percona-operator-for-mysql/pxc/index.html), which is production-ready and contains everything you need to quickly and consistently deploy and scale MySQL clusters in a Kubernetes-based environment, on-premises or in the cloud.

## Highlights

## Scheduled backups

Starting from now, the Operator supports scheduled backups, moving towards the upcoming general availability status and feature parity with other Percona Operators.

```yaml
 schedule:
#      - name: "sat-night-backup"
#        schedule: "0 0 * * 6"
#        keep: 3
#        storageName: s3-us-west
#      - name: "daily-backup"
#        schedule: "0 0 * * *"
#        keep: 5
#        storageName: s3
```

## New features

* {{ k8spsjira(348) }}: [Scheduled backups](../backups-scheduled.md) are now supported in addition to on-demand ones

## Improvements

* {{ k8spsjira(361) }}: Use port 33061 for GR in group replication bootstrap
* {{ k8spsjira(364) }}: Do `reconcileFullClusterCrash` only for GR
* {{ k8spsjira(377) }}: Clean-up the database initialization code in the Operator to avoid using the `--skip-ssl` option removed in MySQL 8.4 

## Bugs Fixed

* {{ k8spsjira(350) }}: sslInternalSecretName is present in bundle.yaml and docs but not used in code
* {{ k8spsjira(354) }}: Custom sslSecret is deleted when percona.com/delete-ssl Finalizer is disabled
* {{ k8spsjira(359) }}: Fix a bug where the Operator couldn't perform crash recovery if there was a leftover instance in metadata
* {{ k8spsjira(360) }}: After async cluster downscale, orc services aren't cleaned up
* {{ k8spsjira(365) }}: Group replication: mysql container constantly restarts during smart update
* {{ k8spsjira(369) }}: [async] ps cluster has error status during smart update but update finishes successfully
* {{ k8spsjira(372) }}: [async] mysql pod fails during SmartUpdate when spec.mysql.size=2
* {{ k8spsjira(373) }}: [async] 'Unable to determine cluster name' and 'unexpected end of JSON input' errors in operator log
* {{ k8spsjira(388) }}: PS-Operator cannot create ps-db-mysql and ps-db-orc StatefulSet when Resource Quota is enabled

## Deprecation and removal

* Starting from now, `sslInternalSecretName option` option is now removed from the Custom Resource

## Supported Platforms

The Operator was developed and tested with Percona Server for MySQL 8.0.40-31.
Other options may also work but have not been tested. Other software components include:

* Orchestrator 3.2.6-15
* MySQL Router 8.0.40
* XtraBackup 8.0.35-31
* Percona Toolkit 3.7.0
* HAProxy 2.8.11
* PMM Client 2.44.0

Percona Operators are designed for compatibility with all [CNCF-certified :octicons-link-external-16:](https://www.cncf.io/training/certification/software-conformance/) Kubernetes distributions. Our release process includes targeted testing and validation on major cloud provider platforms and OpenShift, as detailed below for Operator version 0.9.0:

* [Google Kubernetes Engine (GKE) :octicons-link-external-16:](https://cloud.google.com/kubernetes-engine) 1.29 - 1.31
* [Amazon Elastic Container Service for Kubernetes (EKS) :octicons-link-external-16:](https://aws.amazon.com) 1.29 - 1.32
* [Minikube :octicons-link-external-16:](https://minikube.sigs.k8s.io/docs/) 1.35.0 (based on Kubernetes 1.32.0)

This list only includes the platforms that the Percona Operators are specifically tested on as part of the release process. Other Kubernetes flavors and versions depend on backward compatibility offered by Kubernetes itself.
