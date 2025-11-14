# Percona Operator for MySQL 0.10.0 ({{date.v0_10_0}})

[Installation](../System-Requirements.md#installation-guidelines){.md-button}

Percona Operator for MySQL allows users to deploy MySQL clusters with both asynchronous and group replication topology. This release includes various stability improvements and bug fixes, getting the Operator closer to the General Availability stage. Version 0.10.0 of the Percona Operator for MySQL is still **a tech preview release**, and it is **not recommended for production environments**. 

**As of today, we recommend using** [Percona Operator for MySQL based on Percona XtraDB Cluster](https://docs.percona.com/percona-operator-for-mysql/pxc/index.html), which is production-ready and contains everything you need to quickly and consistently deploy and scale MySQL clusters in a Kubernetes-based environment, on-premises or in the cloud.

## Release highlights

### PMM3 support

The Operator is natively integrated with PMM 3, enabling you to monitor the health and performance of your Percona Server MySQL deployment and at the same time enjoy enhanced performance, new features, and improved security that PMM 3 provides.

Note that the support for PMM2 is dropped. This means you must do the following to monitor your deployment further:

* transition to PMM 3 if you had PMM 2 to. The PMM documentation explains how to upgrade.
* run the Operator version 0.10.0. Check the [Upgrade the Operator](../update-operator.md) tutorial for the update steps.
* ensure that PMM 3 Server version must be equal to or newer than the PMM Client.

### Support for deployments on OpenShift

OpenShift is a fully integrated Kubernetes-based platform enhanced with automation, security, and developer-friendly tools. You can now deploy Percona Operator for MySQL based on Percona Server for MySQL on OpenShift and benefit from its portability across hybrid clouds. The Operator also fully supports the Red Hat OpenShift lifecycle which ensures its security and reliability.

Follow our [installation guide](../openshift.md) to install the Operator on OpenShift.

### Added labels to identify the version of the Operator

CRD is compatible with the last 3 Operator versions. To know which Operator version is attached to it, we've added lables to all Custom Resource Definitions. The labels help you identify the current Operator version and decide if you need to update the CRD.

To view the labels, run: `kubectl get crd perconaservermysqls.ps.percona.com --show-labels`

### Improved configuration validation during cluster deployment

The Operator now enforces these mandatory parameters to have values when it deploys the database cluster:

* `.spec.mysql.size`
* `.spec.proxy.haproxy.size`
* `.spec.proxy.router.size`
* `.spec.orchestrator.size`
* `.spec.backup.pitr.binlogServer.size`

If any of the following configuration options are empty, the deployment fails.

This improved validation ensures that every cluster is deployed with the necessary settings for stability and functionality.  

## Changelog

### New features

* [K8SPS-393](https://perconadev.atlassian.net/browse/K8SPS-393) - Added support for PMM v3

* [K8SPS-110](https://perconadev.atlassian.net/browse/K8SPS-110) - Added support for OpenShift

### Improvements

* [K8SPS-135](https://perconadev.atlassian.net/browse/K8SPS-135) - Use MD5 hashing for stored configuration

* [K8SPS-320](https://perconadev.atlassian.net/browse/K8SPS-320) - Added labels to TLS and user secret objects created by the Operator

* [K8SPS-357](https://perconadev.atlassian.net/browse/K8SPS-357), [K8SPS-423](https://perconadev.atlassian.net/browse/K8SPS-423) - Added the `state-monitor` utility to read MySQL state during startup. It is a valuable tool to improve cluster provisioning

* [K8SPS-382](https://perconadev.atlassian.net/browse/K8SPS-382) - Removed the `loadBalancerIP` Service type as deprecated

* [K8SPS-392](https://perconadev.atlassian.net/browse/K8SPS-392) - Added the ability to increase timeout for the CLONE operation while bootstrapping a cluster (Thank you Alexander Kuleshov for reporting this issue)

* [K8SPS-426](https://perconadev.atlassian.net/browse/K8SPS-426) - Added Labels for Custom Resource Definitions (CRD) to identify the Operator version attached to them

## Bugs Fixed

* [K8SPS-212](https://perconadev.atlassian.net/browse/K8SPS-212) - Improved the Custom Resource validation during a cluster deployment when the `.mysql.clusterType` is set to `async`. The validation rules verify that HAProxy and Orchestrator are enabled, while MySQL Router is disabled for async deployments. The corresponding log message is also printed. This helps ensure your cluster is configured according to the requirements for this replication type. 

* [K8SPS-221](https://perconadev.atlassian.net/browse/K8SPS-221) - Fixed a bug with bootstrapping the cluster after crash when the `clusterType` is set to `group-replication`. The fix uses the `state-monitor` utility that checks MySQL state and proceeds with bootstrappins based on the database state. 

* [K8SPS-299](https://perconadev.atlassian.net/browse/K8SPS-299) - Fixed the issue with the Operator failing to initialize the cluster when the size for MySQL is absent in Custom Resource manifest by making the parameters that affect cluster operation mandatory for deployment. If any option has no value, the Operator fails to deploy the cluster 

* [K8SPS-365](https://perconadev.atlassian.net/browse/K8SPS-365) - Fixed the issue with `clusterType` set to `group-replication` failing after the upgrade of the MySQL image. The issue was fixed by removing the excessive restart of the `mysql` container after adding a pod to the cluster. 

* [K8SPS-375](https://perconadev.atlassian.net/browse/K8SPS-375) - Improved the cluster startup process by handling reconciling errors 

* [K8SPS-379](https://perconadev.atlassian.net/browse/K8SPS-379) - Automated the ClusterRole generation when installing the Operator in a cluster-wide mode


* [K8SPS-387](https://perconadev.atlassian.net/browse/K8SPS-387) - Added the `wait_for_delete` function to ensure that the cluster or its components are fully cleaned up before performing operations like restoration, scaling, or re-deployment.

## Deprecation and removal

The `loadBalancerIP` type for the Service objects is deprecated in Kubernetes v1.24+. It is removed from the HAProxy and Router subsections of the `deploy/cr.yaml` Custom Resource manifest. Please refer to [Kubernetes documentation :octicons-link-external-16:](https://kubernetes.io/docs/concepts/services-networking/service/#loadbalancer) for recommendations how to proceed if you have defined this type before.

## Supported software

--8<-- [start:software]

The Operator was developed and tested with the following software: 

* Percona Server for MySQL 8.0.42-33
* Orchestrator 3.2.6-17
* MySQL Router 8.0.42
* XtraBackup 8.0.35-33
* Percona Toolkit 3.7.0
* HAProxy 2.8.14
* PMM Client 3.2.0

Other options may also work but have not been tested. 

--8<-- [end:software]

## Supported platforms

Percona Operators are designed for compatibility with all [CNCF-certified :octicons-link-external-16:](https://www.cncf.io/training/certification/software-conformance/) Kubernetes distributions. Our release process includes targeted testing and validation on major cloud provider platforms and OpenShift, as detailed below for Operator version 0.10.0:

--8<-- [start:platforms]

* [Google Kubernetes Engine (GKE) :octicons-link-external-16:](https://cloud.google.com/kubernetes-engine) 1.30 - 1.32
* [Amazon Elastic Container Service for Kubernetes (EKS) :octicons-link-external-16:](https://aws.amazon.com) 1.30 - 1.32
* [OpenShift :octicons-link-external-16:](https://www.openshift.com) 4.15 - 4.18
* [Minikube :octicons-link-external-16:](https://minikube.sigs.k8s.io/docs/) 1.36.0 (based on Kubernetes 1.33.0)

--8<-- [end:platforms]

This list only includes the platforms that the Percona Operators are specifically tested on as part of the release process. Other Kubernetes flavors and versions depend on backward compatibility offered by Kubernetes itself.

## Percona certified images

Find Percona's certified Docker images that you can use with Percona Operator for MySQL based on Percona Server for MySQL in the following table:

--8<-- [start:images]

 Image                                                    | Digest                                                           |
|:---------------------------------------------------------|:-----------------------------------------------------------------|
| percona/percona-server-mysql-operator:0.10.0 (x86_64)     | 406cf9b929eb42a158fc05d6bbde3435d2c46c7fed0a53889d82b335334e8df2 |
| percona/percona-server-mysql-operator:0.10.0 (ARM64)      | 0889abb9ef079efb164a1046393a5266cd30701fcd53c32db439a2ca93c6dceb |
| percona/percona-mysql-router:8.0.42                      | a6351fc5774086400f1d1dcf08f4f2d5975b97bc943d3dd98fb870e364066968 |
| percona/percona-orchestrator:3.2.6-17                    | c1871ddc6ff3eaca7bb03c3aa11db880ae02d623db1203d0858f8566f56ea5f7 |
| percona/percona-toolkit:3.7.0                            | 17ef2b69a97fa546d1f925c74ca09587ac215085c392761bb4d51f188baa6c0e |
| percona/haproxy:2.8.14                                   | 6de8c402d83b88dae7403c05183fd75100774defa887c05a57ec04bc25be2305 |
| percona/percona-xtrabackup:8.0.35-33                     | 57518571b4663ab492bbd2dc8369fea7e8d358b8e544ea8fa1c1eda12207b8e2 |
| percona/percona-server:8.0.42-33                         | e30ad4bd3729f6a1ab443341a0a9ce10bbe70cb80d14e5e24a25da4bae4305da |
| percona/percona-server:8.0.40-31                         | 09276abecbc7c38ce9c5453da1728f3e7d81722c56e2837574ace3a021ee92f2 |
| percona/percona-server:8.0.36-28                         | 423acd206f94b34288d10ed041c3ba42543e26e44f3706621320504a010dd41f |
| percona/percona-server:8.0.33-25                         | 14ef81039f2dfa5e19a9bf20e39aaf367aae4370db70899bc5217118d6fd2171 |
| percona/percona-server:8.0.32-24                         | 2107838f98d41172f37c7fc9689095e9ebd0a1af557b687396d92cf00f54ec3f |
| percona/pmm-client:3.2.0 (x86_64)                        | 7b1d1798b6446d6c3d5e4005fd9c07be9f4be5859ac2fae908be387cf7b0f50c |
| percona/pmm-client:3.2.0 (ARM64)                         | 1a36eb47e39dcd275c5ed62da8415c862e560933f48790bbf9b78f41cd3dfd10 |

--8<-- [end:images]

[Find images for previous versions :octicons-link-external-16:](https://docs.percona.com/legacy-documentation/){.md-button}
