# *Percona Operator for MySQL* 0.9.0

* **Date**

    February 11, 2025

* **Installation**

    [Installing Percona Operator for MySQL](../System-Requirements.md#installation-guidelines)

Percona Operator for MySQL allows users to deploy MySQL clusters with both asynchronous and group replication topology. This release includes various stability improvements and bug fixes, getting the Operator closer to the General Availability stage. Version 0.9.0 of the Percona Operator for MySQL is still **a tech preview release** and it is **not recommended for production environments**. **As of today, we recommend using** [Percona Operator for MySQL based on Percona XtraDB Cluster](https://docs.percona.com/percona-operator-for-mysql/pxc/index.html), which is production-ready and contains everything you need to quickly and consistently deploy and scale MySQL clusters in a Kubernetes-based environment, on-premises or in the cloud.

## Highlights

## Scheduled backups

Starting from now, the Operator supports scheduled backups, moving towards the upcoming general availability status. You can configure scheduled backups in the Custom Resource, as you do with other Percona Operators, in the `backup.schedule` subsection, setting the `name` of the backup, `schedule` in [crontab format :octicons-link-external-16:](https://en.wikipedia.org/wiki/Cron), as well as the backup `storage`, and, optionally, the retention (the number of backups to `keep`):

```yaml
backup:
  ...
  schedule:
    - name: "sat-night-backup"
      schedule: "0 0 * * 6"
      keep: 3
      storageName: s3-us-west
```

See more detailed instructions on configuring scheduled backups in [our documentation](../backups-scheduled.md).

## New features

* {{ k8spsjira(348) }}: [Scheduled backups](../backups-scheduled.md) are now supported in addition to on-demand ones
* {{ k8spsjira(367) }}: A new [percona.com/delete-mysql-pvc](../operator.md#metadata-name) Finalizer can be used to automatically delete Persistent Volume Claims for the database cluster Pods after the cluster deletion event (off by default)

## Improvements

* {{ k8spsjira(361) }}: Now the recommended 33061 port is used during the Group Replication bootstrap instead of the default MySQL port 3306
* {{ k8spsjira(364) }}: Reconciling full cluster crush is now done only for the Group Replication cluster type, as not needed for asynchronous replication clusters
* {{ k8spsjira(377) }}: A clean-up was done in the database initialization code to avoid using the `--skip-ssl` option in the Operator, which was removed in MySQL 8.4 

## Bugs Fixed

* {{ k8spsjira(350) }}: Remove the the `sslInternalSecretName` Custom Resource option which was not actually used by the Operator
* {{ k8spsjira(354) }}: Fix a bug where custom sslSecret was deleted at cluster deletion even with disabled `percona.com/delete-ssl` finalizer
* {{ k8spsjira(359) }}: Fix a bug where the Operator couldn't perform crash recovery for the Group Replication cluster, if there was a leftover instance 
* {{ k8spsjira(360) }}: Fix a bug where the outdated orchestrator Services were not removed after the asynchronous cluster downscale
* {{ k8spsjira(365) }}: Fix a bug that caused crash loop in case of MySQL version upgrade due to restarting MySQL container after adding the Pod to the cluster
* {{ k8spsjira(369) }} and {{ k8spsjira(373) }}: Fix a bug where the asynchronous replication cluster was temporarily getting error status during smart update or when starting the single-Pod cluster
* {{ k8spsjira(372) }}: Fix a bug where MySQL Pod was failing during the SmartUpdate on two-node asynchronous replication cluster
* {{ k8spsjira(388) }}: Fix a bug where the Operator could not create ps-db-mysql and ps-db-orc StatefulSet with enabled Resource Quota (thanks to xirehat for contribution)

## Deprecation and removal

* The `sslInternalSecretName` option option is removed from the Custom Resource

## Known limitations

* Both upgrade to the Operator version 0.9.0 and the appropriate database cluster upgrade can not be done in a usual way due to a number of internal changes, and require additional manual operations.

    * Upgrading the Operator can be done with [this workaround](../update.md#prerequisites)
    * Upgrading the database cluster can be done by [deleting and recreating it](../delete.md#delete-the-database-cluster)

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
