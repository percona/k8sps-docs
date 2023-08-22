# *Percona Operator for MySQL* 0.5.0

* **Date**

    March 30, 2023

* **Installation**

    [Installing Percona Operator for MySQL](../System-Requirements.md#installation-guidelines)

Percona Operator for MySQL allows users to deploy MySQL clusters with both asynchronous and group replication topology. This release includes various stability improvements and bug fixes, getting the Operator closer to the General Availability stage. Version 0.5.0 of the Percona Operator for MySQL is still **a tech preview release** and it is **not recommended for production environments**. **As of today, we recommend using** [Percona Operator for MySQL based on Percona XtraDB Cluster](https://docs.percona.com/percona-operator-for-mysql/pxc/index.html), which is production-ready and contains everything you need to quickly and consistently deploy and scale MySQL clusters in a Kubernetes-based environment, on-premises or in the cloud.

## Highlights

* The [Smart Upgrade functionality](../upgrade.md/#operator-update-smartupdates) allows users to automatically get the latest version of the software compatible with the Operator and apply it safely

## New features

K8SPS-239 and K8SPS-216	Bootstrap group replication with mysql-shell and Force clone when scaling up
* {{ k8spsjira(283) }}: Now the cluster with group replication can be deployed with HAProxy instead of MySQL Router
* {{ k8spsjira(160) }}: Add Smart Upgrade functionality to automate Percona Server for MySQL upgrades

## Improvements

* {{ k8spsjira(162) }}: [Support of the proxy-protocol](../haproxy-conf.html#haproxy-conf-protocol) in HAProxy
* {{ k8spsjira(163) }}: Make Percona Monitoring and Management (PMM) able to gather HaProxy metrics
* K8SPS-205	Update user passwords individually
* {{ k8spsjira(270) }}: Use more clear [Controller](https://kubernetes.io/docs/concepts/architecture/controller/) names in log messages
* {{ k8spsjira(280) }}: Full cluster crash recovery with group replication is now using MySQL shell built-in checks to detect the member with latest transactions and reboots from it, making the cluster prone to data loss
* {{ k8spsjira(281) }}: The Operator [can now be run locally](../ToDo.md) against a remote Kubernetes cluster, which simplifies the development process, substantially shortening the way to make and try minor code improvements
* {{ k8spsjira(285) }}: Add startup probe for MySQL Router

## Bugs Fixed

K8SPS-230	Cluster doesn't start correctly unless 3 mysql pods	Dmitriy Kostiuk	
K8SPS-234	When Node restart randomly has issue in name resolution	Ege Gunes
K8SPS-260	group replication cluster stuck in initializing state after restore
K8SPS-190	Stuck on delete
K8SPS-211	cluster status is flapping on passwords change
K8SPS-223	Deleting a pod and its PVC breaks InnoDB Cluster
K8SPS-224	mysql-shell warns about missing parallel-applier settings on members
K8SPS-244	Mysql router pods are not restarted on custom config map changes
K8SPS-249	Operator should run cluster.rescan() if needed
K8SPS-254	Prohibit to run several restores in parallel
K8SPS-256	Don't print any sensitive information in the logs
K8SPS-257	Stuck in deleting backup in Error state
K8SPS-259	operator error during cluster scaling
K8SPS-261	Return error state if external cert issuer is invalid under cluster creation
K8SPS-262	operator deletes the ssl issuer and certificate if delete-ssl finalizer is not specified
K8SPS-263	Return error state if apply incorrect issuer on existent cluster
K8SPS-272	Monitor password is visible in pmm-client logs
* {{ k8spsjira(278) }}: Fix a bug due to which MySQL Pods did not restart when the user-created MySQL config was provided with the <cluster-name>-mysql ConfigMapK

## Deprecation and removal

* {{ k8spsjira(276) }}: Semi-synchronous replication support was removed from the Operator; now it provides either group replication with MySQL Router, or asynchronous replication with Orchestrator and HAProxy

## Supported Platforms

The Operator was developed and tested with Percona Server for MySQL 8.0.32.
Other options may also work but have not been tested.

The following platforms were tested and are officially supported by the Operator
0.5.0:

* [Google Kubernetes Engine (GKE)](https://cloud.google.com/kubernetes-engine) 1.22 - 1.25
* [Amazon Elastic Container Service for Kubernetes (EKS)](https://aws.amazon.com) 1.22 - 1.25
* [Minikube](https://minikube.sigs.k8s.io/docs/) 1.29 (based on Kubernetes 1.26)

This list only includes the platforms that the Percona Operators are specifically tested on as part of the release process. Other Kubernetes flavors and versions depend on backward compatibility offered by Kubernetes itself.
