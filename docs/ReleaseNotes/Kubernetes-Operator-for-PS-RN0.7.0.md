# *Percona Operator for MySQL* 0.7.0

* **Date**

    March 25, 2024

* **Installation**

    [Installing Percona Operator for MySQL](../System-Requirements.md#installation-guidelines)

Percona Operator for MySQL allows users to deploy MySQL clusters with both asynchronous and group replication topology. This release includes various stability improvements and bug fixes, getting the Operator closer to the General Availability stage. Version 0.7.0 of the Percona Operator for MySQL is still **a tech preview release** and it is **not recommended for production environments**. **As of today, we recommend using** [Percona Operator for MySQL based on Percona XtraDB Cluster](https://docs.percona.com/percona-operator-for-mysql/pxc/index.html), which is production-ready and contains everything you need to quickly and consistently deploy and scale MySQL clusters in a Kubernetes-based environment, on-premises or in the cloud.

## Highlights

### Documentation improvements

Within this release, a [Quickstart guide](../quickstart.md) was added to the Operator docs, that’ll set you up and running in no time! Taking a look at this guide you’ll be guided step by step through quick installation (multiple options), connecting to the database, inserting data, making a backup, and even integrating with Percona Monitoring and Management (PMM) to monitor your cluster.

### Fine-tuning backups

This release brings a number of improvements for backups, making them more stable and robust. The new [backup.backoffLimit](../operator.md#backup-backofflimit) Custom Resource option allows customizing the number of attempts the Operator should take to create the backup (the default is making 6 retries after the first backup attempt fails for some reason, such as faulty network connection or the cloud outage). Also, the Operator now makes a number of checks before starting the restore process to make sure that there are needed cloud credentials and the actual backup. This allows to avoid faulty restore that would leave the database cluster in non-functional state.

### Other improvements

With our latest release, we put an all-hands-on-deck approach towards fine-tuning the Operator with code refactoring and a number of minor improvements, along with addressing key bugs reported by the community. We are extremely grateful to each and every person who submitted feedback and contributed to help us get to the bottom of these pesky issues.

## New features

* {{ k8spsjira(275) }}: The Operator now checks if the needed Secrets exist and connects to the storage to check the existence of a backup before starting the restore process
* {{ k8spsjira(277) }}: The new `topologySpreadConstraints` Custom Resource option allows to use [Pod Topology Spread Constraints :octicons-link-external-16:](https://kubernetes.io/docs/concepts/workloads/pods/pod-topology-spread-constraints/#spread-constraints-for-pods) to achieve even distribution of Pods across the Kubernetes cluster

## Improvements

* {{ k8spsjira(129) }}: The documentation on how to build and test the Operator [is now available :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/main/e2e-tests/README.md)
* {{ k8spsjira(295) }}: Certificate issuer errors are now reflected in the Custom Resource status message and can be easily checked with the `kubectl get ps -o yaml` command
* {{ k8spsjira(326) }}: The mysql-monit Orchestrator sidecar container now inherits orchestrator resources following the way that HAProxy mysql-monit container does (thanks to SlavaUtesinov for contribution)

## Bugs Fixed

* {{ k8spsjira(124) }}: Parametrize the number of attempts the Operator should make for backup through a [Custom Resource option](../operator.md#backup-backofflimit)
* {{ k8spsjira(146) }}: Log messages were incorrectly mentioning semi-synchronous replication regardless of the actual replication type
* {{ k8spsjira(173) }}: Fix a bug due to which the Operator was silently resetting a component size to the minimum size allowed when `allowUnsafeConfig` was turned off, without any messages in the log
* {{ k8spsjira(185) }}: Fix a bug due to which the Orchestrator-MySQL (topology instances) connections were not encrypted
* {{ k8spsjira(256) }}: Fix a bug which caused logging the SQL statements, potentially printing sensitive information in the logs
* {{ k8spsjira(258) }}: If two backups were created at the same time, both of them were set to the “Running” state, while only one of them was actually running and the other one was waiting
* {{ k8spsjira(291) }}: Fix a bug due to which instances were not actually removed when scaling down the group replication cluster
* {{ k8spsjira(302) }}: Fix a bug where HAProxy, Orchestrator, and MySQL (if exposed) Services were deleted when just pausing the cluster
* {{ k8spsjira(303) }}: Fix a bug where ports 6033 (the default one for ProxySQL) for MySQL and port 33060 for Router were missing in appropriate Services
* {{ k8spsjira(311) }}: The Operator was setting the restore state to `Error` instead of leaving it empty if the other restore was already running, which could cause it to continue later, not desirable in situations of accidental running two restores
* {{ k8spsjira(312) }}: Fix a bug where Pods did not restart if the cluster1-ssl secret was deleted and recreated by cert manager, so the change of certificates did not take effect
* {{ k8spsjira(315) }}: ConfigMap with custom configuration specifying something different than my.cnf as config name was silently not applied without error message
* {{ k8spsjira(316) }}: Fix a bug where MySQL was started in `read_only=true` mode in case of a single instance database cluster configuration (thanks to Kilian Ries for report)
* {{ k8spsjira(330) }}: Fix a bug due to which the admin port did not work in case of asynchronous replication cluster with one Pod only

## Supported Platforms

The Operator was developed and tested with Percona Server for MySQL 8.0.36-28.
Other options may also work but have not been tested. Other software components include:

* Orchestrator 3.2.6-12
* MySQL Router 8.0.36
* XtraBackup 8.0.35-30
* Percona Toolkit 3.5.7
* HAProxy 2.8.5
* PMM Client 2.41.1

The following platforms were tested and are officially supported by the Operator
0.7.0:

* [Google Kubernetes Engine (GKE) :octicons-link-external-16:](https://cloud.google.com/kubernetes-engine) 1.26 - 1.29
* [Amazon Elastic Container Service for Kubernetes (EKS) :octicons-link-external-16:](https://aws.amazon.com) 1.25 - 1.29
* [Minikube :octicons-link-external-16:](https://minikube.sigs.k8s.io/docs/) 1.32

This list only includes the platforms that the Percona Operators are specifically tested on as part of the release process. Other Kubernetes flavors and versions depend on backward compatibility offered by Kubernetes itself.
