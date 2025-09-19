# Percona Operator for MySQL 0.12.0 ({{date.v0_12_0}})

[Installation](../System-Requirements.md#installation-guidelines){.md-button}

Percona Operator for MySQL allows users to deploy MySQL clusters with both asynchronous and group replication topology. This release includes various stability improvements and bug fixes, getting the Operator closer to the General Availability stage. Version 0.12.0 of the Percona Operator for MySQL is still **a tech preview release**, and it is **not recommended for production environments**. 

**As of today, we recommend using** [Percona Operator for MySQL based on Percona XtraDB Cluster](https://docs.percona.com/percona-operator-for-mysql/pxc/index.html), which is production-ready and contains everything you need to quickly and consistently deploy and scale MySQL clusters in a Kubernetes-based environment, on-premises or in the cloud.

## Release highlights

### Full MySQL 8.4 support now available

With this release, data-at-rest encryption is now supported for Percona Server for MySQL 8.4.

In the previous release, we have added support for Percona Server for MySQL 8.4 within the Operator. However, data-at-rest encryption was not yet available. That limitation has now been lifted, unlocking the full potential of Percona Server for MySQL’s latest major version. Check our [documentation](../encryption-setup.md) for Percona Server for MySQL 8.4-specific setup instructions.

This improvement empowers you to take full advantage of Percona Server for MySQL 8.4’s features while benefiting from seamless, automated lifecycle management provided by the Operator. Percona Server for MySQL 8.4 is now the default version for deploying a database cluster.

### Ensure cluster availability with PodDisruptionBudgets

A PodDisruptionBudget (PDB) in Kubernetes helps keep your applications available during voluntary disruptions, such as deleting a deployment or draining a node for maintenance. A PDB sets a limit on how many Pods can be unavailable at the same time due to these voluntary actions.

With this release, you can now configure PodDisruptionBudgets for MySQL, HAProxy, MySQL Router, and Orchestrator Pods, thus ensuring your cluster remains available, even during disruptions or planned maintenance.

### Fine-tune backup and restore operations

The Operator sets sensible defaults for backups and restores to ensure their smooth flow. If you need more control, you can fine-tune `xtrabackup`, `xbstream`, and `xbcloud` settings. You can do this globally via the `deploy/cr.yaml` Custom resource manifest or individually for a specific backup / restore operation via the respective `deploy/backup.yaml` or `deploy/restore.yaml` manifests. In either case, define your configuration in the `spec.containerOptions` subsection. For example:

```yaml
spec:
  backup:
    storages:
      <STORAGE-NAME>:
         containerOptions:
           env:
           - name: VERIFY_TLS
             value: "false"
           args:
             xtrabackup:
             - "--someflag=abc"
             xbcloud:
             - "--someflag=abc"
             xbstream:
             - "--someflag=abc"
```

Note that individual settings take precedence over the global ones. Read more about fine- tuning backups and restores and how the settings are applied in our [documentation](../backups-fine-tune.md)

### Monitor PMM Client health and status

Percona Monitoring and Management (PMM) is a great tool to monitor the health of your database cluster. Now you can also learn if PMM itself is healthy using probes - a Kubernetes diagnostics mechanism to check the health and status of containers. Use the spec.pmm.readinessProbes.*and spec.pmm.livenessProbes.* Custom Resource options to fine-tune Readiness and Liveness probes for PMM Client.

### Define a source Pod for backups

You can now explicitly define from what MySQL instance Pod the Operator should make a backup. You can specify the Pod in the deploy/cr.yaml to apply it for all backups, both scheduled and on-demand. You can also override it for an on-demand backup in its resource manifest.

```yaml
spec:
  backup:
      sourcePod: ps-cluster1-mysql-1
```

These options let you tailor your backup strategy to fit your organization's policies.

For asynchronous replication clusters, the Operator must know the cluster topology to run a backup. For this, either enable the Orchestrator in your deployment. Or specify the `backupPod`, if your cluster has more than one MySQL Pods. 


## Deprecation, rename and removal

* The `.spec.initImage` field has been replaced by the `.spec.initContainer` subsection, which follows Kubernetes best practices for defining containers that run before the main containers in a Pod. The `initContainer` feature is helpful for setup tasks such as:

   - Initializing data
   - Waiting for services to become available
   - Setting permissions
   - Pulling secrets or configuration files

* The default cluster name has been changed to `ps-cluster1` to prevent possible conflicts if you have custom resources of both Percona Operator for MySQL based on Percona Server for MySQL and Percona XtraDB Cluster in the same namespace.

## Changelog

### New features

* [K8SPS-400](https://perconadev.atlassian.net/browse/K8SPS-400) - Improved flexibility for backups and restores via adding support for custom options for `xtrabackup`, `xbstream`, and `xbcloud` binaries.

* [K8SPS-405](https://perconadev.atlassian.net/browse/K8SPS-405) - Users can now configure the LivenessProbe for the PMM Client container, allowing for custom timeouts and improved container health checks.

* [K8SPS-413](https://perconadev.atlassian.net/browse/K8SPS-413) - Add ability to set  resources and `containerSecurityContext` for init containers.

* [K8SPS-480](https://perconadev.atlassian.net/browse/K8SPS-480) - Added support for data-at-rest encryption for MySQL 8.4.

### Improvements

* [K8SPS-172](https://perconadev.atlassian.net/browse/K8SPS-172) - The operator now includes logs for all haproxy manipulations, providing better visibility for operations like adding, deleting, or downscaling.

* [K8SPS-269](https://perconadev.atlassian.net/browse/K8SPS-269) - All Kubernetes objects created by the Operator now have appropriate labels, including the Orchestrator configmap in async clusters. This improves object filtering and grouping.

* [K8SPS-417](https://perconadev.atlassian.net/browse/K8SPS-417) - Added ability to define PodDisruptionBudget, which helps manage voluntary disruptions to your cluster.

* [K8SPS-427](https://perconadev.atlassian.net/browse/K8SPS-427) - Simplified the Custom Resource (CR) validation logic by using Kubernetes validations for CR input.

* [K8SPS-464](https://perconadev.atlassian.net/browse/K8SPS-464) - The Operator will now automatically set the `crVersion` to the Operator's current version if it is not defined by the user.

* [K8SPS-466](https://perconadev.atlassian.net/browse/K8SPS-466) - Added ability to set global labels and annotations for all Kubernetes objects created by the Operator.

* [K8SPS-478](https://perconadev.atlassian.net/browse/K8SPS-478) - Improved bootstrapper behavior to determine if incremental recovery is possible and specify it when adding new instances to the existing cluster.

### Bugs fixed

* [K8SPS-371](https://perconadev.atlassian.net/browse/K8SPS-371) - Added the ability to set a backup source Pod to ensure backups are made for clusters with asynchronous replication when the Orchestrator is disabled.

* [K8SPS-374](https://perconadev.atlassian.net/browse/K8SPS-374) - Fixed the issue with the Operator reporting the reconciliation error when an async cluster was being paused or recovered.

* [K8SPS-378](https://perconadev.atlassian.net/browse/K8SPS-378) - Fixed an issue where the cluster would remain in an unready state if the Orchestrator was scaled down to 1 Pod.

* [K8SPS-430](https://perconadev.atlassian.net/browse/K8SPS-430) - The Operator now updates TLS certificates when new Subject Alternative Names (SANs) are added to the CR.

* [K8SPS-465](https://perconadev.atlassian.net/browse/K8SPS-465) - Readiness and liveness probes have been added for HAProxy Pods to ensure their health.

* [K8SPS-475](https://perconadev.atlassian.net/browse/K8SPS-475) - Fixed an issue where the `exposePrimary.labels` field was incorrectly applied to the service selector. The exposed services now contain global labels together with the exposed labels and the selectors do not contain labels.

* [K8SPS-494](https://perconadev.atlassian.net/browse/K8SPS-494) - Fixed the issue with the constant update of the `resourceVersion` of the PerconaServerMySQL object after a cluster is created. The issue was caused by the Operator receiving stale objects during reconciliation, which resulted in the `InnoDBClusterBootstrapped` condition being set twice in every loop and constantly updating its last transition time. The Fix updates the status directly after setting the condition and waits for consistency with the API server.

## Supported software

--8<-- [start:software]

The Operator was developed and tested with the following software:

* Percona Server for MySQL 8.4.6-6
* Percona Server for MySQL 8.0.43-34
* XtraBackup 8.4.0-4
* XtraBackup 8.0.35-34
* MySQL Router 8.4.6-6
* MySQL Router 8.0.43-34
* HAProxy 2.8.15-1
* Orchestrator 3.2.6-18
* Percona Toolkit 3.7.0-2
* PMM Client 3.4.0
* Cert Manager 1.18.2

Other options may also work but have not been tested.

--8<-- [end:software]

## Supported platforms

Percona Operators are designed for compatibility with all [CNCF-certified :octicons-link-external-16:](https://www.cncf.io/training/certification/software-conformance/) Kubernetes distributions. Our release process includes targeted testing and validation on major cloud provider platforms and OpenShift, as detailed below for Operator version 0.9.0:

--8<-- [start:platforms]

* [Google Kubernetes Engine (GKE) :octicons-link-external-16:](https://cloud.google.com/kubernetes-engine) 1.30 - 1.33
* [Amazon Elastic Container Service for Kubernetes (EKS) :octicons-link-external-16:](https://aws.amazon.com) 1.31 - 1.33
* [OpenShift :octicons-link-external-16:](https://www.openshift.com) 4.15 - 4.19
* [Minikube :octicons-link-external-16:](https://minikube.sigs.k8s.io/docs/) 1.37.0 (based on Kubernetes 1.34.0)

--8<-- [end:platforms]

This list only includes the platforms that the Percona Operators are specifically tested on as part of the release process. Other Kubernetes flavors and versions depend on backward compatibility offered by Kubernetes itself.

## Percona certified images

Find Percona's certified Docker images that you can use with Percona Operator for MySQL based on Percona Server for MySQL in the following table:

--8<-- [start:images]

Image                                                    | Digest                                                           |
|:---------------------------------------------------------|:-----------------------------------------------------------------|
| percona/percona-server-mysql-operator:0.12.0             | a9d073efaee64250c7a97210232373909c951d0d6da3d67d68b36a212b5e5a5b |
| percona/percona-server-mysql-operator:0.12.0 (ARM64)     | cb704b34cff91fd44e897d4aed0379ffb5c970625e8e5ecd7ffec2b12b0e5897 |
| percona/percona-mysql-router:8.4.6                       | 5b714f768c4cea30e85b31de7ab3958074814e8ccfbcad61db5109d3d80710b3 |
| percona/percona-mysql-router:8.0.43                      | 00047362aec0ee988e32f7133d41b723928a6ac98d38dcd10c18ca99e2718a53 |
| percona/percona-orchestrator:3.2.6-18                    | 6fa4c515363c2a89a13accb0a58ba66519329afc04ad31c400775ced96bc8c09 |
| percona/percona-toolkit:3.7.0-2                          | 17ef2b69a97fa546d1f925c74ca09587ac215085c392761bb4d51f188baa6c0e |
| percona/haproxy:2.8.15                                   | e64e468ac0ed2036ee164631469cc71821dcb84a6d568883f704d0eacaf84bb4 |
| percona/percona-xtrabackup:8.4.0-4.1                     | f9e859ffbc6a9db1b1e3c72a8545cfcb0c9d70271c3c3273007d033fed3772a6 |
| percona/percona-xtrabackup:8.0.35-34.1                   | 2dc127b08971051296d421b22aa861bb0330cf702b4b0246ae31053b0f01911e |
| percona/percona-server:8.4.6-6.1                         | dd0c67df12f5b13eac441dfa27b04a49ac449b6946adf100bc1ecebffd8074f4 |
| percona/percona-server:8.4.5-5                           | 61a6811372d919316640990922188005f92d58639a2472865d59e56b2a6050a1 |
| percona/percona-server:8.0.43-34.1                       | d8a03675a2dd5d01a36ab0fe1c942091679bce90a241fb539cd31776ebf43aca |
| percona/percona-server:8.0.42-33                         | a7cbaa50c43483a07506f7cd5cccc4e587611f6500e1be5df0a93e339b9d3bc5 |
| percona/percona-server:8.0.40-31                         | 09276abecbc7c38ce9c5453da1728f3e7d81722c56e2837574ace3a021ee92f2 |
| percona/percona-server:8.0.36-28                         | 423acd206f94b34288d10ed041c3ba42543e26e44f3706621320504a010dd41f |
| percona/percona-server:8.0.33-25                         | 14ef81039f2dfa5e19a9bf20e39aaf367aae4370db70899bc5217118d6fd2171 |
| percona/pmm-client:3.4.0                                 | 9e8bf020be35eddc2a9e3a22e974234ce02c4818353e87e0522191df2743af3c |
| percona/pmm-client:3.4.0 (ARM64)                         | 1f3e19db0a409e92ccd5238893000f4340bc309a44ebdc2a78eedf4d7948c766 |


--8<-- [end:images]

[Find images for previous versions :octicons-link-external-16:](https://docs.percona.com/legacy-documentation/){.md-button}
