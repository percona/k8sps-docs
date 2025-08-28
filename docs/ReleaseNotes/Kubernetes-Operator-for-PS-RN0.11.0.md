# Percona Operator for MySQL 0.11.0 ({{date.v0_11_0}})

[Installation](../System-Requirements.md#installation-guidelines){.md-button}

Percona Operator for MySQL allows users to deploy MySQL clusters with both asynchronous and group replication topology. This release includes various stability improvements and bug fixes, getting the Operator closer to the General Availability stage. Version 0.11.0 of the Percona Operator for MySQL is still **a tech preview release**, and it is **not recommended for production environments**. 

**As of today, we recommend using** [Percona Operator for MySQL based on Percona XtraDB Cluster](https://docs.percona.com/percona-operator-for-mysql/pxc/index.html), which is production-ready and contains everything you need to quickly and consistently deploy and scale MySQL clusters in a Kubernetes-based environment, on-premises or in the cloud.

## Release highlights

### Support for MySQL 8.4

This release introduces support for Percona Server for MySQL 8.4.x. The Operator supports all major functionality for this latest major version except data-at-rest encryption. However, we do not recommended Percona Server for MySQL 8.4 for production environments yet.

### Ensure data security with data at rest encryption

Data-at-rest encryption provides robust data protection by encrypting your database files on disk. Data is encrypted automatically, in real time, prior to writing to storage and decrypted when read from storage. The Operator uses the `keyring_vault` plugin to encrypt tablespace files and binlog. It integrates directly with HashiCorp Vault, giving you a secure and automated solution for managing encryption keys.

With this feature, you can meet your compliance requirements and protect sensitive data without the operational complexity. Learn how to configure it in our [documentation](../encryption.md)

Note that data-at-rest encryption is currently not supported for Percona Server for MySQL 8.4.x. We plan to add it in future releases.

### Support for `emptyDir` and `hostPath` volumes

You can now configure the Operator to use `emptyDir` or `hostPath` volumes for MySQL Pods, in addition to `persistentVolumeClaim` volumes. This extends the number of use cases for using the Operator, such as configuring additional storage for the data you don't need to persist when a Pod restarts, ephemeral workloads, testing CI/CD automation against a database and more.

Note the following key points for using volume types:

* Using `hostPath` can be risky in production, as it ties your Pod to a specific node and can lead to data loss if the node fails.
* `emptyDir` is not for persistent data.
* `persistentVolumeClaim` is the recommended way for persistent, portable storage in Kubernetes.

### Improved security for user secrets with special characters in passwords

The Operator now generates stronger passwords using the combination of uppercase and lowercase letters, digits, and special characters like `! $ % & ( ) * + , - . < = > ? @ [ ] ^ _ { } ~ #`. These have been tested to ensure compatibility across SQL queries, shell scripts, YAML files, and connection strings.

The Operator excludes problematic characters such as `’ “ \ / : | ;`.

When you create passwords for user secrets yourself, be sure to stick to the approved character set to ensure your services run smoothly.

### Customize connection to MySQL router via configurable ports

You can now modify existing ports for the MySQL router service, as well as add new custom ports. This ability enables you to fine-tune the connection to your Percona Server for MySQL cluster. For example, you can separate access to the database for different applications, so that each one connects to the same MySQL Router but gets a tailored experience based on the port.

### Automated volume resizing

Kubernetes supports the Persistent Volume expansion as a stable feature since v1.24. Using it with the Operator previously involved manual operations. Now this is automated, and users can resize their PVCs by just changing the value of the `resources.requests.storage` option in the PerconaServerMySQL custom resource.

## Deprecation, rename and removal

* `.spec.pmm.runtimeClassName` field has been removed from the `crd.yaml` and code because it wasn't being used
* `.spec.backup.imagePullSecrets` will now be applied to the backup and restore jobs
* `.spec.proxy.haproxy.runtimeClassName` will be applied to the haproxy pods
* `.spec.pmm.serverUser` is removed as not used in PMM3

## Changelog

### New features

* [K8SPS-126](https://perconadev.atlassian.net/browse/K8SPS-126) -  It is now possible to resize Persistent Volume Claims by patching the PerconaServerMySQL custom resource. Change `persistentVolumeClaim.resources.requests.storage` and let the Operator do the scaling.

* [K8SPS-421](https://perconadev.atlassian.net/browse/K8SPS-421) - Added data-at-rest encryption support

* [K8SPS-445](https://perconadev.atlassian.net/browse/K8SPS-445) - Added MySQL 8.4 support

### Improvements

* [K8SPS-437](https://perconadev.atlassian.net/browse/K8SPS-437) - Removed the `spec.pmm.serverUser` field as not used in PMM 3

* [K8SPS-406](https://perconadev.atlassian.net/browse/K8SPS-406) - Added possibility of adding custom parameters for PMM client via Custom Resource

* [K8SPS-131](https://perconadev.atlassian.net/browse/K8SPS-131) - Improve connection configuration by making router ports configurable

* [K8SPS-265](https://perconadev.atlassian.net/browse/K8SPS-265) - Added special symbols support in passwords

* [K8SPS-319](https://perconadev.atlassian.net/browse/K8SPS-319) - Improve labels by adding MySQL to the Operator name

* [K8SPS-323](https://perconadev.atlassian.net/browse/K8SPS-323) - Added support for primary Pod discovery through a Kubernetes Service (Thank you Marjus Cako for reporting this issue)

* [K8SPS-336](https://perconadev.atlassian.net/browse/K8SPS-336) - Added the ability to deploy the Operator with `hostPath` and `emptyDir` volume types

* [K8SPS-357](https://perconadev.atlassian.net/browse/K8SPS-357) - Improved cluster provisioning

* [K8SPS-401](https://perconadev.atlassian.net/browse/K8SPS-401) - Added examples of setting up backups on Azure into our CRs

* [K8SPS-418](https://perconadev.atlassian.net/browse/K8SPS-418) - Added the ability to specify the time for the Pod to shut down gracefully after receiving a termination signal before it is forcefully killed.

* [K8SPS-414](https://perconadev.atlassian.net/browse/K8SPS-414) - Added the ability to configure imagePullSecrets via the Custom Resource

* [K8SPS-415](https://perconadev.atlassian.net/browse/K8SPS-415) - Added the ability to configure runtimeClassName via the Custom Resource

* [K8SPS-416](https://perconadev.atlassian.net/browse/K8SPS-416) - Added the ability to configure tolerations via the Custom Resource

## Bugs Fixed

* [K8SPS-287](https://perconadev.atlassian.net/browse/K8SPS-287) - Improved logging to include information about `allowUnsafeConfigurations` not set when a user tries to scale down a cluster to less than 3 Pods

* [K8SPS-298](https://perconadev.atlassian.net/browse/K8SPS-298) - Added an error to the logs about invalid configuration for deploying a cluster with asynchronous replication without a proxy.

* [K8SPS-308](https://perconadev.atlassian.net/browse/K8SPS-308) - Fixed the issue with smart update reporting errors for the cluster with async replication

* [K8SPS-381](https://perconadev.atlassian.net/browse/K8SPS-381) - Improved restores from Azure blob storage by removing a hardcoded slash

* [K8SPS-394](https://perconadev.atlassian.net/browse/K8SPS-394) - Improved the cluster behavior when a user tries to change a replication type on a running cluster. The cluster  fails because this operation is not allowed on a running cluster. Added documentation with the recommended steps.

* [K8SPS-396](https://perconadev.atlassian.net/browse/K8SPS-396) - Improved the gr-self-healing tests by replacing assert with readiness check for chaos-daemon

* [K8SPS-425](https://perconadev.atlassian.net/browse/K8SPS-425) - Fixed the cluster boootstrap process for a group replication clusters with MySQL 8.4

## Supported software

--8<-- [start:software]

The Operator was developed and tested with the following software:

* Percona Server for MySQL 8.4.5-5
* Percona Server for MySQL 8.0.42-33
* XtraBackup 8.4.0-3
* XtraBackup 8.0.35-33
* MySQL Router 8.4.5-5
* MySQL Router 8.0.42
* HAProxy 2.8.15
* Orchestrator 3.2.6-17
* Percona Toolkit 3.7.0
* PMM Client 3.3.1
* Cert Manager 1.18.2

Other options may also work but have not been tested.

--8<-- [end:software]

## Supported platforms

Percona Operators are designed for compatibility with all [CNCF-certified :octicons-link-external-16:](https://www.cncf.io/training/certification/software-conformance/) Kubernetes distributions. Our release process includes targeted testing and validation on major cloud provider platforms and OpenShift, as detailed below for Operator version 0.9.0:

--8<-- [start:platforms]

* [Google Kubernetes Engine (GKE) :octicons-link-external-16:](https://cloud.google.com/kubernetes-engine) 1.31 - 1.33
* [Amazon Elastic Container Service for Kubernetes (EKS) :octicons-link-external-16:](https://aws.amazon.com) 1.31 - 1.33
* [OpenShift :octicons-link-external-16:](https://www.openshift.com) 4.15 - 4.19
* [Minikube :octicons-link-external-16:](https://minikube.sigs.k8s.io/docs/) 1.36.0 (based on Kubernetes 1.33.1)

--8<-- [end:platforms]

This list only includes the platforms that the Percona Operators are specifically tested on as part of the release process. Other Kubernetes flavors and versions depend on backward compatibility offered by Kubernetes itself.

## Percona certified images

Find Percona's certified Docker images that you can use with Percona Operator for MySQL based on Percona Server for MySQL in the following table:

--8<-- [start:images]

 Image                                                    | Digest                                                           |
|:---------------------------------------------------------|:-----------------------------------------------------------------|
| percona/percona-server-mysql-operator:0.11.0             | 3068b1a4d81b5da7676e071040d3b44ff9fec5532cbfabb17f9c7612e8c9d35d |
| percona/percona-server-mysql-operator:0.11.0 (ARM64)     | b50f215869ca3d9f6a52561171851e8ffa033ca30d0276556e220ad448418b61 |
| percona/percona-mysql-router:8.4.5                       | e890ecc49c297cc8882b54ba457ff4d25da896cb11269989fa072aa338d620c1 |
| percona/percona-mysql-router:8.0.42                      | 2364ebb010cc94d7873367e06ad2fadba44f37b81fc78febf3f58a9e61fa5948 |
| percona/percona-orchestrator:3.2.6-17                    | c1871ddc6ff3eaca7bb03c3aa11db880ae02d623db1203d0858f8566f56ea5f7 |
| percona/percona-toolkit:3.7.0                            | 17ef2b69a97fa546d1f925c74ca09587ac215085c392761bb4d51f188baa6c0e |
| percona/haproxy:2.8.15                                   | 49e6987a1c8b27e9111ae1f1168dd51f2840eb6d939ffc157358f0f259819006 |
| percona/percona-xtrabackup:8.4.0-3                       | 01071522753ad94e11a897859bba4713316d08e493e23555c0094d68da223730 |
| percona/percona-xtrabackup:8.0.35-33                     | ae56852f0343726409633268cf8c6af92754ea2b5aacbecbec93fa980f8e724d |
| percona/percona-server:8.4.5-5                           | 9628b1e598c0ec13c2a6b834caa1642bf77f2b4a2d7620b1ba2d8aaf2b708133 |
| percona/percona-server:8.0.42-33                         | a7cbaa50c43483a07506f7cd5cccc4e587611f6500e1be5df0a93e339b9d3bc5 |
| percona/percona-server:8.0.40-31                         | 09276abecbc7c38ce9c5453da1728f3e7d81722c56e2837574ace3a021ee92f2 |
| percona/percona-server:8.0.36-28                         | 423acd206f94b34288d10ed041c3ba42543e26e44f3706621320504a010dd41f |
| percona/percona-server:8.0.33-25                         | 14ef81039f2dfa5e19a9bf20e39aaf367aae4370db70899bc5217118d6fd2171 |
| percona/percona-server:8.0.32-24                         | 2107838f98d41172f37c7fc9689095e9ebd0a1af557b687396d92cf00f54ec3f |
| percona/pmm-client:3.3.1                                 | 29a9bb1c69fef8bedc4d4a9ed0ae8224a8623fd3eb8676ef40b13fd044188cb4 |
| percona/pmm-client:3.3.1 (ARM64)                         | 50bccba4cb2c33bd3f6c5e37553bb70345de3f328b23a64ecfa63893f9025c83 |


--8<-- [end:images]

[Find images for previous versions :octicons-link-external-16:](https://docs.percona.com/legacy-documentation/){.md-button}
