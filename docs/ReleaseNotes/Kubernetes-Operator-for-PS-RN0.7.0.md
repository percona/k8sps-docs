# *Percona Operator for MySQL* 0.7.0

* **Date**

    March 25, 2024

* **Installation**

    [Installing Percona Operator for MySQL](../System-Requirements.md#installation-guidelines)

Percona Operator for MySQL allows users to deploy MySQL clusters with both asynchronous and group replication topology. This release includes various stability improvements and bug fixes, getting the Operator closer to the General Availability stage. Version 0.7.0 of the Percona Operator for MySQL is still **a tech preview release** and it is **not recommended for production environments**. **As of today, we recommend using** [Percona Operator for MySQL based on Percona XtraDB Cluster](https://docs.percona.com/percona-operator-for-mysql/pxc/index.html), which is production-ready and contains everything you need to quickly and consistently deploy and scale MySQL clusters in a Kubernetes-based environment, on-premises or in the cloud.

## Highlights

* 

## New features
* {{ k8spsjira(147) }}: [Support of the proxy-protocol](../haproxy-conf.md#haproxy-conf-protocol) in HAProxy
* {{ k8spsjira(275) }}: Do not start restore if credentials are invalid or backup doesn't exist
* {{ k8spsjira(277) }}: The new `topologySpreadConstraints` Custom Resource option allows to use [Pod Topology Spread Constraints :octicons-link-external-16:](https://kubernetes.io/docs/concepts/workloads/pods/pod-topology-spread-constraints/#spread-constraints-for-pods) to achieve even distribution of Pods across the Kubernetes cluster

## Improvements

* {{ k8spsjira(329) }}: Start to use peer-list from init image
* {{ k8spsjira(129) }}: Add documentation on how to test our PS operator
* {{ k8spsjira(266) }}: Refactor replicator package
* {{ k8spsjira(295) }}: Improve status message on cert issuer error
* {{ k8spsjira(326) }}: Orchestrator mysql-monit resources

## Bugs Fixed

* {{ k8spsjira(124) }}: Backup stuck in running when failing to create bucket
* {{ k8spsjira(144) }}: Pods not able to communicate on AWS
* {{ k8spsjira(146) }}: Set correct type of replication in log messages
* {{ k8spsjira(173) }}: Failed to downscale haproxy
* {{ k8spsjira(185) }}: Some cluster connections don't use TLS
* {{ k8spsjira(256) }}: Don't print any sensitive information in the logs
* {{ k8spsjira(258) }}: Backup object shows backups as Running even if they are waiting
* {{ k8spsjira(273) }}: Operator can't recover from majority loss if cluster is partialy online
* {{ k8spsjira(291) }}: group replication - nodes are not removed from the cluster on scale down
* {{ k8spsjira(302) }}: haproxy and orchestrator services are removed when cluster paused
* {{ k8spsjira(303) }}: missing ports in services
* {{ k8spsjira(311) }}: restore error status is not final
* {{ k8spsjira(312) }}: pods are not restarted on ssl certificate change
* {{ k8spsjira(315) }}: ConfigMap variables not applied
* {{ k8spsjira(316) }}: MySQL should not be in read_only=true with single node
* {{ k8spsjira(317) }}: Remove mysql-shell and JSON field usage in reconciliation
* {{ k8spsjira(325) }}: pmm agent is failing in openshift with temp folder permission issue
* {{ k8spsjira(330) }}: Admin port does not work in case of async deployment with one pod only

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
0.7.0:

* [Google Kubernetes Engine (GKE) :octicons-link-external-16:](https://cloud.google.com/kubernetes-engine) 1.24 - 1.27
* [Amazon Elastic Container Service for Kubernetes (EKS) :octicons-link-external-16:](https://aws.amazon.com) 1.23 - 1.27
* [Minikube :octicons-link-external-16:](https://minikube.sigs.k8s.io/docs/) 1.31.2 (based on Kubernetes 1.27)

This list only includes the platforms that the Percona Operators are specifically tested on as part of the release process. Other Kubernetes flavors and versions depend on backward compatibility offered by Kubernetes itself.
