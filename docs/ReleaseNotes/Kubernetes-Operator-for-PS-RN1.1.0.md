# Percona Operator for MySQL 1.1.0 ({{date.1_1_0}})

[Installation](../System-Requirements.md#installation-guidelines){.md-button}

Percona Operator for MySQL brings production-grade automation to MySQL deployments on Kubernetes. It handles provisioning, scaling, backups, failover, and upgrades using declarative Custom Resources, thus reducing manual effort and human error. With built-in support for Percona XtraBackup, proxies such as HAProxy or MySQL Router and Percona Toolkit, it ensures resilient, secure, and performant MySQL clusters.

## Release highlights

This release focuses on backups improvements enabling more efficient and flexible data protection strategies. It also includes a handful of improvements and bug fixes.  

### Point-in-time recovery (tech preview)

This release introduces point-in-time recovery, giving you precise control over how far back you restore your MySQL cluster. Instead of recovering only to the moment a backup was taken, you can now roll the database forward to a specific transaction or timestamp. This is invaluable when you need to undo a bad migration, recover right before someone dropped the wrong table, or meet tighter RPO requirements with minimal data loss.

Point-in-time recovery works the same way in both asynchronous and group replication clusters, ensuring consistent recovery behavior regardless of your topology. It uses the Percona Binlog Server to collect binary logs and the `mysqlbinlog` client to apply them during the restore. Read more about the workflow in our [documentation](../backups-pitr.md)

Point-in-time recovery is released as a **tech preview**. We do not recommend using it in production environments yet. However, we strongly encourage you to try it out in staging or test clusters and share your feedback. Your input will directly shape how we refine and finalize this capability in future releases.

### Incremental backups (tech preview)

This release introduces incremental backups for MySQL clusters, giving you a faster, more efficient, and more cost effective way to protect your data. Instead of creating a full backup every time, the Operator now captures only the changes since the previous backup, significantly reducing backup size, storage usage, and data transfer overhead. Incremental backups also lower the load on your cluster, helping you maintain performance even during frequent backup operations. This feature works seamlessly with all [supported backup storages](../backups-storage.md) and integrates with both [scheduled](../backups-scheduled.md) and [on-demand](../backups-ondemand.md) backup jobs.

Incremental backups are released as a **tech preview** feature and we don't recommend them for production environments yet. However, we encourage you to try them out and leave your feedback. This will help us shape the future of this functionality.

Learn more about incremental backups in our [documentation](../backups-incremental.md)

### Backup compression

Percona Operator for MySQL now supports backup compression, giving you faster, lighter, and more cost efficient backups.

Compressed backups are smaller in size, which means they stream to object storage quicker and consume less storage space as compared to uncompressed ones. In practice, this reduces both storage and data transfer costs.

Compression works for full and [incremental backups](#incremental-backups-tech-preview), and you can use it for both on demand and scheduled backup workflows. Configure compression globally or per backup storage directly in the Custom Resource . You can also override the compression algorithm for a specific on-demand backup. 

During the restore, the Operator automatically detects whether a backup is compressed and decompresses it as part of the restore workflow, so no additional steps are required from you.

Currently the Operator supports only the `zstd` compression algorithm. There is a known limitation for the `lz4` compression algorithm and it will be lifted after the [PXB-3568](https://perconadev.atlassian.net/browse/PXB-3568) is resolved.

To learn more about compressed backups, read our [documentation](../backups-compressed.md).

### Configure file descriptor limit for HAProxy

When HAProxy performs external MySQL health checks, it tries to close every file descriptor (FD) up to the system limit before executing the check script. Some systems set this limit extremely high, so HAProxy ends up looping through millions or even billions of numbers. This causes heavy CPU use, long delays and timeouts.

This release sets a safe file descriptor limit in the entrypoint script before HAProxy container starts. The default FD limit value is `1048576`. 

You can change this limit with the `HA_RLIMIT_NOFILE` environment variable in the Custom Resource. The value is checked, and if it is invalid, the Operator falls back to the default value. If the value is too large, the Operator uses the   hard limit file descriptor value. This makes external checks fast, stable, and predictable.

### Configurable reconnect attempts for clusters with asynchronous replication

In some cases, the default number of attempts for a replica to reconnect to its source is not sufficient, causing the cluster to become stuck. You can now fine-tune this behavior using the following environment variables:

* `ASYNC_SOURCE_RETRY_COUNT` - controls the number of reconnection attempts
* `ASYNC_SOURCE_CONNECT_RETRY` - adjusts the reconnect timeout for MySQL Pods
  
Specify new values directly in the Custom Resource to match your environment’s needs. 

Read more about other environment variables in our [documentation](../env-vars-custom.md)

This makes cluster management more predictable and avoids unexpected stalls during replication interruptions.

### Documentation updates

* Completed the install on Openshift documentation with instructions how to install using OLM
* Added a tutorial how to upgrade the Operator on OpenShift
* Enhanced Helm install documentation explaining how to install the Operator with customized parameters and apply custom naming to releases

## CRD changes

* The `.status.storage.s3.storageClass` has now the type `string`
* The `v1.^.status.storage.s3.storageClass` field is removed
* Added the `incrementalBaseBackupName` option. This option can be set only when the backup configuration has `spec.type` set to `incremental`, and its value must refer to an existing full backup.

## Changelog

### New features

* [K8SPS-410](https://perconadev.atlassian.net/browse/K8SPS-410) - Added the ability to make incremental backups to save only the changes since the previous backup.

* [K8SPS-642](https://perconadev.atlassian.net/browse/K8SPS-642) - Introduced Point-in-Time Recovery (PITR) support for enhanced data protection. This feature enables the binlog server to collect binary logs, allowing users to restore their database to any specific timestamp.

### Improvements

* [K8SPS-69](https://perconadev.atlassian.net/browse/K8SPS-69) - Updated the readiness probe to fail if replication threads have stopped. This prevents application traffic from being routed to nodes that are no longer receiving updates from the primary.

* [K8SPS-96](https://perconadev.atlassian.net/browse/K8SPS-96) - Added support for backup compression using Percona XtraBackup. This enhancement significantly reduces the storage footprint and transfer time for all database backups.

* [K8SPS-215](https://perconadev.atlassian.net/browse/K8SPS-215) - Improved restoration logic by automatically removing unnecessary PVCs during asynchronous replication restores. This ensures a clean environment and prevents resource conflicts when bringing pods back online.

* [K8SPS-435](https://perconadev.atlassian.net/browse/K8SPS-435) - Prevented scheduled backups from running if the database is in an unhealthy state. This change avoids redundant system overhead and failed backup attempts when the cluster cannot reliably provide data.

* [K8SPS-467](https://perconadev.atlassian.net/browse/K8SPS-467) - Set the default temporary path for PMM agents to /tmp/pmm to improve platform compatibility. This update specifically resolves file system permission issues encountered on platforms like OpenShift.

* [K8SPS-595](https://perconadev.atlassian.net/browse/K8SPS-595) - Replaced Operator panics with structured error handling when invalid storage configurations are detected. Users will now receive clear diagnostic messages instead of operator crashes, facilitating easier troubleshooting.

* [K8SPS-601](https://perconadev.atlassian.net/browse/K8SPS-601) - Reclassified status changes and replication warnings as "Normal" event types in Kubernetes. This update reduces monitoring noise by distinguishing expected operational transitions from critical failures.

* [K8SPS-622](https://perconadev.atlassian.net/browse/K8SPS-622) - Made the async replication retry count configurable via the Custom Resource. Users can now tune the `SOURCE_RETRY_COUNT` parameter to better match their specific network conditions and stability requirements.

* [K8SPS-666](https://perconadev.atlassian.net/browse/K8SPS-666) - Optimized how file descriptors are managed in the HAProxy entrypoint to avoid performance bottlenecks. This fix prevents HAProxy from attempting to close thousands of unused file descriptors during health checks.

### Fixed bugs

* [K8SPS-530](https://perconadev.atlassian.net/browse/K8SPS-530) - Fixed an issue where the `percona/delete-backup` finalizer would block the deletion of backups stuck in the starting state. Users can now immediately remove pending or failed backup resources without waiting for a timeout.

* [K8SPS-616](https://perconadev.atlassian.net/browse/K8SPS-616) - Removed the requirement for a backup image when backups are explicitly disabled in the configuration. This simplifies the Custom Resource definition by eliminating unnecessary parameters for unused features.

* [K8SPS-623](https://perconadev.atlassian.net/browse/K8SPS-623) - Resolved an "Access Denied" error when performing GCS backups to private buckets. The Operator now correctly validates and uses credentials to authenticate storage access during the backup process.

* [K8SPS-635](https://perconadev.atlassian.net/browse/K8SPS-635) - Fixed a bug where annotations for MySQL, HAProxy, and Router were not correctly applied to all components. This ensure that custom metadata and third-party integrations work consistently across the entire cluster deployment.

* [K8SPS-653](https://perconadev.atlassian.net/browse/K8SPS-653) - Corrected a validation error where the Operator would default to asynchronous replication even when not explicitly requested. The Operator now adheres to the intended cluster type, preventing unexpected deployment failures.

* [K8SPS-661](https://perconadev.atlassian.net/browse/K8SPS-661) - Resolved an issue where primary nodes retained stale replication configurations after a Kubernetes node restart. This fix ensures that primary nodes are always initialized with the most current cluster state. (Thank you Alexander Khozya for reporting this issue)

* [K8SPS-669](https://perconadev.atlassian.net/browse/K8SPS-669) - Enabled automated recovery for clusters that have suffered a complete loss of quorum. The Operator can now detect and rebuild the cluster automatically, significantly reducing recovery time is case of failures.

* [K8SPS-684](https://perconadev.atlassian.net/browse/K8SPS-684) - Resolved a connection drop issue that occurred whenever the HAProxy configuration was reloaded. This ensures stable and uninterrupted application connectivity during proxy maintenance or scaling events.

## Supported software

--8<-- [start:software]

The Operator was developed and tested with the following software:

* Percona Server for MySQL 8.4.8-8.1
* Percona Server for MySQL 8.0.45-36.1
* XtraBackup 8.4.0-5.1
* XtraBackup 8.0.35-35.1
* MySQL Router 8.4.8
* MySQL Router 8.0.45
* HAProxy 2.8.18-1
* Orchestrator 3.2.6-20
* Percona Toolkit 3.7.1
* PMM Client 3.7.0
* Cert Manager 1.19.1
* Percona Binlog Server 0.2.1

Other options may also work but have not been tested.

--8<-- [end:software]

## Supported platforms

Percona Operators are designed for compatibility with all [CNCF-certified :octicons-link-external-16:](https://www.cncf.io/training/certification/software-conformance/) Kubernetes distributions. Our release process includes targeted testing and validation on major cloud provider platforms and OpenShift, as detailed below:

--8<-- [start:platforms]

* [Google Kubernetes Engine (GKE) :octicons-link-external-16:](https://cloud.google.com/kubernetes-engine) 1.32 - 1.35
* [Amazon Elastic Kubernetes Service (EKS) :octicons-link-external-16:](https://aws.amazon.com/eks/) 1.33 - 1.35
* [Azure Kubernetes Service (AKS) :octicons-link-external-16:](https://azure.microsoft.com/en-us/products/kubernetes-service) 1.33 - 1.35
* [OpenShift :octicons-link-external-16:](https://www.openshift.com) 4.18.36 - 4.21.8
* [Minikube :octicons-link-external-16:](https://minikube.sigs.k8s.io/docs/) 1.38.1 based on Kubernetes v1.35.1

--8<-- [end:platforms]

This list only includes the platforms on which the Percona Operators are specifically tested as part of the release process. Compatibility with other Kubernetes flavors and versions depends on the backward compatibility provided by Kubernetes itself.

## Percona certified images

Find Percona's certified Docker images that you can use with Percona Operator for MySQL based on Percona Server for MySQL in the following table:

--8<-- [start:images]

Image                                                    | Digest                                                           |
|:---------------------------------------------------------|:-----------------------------------------------------------------|
| percona/percona-server-mysql-operator:1.1.0             | c44447339098998367dcc84028ad065a3872c9b8b1239d5b338e90f28f984107 |
| percona/percona-server-mysql-operator:1.1.0 (ARM64)     | 55ffe11625f6453c67e394c5cc757746d8a5c58022cd6285af5a5072f850ff4e |
| percona/percona-server:8.4.8-8.1                         | 5203959150b5afe769f04f17453ae22d63ea889dfbbdef6acc013e999cc31552 |
| percona/percona-server:8.4.8-8.1 (ARM64)                 | 831ac32171d0b794826e276745cf3e7526b63c62447fdb266b9e308e7028319e |
| percona/percona-server:8.0.45-36.1                       | 27845b5451a1b707df70e832d51bcd3c384e6cb3cc02799a7bc01ec6cd578c2d |
| percona/percona-server:8.0.45-36.1 (ARM64)               | 1dae69344a18d21800fd65752a1450ddaac31b50d733d3eb1507f28ec824172d |
| percona/percona-xtrabackup:8.4.0-5.1                     | 1c7e20fac192f70de2233e471a9243ba9a65399e9667cf954f5fc5afba1b9aa4 |
| percona/percona-xtrabackup:8.4.0-5.1 (ARM64)             | dd6089277586865a7debfbe2e8b3a894632f9240fd1aec8c77c4f71cb9750b90 |
| percona/percona-xtrabackup:8.0.35-35.1                   | f44162b0bede26d74f23c1cd3ab58efb0f43529f7fe09d221e3ad7b473463f0b |
| percona/percona-xtrabackup:8.0.35-35.1 (ARM64)           | 68908749139e3904d81a21a0cbb7ff85b08dc7a65d9d063b17dfff278ad81107 |
| percona/percona-mysql-router:8.4.8                       | c087433f2824a0d53e297d13eb8db995b3b6cb6c90491d894a0494bb1ccbf6bd |
| percona/percona-mysql-router:8.4.8 (ARM64)               | c087433f2824a0d53e297d13eb8db995b3b6cb6c90491d894a0494bb1ccbf6bd |
| percona/percona-mysql-router:8.0.45                      | 0b1a1ba2005eb7be254d2e7b851802c33081f428d4f8524ed5f62a354499fa2e |
| percona/percona-mysql-router:8.0.45 (ARM64)              | 0b1a1ba2005eb7be254d2e7b851802c33081f428d4f8524ed5f62a354499fa2e |
| percona/percona-orchestrator:3.2.6-20                    | 13ae84e75279201da09ed8cd1936a5306fa2f29b2cc74478974f16a5d1e05e6c |
| percona/percona-orchestrator:3.2.6-20 (ARM64)            | 1d0f9b414fcadebe6d3c2e6778e58e0f17b42c64a4293f03efc744b1d27bef99 |
| percona/haproxy:2.8.18-1                                 | fa668cec0a541ce862ecd8fd781df4631e837e085dde6b5ae2a4bb678cc84024 |
| percona/haproxy:2.8.18-1 (ARM64)                         | 8271dafc8db4d1a4e5a446b3618ec8bed95837c7e9066cce0898ffefdf6b36f1 |
| percona/percona-toolkit:3.7.1-3                          | 7fd2092b0ac8addf44163a5a7e1999acf5ae34ccffe77aeb005aa6ea8a8cfc5d |
| percona/percona-toolkit:3.7.1-3 (ARM64)                  | afa0a0c7826433071da8f16077830977522240f03959e0b57db14ecad2357cca |
| percona/pmm-client:3.7.0                                 | 3ddfd925a9f6bb0daee88021e0310f8375f550afd70b7f2d0980509b7f3fb777 |
| percona/pmm-client:3.7.0 (ARM64)                         | 2701042087701c70666fd88383bfac22368c339a033b15e364bd6dd417ad1922 |
| percona/percona-server-mysql-operator:1.1.0-binlog-server-0.2.1 | 9ffb7db0094dc0c39f6ec794b70a33db6e4cd19aa4ca38cd6a9b05bc5bbea63c |
| percona/percona-server-mysql-operator:1.1.0-binlog-server-0.2.1 (ARM64) | 97ad1244d08773eb6e6121c4b45424d88d2a624fbd26eb40ab907d054999e154 |


--8<-- [end:images]

[Find images for previous versions :octicons-link-external-16:](https://docs.percona.com/legacy-documentation/){.md-button}
