# *Percona Operator for MySQL* 0.6.0

* **Date**

    September 5, 2023

* **Installation**

    [Installing Percona Operator for MySQL](../System-Requirements.md#installation-guidelines)

Percona Operator for MySQL allows users to deploy MySQL clusters with both asynchronous and group replication topology. This release includes various stability improvements and bug fixes, getting the Operator closer to the General Availability stage. Version 0.6.0 of the Percona Operator for MySQL is still **a tech preview release** and it is **not recommended for production environments**. **As of today, we recommend using** [Percona Operator for MySQL based on Percona XtraDB Cluster :octicons-link-external-16:](https://docs.percona.com/percona-operator-for-mysql/pxc/index.html), which is production-ready and contains everything you need to quickly and consistently deploy and scale MySQL clusters in a Kubernetes-based environment, on-premises or in the cloud.

## Highlights

* The [Smart Upgrade functionality](../update.md/#automated-upgrade) allows users to automatically get the latest version of the software compatible with the Operator and apply it safely
* The role of the HAProxy load balancer, which was previously used for asynchronous replication between MySQL instances, has been extended. Now HAProxy can also be used with group replication as an alternative to MySQL Router
* Starting from this release, semi-synchronous replication is not supported by the Operator in favor of using safer options: either group replication, or asynchronous replication (see [this blog post :octicons-link-external-16:](https://www.percona.com/blog/face-to-face-with-semi-synchronous-replication/) for details on how asynchronous replication may cause data loss in case of a node crash)


## New features

* {{ k8spsjira(283) }}: Now the cluster with group replication can be deployed with HAProxy instead of MySQL Router
* {{ k8spsjira(160) }}: Add Smart Upgrade functionality to automate Percona Server for MySQL upgrades

## Improvements

* {{ k8spsjira(162) }}: Now [MySQL X protocol :octicons-link-external-16:](https://www.percona.com/blog/understanding-mysql-x-all-flavors) can be used with HAProxy load balancing
* {{ k8spsjira(163) }}: Percona Monitoring and Management (PMM) is now able to gather HAProxy metrics
* {{ k8spsjira(205) }}: Update user passwords on a per-user basis instead of a cumulative update so that if an error occurs while changing a user's password, other system users are not affected
* {{ k8spsjira(270) }}: Use more clear [Controller :octicons-link-external-16:](https://kubernetes.io/docs/concepts/architecture/controller/) names in log messages to ease troubleshooting
* {{ k8spsjira(280) }}: Full cluster crash recovery with group replication is now using MySQL shell built-in checks to detect the member with latest transactions and reboots from it, making the cluster prone to data loss
* {{ k8spsjira(281) }}: The Operator [can now be run locally :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/main/CONTRIBUTING.md#1-contributing-to-the-source-tree) against a remote Kubernetes cluster, which simplifies the development process, substantially shortening the way to make and try minor code improvements

## Bugs Fixed

* {{ k8spsjira(260) }}: Fix a bug due to which group replication cluster can stuck in initializing state after restore
* {{ k8spsjira(190) }}: Fix a bug due to which the Operator could not delete a cluster that was stuck in initializing state (for example, due to the inability to start one of the Pods)
* {{ k8spsjira(211) }}: Fix a bug which caused the cluster status to oscillate between “initializing” and “ready” on passwords change
* {{ k8spsjira(223) }}: Fix a bug due to which deleting a Pod with its PVC was breaking the InnoDB Cluster because of the UUID change of the recreated Pod
* {{ k8spsjira(224) }}: Fix a bug that caused flooding the Operator logs with warnings about missing parallel-applier settings on cluster members at each reconcile loop
* {{ k8spsjira(244) }}: Fix a bug due to which MySQL Router Pods were not restarted at the custom configuration ConfigMap change
* {{ k8spsjira(254) }}: Fix a bug due to which it was possible to run multiple restores for the same cluster in parallel
* {{ k8spsjira(257) }}: Fix a bug causing a hang when trying to delete a backup in an `error` state
* {{ k8spsjira(259) }}: Fix a bug that caused flooding the Operator logs with "failed to get cluster status" errors during the cluster scaling
* {{ k8spsjira(262) }}: Fix a bug which caused the Operator to delete SSL issuer and certificate at cluster deletion if `delete-ssl` finalizer was not set
* {{ k8spsjira(263) }}: Fix a bug due to which setting incorrect issuer in the Custom Resource of the existing cluster resulted in "READY" state instead of the "ERROR" one
* {{ k8spsjira(272) }}: Fix a bug due to which the password of the `monitor` user was visible in the pmm-client logs
* {{ k8spsjira(278) }}: Fix a bug due to which MySQL Pods did not restart when the user-created MySQL config was provided with the `<cluster-name>-mysql` ConfigMap

## Deprecation and removal

* {{ k8spsjira(276) }}: Semi-synchronous replication support was removed from the Operator; now it provides either group replication with HAProxy or MySQL Router, or asynchronous replication with Orchestrator and HAProxy

## Supported Platforms

The Operator was developed and tested with Percona Server for MySQL  8.0.33-25.
Other options may also work but have not been tested. Other software components include:

* Orchestrator 3.2.6-9
* MySQL Router 8.0.33-25
* XtraBackup 8.0.33-27
* Percona Toolkit 3.5.3
* HAProxy 2.8.1
* PMM Client 2.39

The following platforms were tested and are officially supported by the Operator
0.6.0:

* [Google Kubernetes Engine (GKE) :octicons-link-external-16:](https://cloud.google.com/kubernetes-engine) 1.24 - 1.27
* [Amazon Elastic Container Service for Kubernetes (EKS) :octicons-link-external-16:](https://aws.amazon.com) 1.23 - 1.27
* [Minikube :octicons-link-external-16:](https://minikube.sigs.k8s.io/docs/) 1.31.2 (based on Kubernetes 1.27)

This list only includes the platforms that the Percona Operators are specifically tested on as part of the release process. Other Kubernetes flavors and versions depend on backward compatibility offered by Kubernetes itself.
