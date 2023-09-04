# *Percona Operator for MySQL* 0.6.0

* **Date**

    September 5, 2023

* **Installation**

    [Installing Percona Operator for MySQL](../System-Requirements.md#installation-guidelines)

Percona Operator for MySQL allows users to deploy MySQL clusters with both asynchronous and group replication topology. This release includes various stability improvements and bug fixes, getting the Operator closer to the General Availability stage. Version 0.6.0 of the Percona Operator for MySQL is still **a tech preview release** and it is **not recommended for production environments**. **As of today, we recommend using** [Percona Operator for MySQL based on Percona XtraDB Cluster](https://docs.percona.com/percona-operator-for-mysql/pxc/index.html), which is production-ready and contains everything you need to quickly and consistently deploy and scale MySQL clusters in a Kubernetes-based environment, on-premises or in the cloud.

## Highlights

* The [Smart Upgrade functionality](../upgrade.md/#operator-update-smartupdates) allows users to automatically get the latest version of the software compatible with the Operator and apply it safely

## New features

* {{ k8spsjira(239) }} and * {{ k8spsjira(216) }}: Bootstrap group replication with mysql-shell and Force clone when scaling up
* {{ k8spsjira(283) }}: Now the cluster with group replication can be deployed with HAProxy instead of MySQL Router
* {{ k8spsjira(160) }}: Add Smart Upgrade functionality to automate Percona Server for MySQL upgrades

## Improvements

* {{ k8spsjira(162) }}: [Support of the proxy-protocol](../haproxy-conf.html#haproxy-conf-protocol) in HAProxy to preserve users’ IP-address. It allows users to fine-tune the access to the database and have proper audit
* {{ k8spsjira(163) }}: Make Percona Monitoring and Management (PMM) able to gather HAProxy metrics
* * {{ k8spsjira(205) }}: Update user passwords individually
* {{ k8spsjira(270) }}: Use more clear [Controller](https://kubernetes.io/docs/concepts/architecture/controller/) names in log messages to ease troubleshooting
* {{ k8spsjira(280) }}: Full cluster crash recovery with group replication is now using MySQL shell built-in checks to detect the member with latest transactions and reboots from it, making the cluster prone to data loss
* {{ k8spsjira(281) }}: The Operator [can now be run locally](../ToDo.md) against a remote Kubernetes cluster, which simplifies the development process, substantially shortening the way to make and try minor code improvements

## Bugs Fixed

* {{ k8spsjira(260) }}: Fix a bug due to which group replication cluster can stuck in initializing state after restore
* {{ k8spsjira(190) }}: Stuck on delete *CAUSED BY K8SPS-260, fixed by K8SPS-239*
* {{ k8spsjira(211) }}: cluster status is flapping on passwords change
* {{ k8spsjira(223) }}: Fix a bug due to which deleting a Pod with its PVC was breaking the InnoDB Cluster because of the UUID change of the recreated Pod
* {{ k8spsjira(224) }}: Fix a bug that caused flooding the Operator logs with warnings about missing parallel-applier settings on cluster members at each reconcile loop
* {{ k8spsjira(244) }}: Fix a bug due to which MySQL Router Pods were not restarted at custom configuration ConfigMap change
* {{ k8spsjira(249) }}: Operator should run cluster.rescan() if needed
* {{ k8spsjira(254) }}: Fix a bug due to which it was possible to run multiple restores for one cluster in parallel
* {{ k8spsjira(257) }}: Fix a bug causing a hang when trying to delete a backup in an `error` state
* {{ k8spsjira(259) }}: Fix a bug that caused flooding the Operator logs with "failed to get cluster status" errors during the cluster scaling
* {{ k8spsjira(261) }}: Return error state if external cert issuer is invalid under cluster creation *WAS ANYTHING FIXED HERE?*
* {{ k8spsjira(262) }}: Fix a bug which caused the Operator to delete SSL issuer and certificate at cluster deletion if `delete-ssl` finalizer was not set
* {{ k8spsjira(263) }}: Fix a bug due to which setting incorrect issuer in Custom Resource of the existing cluster resulted in "READY" state instead of the "ERROR" one
* {{ k8spsjira(272) }}: Fix a bug due to which the password of the `monitor` user was visible in the pmm-client logs
* {{ k8spsjira(278) }}: Fix a bug due to which MySQL Pods did not restart when the user-created MySQL config was provided with the <cluster-name>-mysql ConfigMapK

## Deprecation and removal

* {{ k8spsjira(276) }}: Semi-synchronous replication support was removed from the Operator; now it provides either group replication with MySQL Router, or asynchronous replication with Orchestrator and HAProxy

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

* [Google Kubernetes Engine (GKE)](https://cloud.google.com/kubernetes-engine) 1.24 - 1.27
* [Amazon Elastic Container Service for Kubernetes (EKS)](https://aws.amazon.com) 1.23 - 1.27
* [Minikube](https://minikube.sigs.k8s.io/docs/) 1.31.2 (based on Kubernetes 1.27)

This list only includes the platforms that the Percona Operators are specifically tested on as part of the release process. Other Kubernetes flavors and versions depend on backward compatibility offered by Kubernetes itself.
