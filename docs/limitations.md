# Known limitations

This page describes known limitations of Percona Operator for MySQL based on Percona Server for MySQL. Understanding these constraints helps you plan deployments and avoid unexpected behavior.

## Tech preview features

The following features are in tech preview. Behavior can change in future releases. Do not use them in production yet. We encourage you to try them in test or staging clusters and share feedback.

* [Asynchronous replication](architecture.md#asynchronous-replication-tech-preview) (`spec.mysql.clusterType: async`)
* [Point-in-time recovery](backups-pitr.md)
* [Incremental backups](backups-incremental.md)

Group replication is generally available and is the recommended topology for production.

## Replication and topology

* Changing the replication type on a **running** cluster is not supported. Pause the cluster, change `spec.mysql.clusterType`, then resume it. See [Change replication type](change-replication-type.md).
* Semi-synchronous replication is not supported. Use group replication or asynchronous replication.
* Group replication supports a maximum of **9** MySQL instances per group. Large transactions can slow the cluster, and especially large transactions can trigger a member fault if the group cannot copy the transaction within a 5-second network window. See [Architecture](architecture.md#group-replication).
* Safe defaults require at least **3** MySQL instances for group replication, an **odd** replica count, and (for asynchronous replication) Orchestrator size of **3 or greater and odd**. You must set the matching [`unsafeFlags`](operator.md#operator-unsafeflags-section) option to go below those limits.
* HAProxy and MySQL Router cannot be enabled at the same time. MySQL Router is available only with group replication. Asynchronous replication requires HAProxy (unless you set `unsafeFlags.proxy`).
* The cluster Custom Resource `metadata.name` must include only URL-compatible characters, must not exceed 22 characters, must start with an alphabetic character, and must end with an alphanumeric character.

## Backups and restores

* The Operator stores backups in cloud object storage only. These object storages are supported: AWS S3 and S3-compatible storages, Microsoft Azure Blob Storage, Google Cloud Storage. Local filesystem backups are not supported.
* Backup compression supports only the `zstd` algorithm. `lz4` is not supported yet.
* When several [scheduled backups](backups-scheduled.md#managing-multiple-backup-schedules-in-the-same-storage) use the **same storage location**:
  
    * Retention (`keep`) applies only to the first schedule in the list, not independently per schedule.
    * Overlapping runs that write to the same path can overwrite each other. Use a separate storage name (different bucket or prefix) for each schedule.
  
* For [incremental backups](backups-incremental.md):
    
    * Retention applies to the whole chain. You cannot set a separate retention policy for increments. Deleting the base full backup deletes the entire chain.
    * You cannot delete an increment in the middle of a chain. Delete only the last increment, or delete the base backup to remove the chain.
    * If a backup in the chain fails after some data was already uploaded, start a new chain. A missing checkpoint file can also hang the next incremental backup.

## Point-in-time recovery

Point-in-time recovery is in tech preview. Additional constraints:

* The Binlog Server supports only AWS S3 and S3-compatible storage.
* After you change the Operator user password, take a new full backup. Otherwise point-in-time recovery fails because the password in the base backup no longer matches.
* Point-in-time recovery Job retries are not idempotent. If recovery fails after the base backup is restored, a retry does not restore the full backup again. Set `spec.backup.backoffLimit: 0` in the cluster Custom Resource to disable automatic Job retries.
* Binlog storage for point-in-time recovery is separate from base backup storage. Configure it under `spec.backup.pitr.binlogServer` for in-place restore, or under `spec.pitr.backupSource.binlogServer` on the Restore object for a cross-cluster restore.

See [Point-in-time recovery](backups-pitr.md#known-limitations) for details, including `force: true` behavior during binlog replay.

## Cross-site replication

Cross-site replication (InnoDB ClusterSet) requires Operator 1.2.0 or later and **group replication** clusters only. Mixing asynchronous and group replication in a ClusterSet is not supported. Switchover is always user-initiated.

Additional constraints include: no automatic rejoin after replication stops, no support of ClusterSets created outside the Operator, no restore onto a ClusterSet replica, backups from a ClusterSet cannot be restored onto a fresh unrelated cluster, and a removed member cannot rejoin the same ClusterSet.

See [Cross-site replication](replication.md#known-limitations) for the full list and recovery steps.

## Scaling and storage

* You cannot shrink an existing Persistent Volume Claim. You can only increase storage size. See [Scale storage](scaling.md#scale-storage).
* Using the Operator's storage autoscaling together with an external PVC autoscaler is not supported. Choose one method.
* Some storage providers limit volume expansion. Check your provider's documentation before you rely on resize.

## Sidecars, labels, and annotations

* You can attach PVCs to [sidecar containers](sidecar.md) only when you deploy a new cluster. Updating sidecar volume claims on a running cluster is not supported.
* The Operator can add custom [labels and annotations](annotations.md) to objects it manages. It cannot delete them. Remove unused labels and annotations manually.

## Upgrades

### Binlog Server image in Operator 1.2.0

The Binlog Server image in Operator 1.2.0 is not compatible with the previous image. To upgrade it, start a fresh binlog collection: stop point-in-time recovery, take a new full backup, change the binlog bucket or prefix, update the image, then re-enable point-in-time recovery. See the [1.2.0 release notes](ReleaseNotes/Kubernetes-Operator-for-PS-RN1.2.0.md#binlog-server-image-incompatibility-notice).

### OpenShift 4.22 image pull

Starting with OpenShift 4.22, unqualified image names can resolve to Red Hat Marketplace instead of Docker Hub and fail with `ImagePullBackOff`. For a manual install or update, prefix Operator images with `docker.io`. OLM installs already use fully qualified names. See [Update on OpenShift](update-openshift.md) and the [1.2.0 release notes](ReleaseNotes/Kubernetes-Operator-for-PS-RN1.2.0.md#considerations-for-using-openshift-422).
