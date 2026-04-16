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

Compression works for full and [incremental backups](#incremental-backups), and you can use it for both on demand and scheduled backup workflows. You configure compression globally or per backup storage directly in the Custom Resource and can choose from [compression algorithms supported by Percona XtraBackup](../backups-compressed.md#choosing-a-compression-algorythm). For example, override the compression algorithm for a specific on-demand backup. 

During the restore, the Operator automatically detects whether a backup is compressed and decompresses it as part of the restore workflow, so no additional steps are required from you.

Currently the Operator supports only the `zstd` compression algorithm. This is a known limitation and will be lifted after the [PXB-3568](https://perconadev.atlassian.net/browse/PXB-3568) is resolved.

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

Read more about other environment variables in our [documentation](../env-var-custom.md)

This makes cluster management more predictable and avoids unexpected stalls during replication interruptions.

### Documentation updates

* Completed the install on Openshift documentation with instructions how to install using OLM
* Added a tutorial how to upgrade the Operator on OpenShift
* Enhanced Helm install documentation explaining how to install the Operator with customized parameters and apply custom naming to releases

## CRD changes

* The `.status.storage.s3.storageClass` has now the type `string`
* The `v1.^.status.storage.s3.storageClass` field is removed

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

* [K8SPS-530](https://perconadev.atlassian.net/browse/K8SPS-530) - Fixed an issue where the delete-backup finalizer would block the deletion of backups stuck in the starting state. Users can now immediately remove pending or failed backup resources without waiting for a timeout.

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
| percona/percona-server-mysql-operator:1.0.0             | 36d82324630c7b2030c6f96df8dc8433726c1236f915e790825a54571dbca7f3 |
| percona/percona-server-mysql-operator:1.0.0 (ARM64)     | fa9e3082d51d3c52f6cefbd1be129f4585effba7ca6221fd1234a481ddcd61a5 |
| percona/percona-server:8.4.6-6.1                         | ea97c9df3e362728fc3819c28c841498f5a1765945b9556bc964b218b7d4dc97 |
| percona/percona-server:8.0.43-34.1                       | 315efeac572c48cc6f118bba7e0b2545ad396142f60328f2db9620ae0ad57e45 |
| percona/percona-xtrabackup:8.4.0-4.1                     | 840260525cf27e299b5edc7b48ad19caea03ad3ea7349000d0fc6de627b2fb10 |
| percona/percona-xtrabackup:8.0.35-34.1                   | 967bafa0823c90aa8fa9c25a9012be36b0deef64e255294a09148d77ce6aea68 |
| percona/percona-mysql-router:8.4.6                       | e083c632c118cd4af472d9030a7900401f4b338e069c91996fe33747b77be985 |
| percona/percona-mysql-router:8.0.43                      | 3a420b803cd39c7c2a3ff414d45d1858df39599961339f5c02df0681f558ccdd |
| percona/percona-orchestrator:3.2.6-18                    | a8a70f8882925b0a1a46893376e29af73646117b22e1eeb5a0a89876a907651f |
| percona/haproxy:2.8.15                                   | e64e468ac0ed2036ee164631469cc71821dcb84a6d568883f704d0eacaf84bb4 |
| percona/percona-toolkit:3.7.0-2                          | b7a4a2ca71ebf2b35786ab614221cbefb032fd5dfb5c5a478efcdd23931dd70b |
| percona/pmm-client:3.4.1                                 | 1c59d7188f8404e0294f4bfb3d2c3600107f808a023668a170a6b8036c56619b |
| percona/pmm-client:3.4.1 (ARM64)                         | 2d23ba3e6f0ae88201be15272c5038d7c38f382ad8222cd93f094b5a20b854a5 |


--8<-- [end:images]

[Find images for previous versions :octicons-link-external-16:](https://docs.percona.com/legacy-documentation/){.md-button}
