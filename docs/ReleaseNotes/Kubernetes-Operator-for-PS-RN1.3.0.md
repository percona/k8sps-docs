# Percona Operator for MySQL 1.3.0 ({{date.1_3_0}})

[Installation](../System-Requirements.md#installation-guidelines){.md-button}

Percona Operator for MySQL brings production-grade automation to MySQL deployments on Kubernetes. It handles provisioning, scaling, backups, failover, and upgrades using declarative Custom Resources, thus reducing manual effort and human error. With built-in support for Percona XtraBackup, proxies such as HAProxy or MySQL Router, and Percona Toolkit, it ensures resilient, secure, and performant MySQL clusters.

This release adds automatic MySQL configuration tuning, a replication type switch on a running cluster (tech preview),  encrypted binlogs for point-in-time recovery, ability to manage application users via the Custom Resource, security builds for the Operator you already run, and support for Percona Server for MySQL 9.7. It also provides a number of improvements for async clusters and ClusterSet improvements.


## What's new at a glance

**MySQL configuration**

- [Automatic MySQL configuration tuning](#automatic-mysql-configuration-tuning) - run production-ready MySQL clusters with MySQL settings calculated based on the Pod's CPU and memory, database version and workload
- [Apply dynamic MySQL configuration without restarts](#apply-dynamic-mysql-configuration-without-restarts) - change dynamic variables while the cluster is running

**Replication**

- [Zero data loss failover for asynchronous clusters](#zero-data-loss-failover-for-asynchronous-clusters) - ensure all data is kept when promoting a replica 
- [Switch replication type on a running cluster (tech preview)](#switch-replication-type-on-a-running-cluster-tech-preview) - move between Group Replication and asynchronous replication in place
- [Size asynchronous clusters the way you use them](#size-asynchronous-clusters-the-way-you-use-them) - use an even number of MySQL instances
- [Improved bootstrapping behavior for async replication clusters](#improved-bootstrapping-behavior-for-async-replication-clusters) - let a clone finish while it keeps making progress
- [Rejoin ClusterSet replicas automatically or by annotation](#rejoin-clusterset-replicas-automatically-or-by-annotation) - the Operator handles rejoin of failed replicas to the ClusterSet. You trigger rejoin only when the ClusterSet replication channel is down
- [Track replication lag for InnoDB ClusterSet](#track-replication-lag-for-innodb-clusterset) - read replication lag from the ClusterSet status

**Backups and recovery**

- [Encrypted binlogs for point-in-time recovery](#encrypted-binlogs-for-point-in-time-recovery) - encrypt binlogs before they are uploaded
- [Point-in-time recovery for encrypted clusters](#point-in-time-recovery-for-encrypted-clusters) - increase security of your point in time recovery 
- [Backup options for start and suspend deadlines](#backup-options-for-start-and-suspend-deadlines) - limit how long a backup waits to start or resume

**Security**

- [Use your existing cert-manager ClusterIssuer for TLS](#use-your-existing-cert-manager-clusterissuer-for-tls) - sign MySQL certificates with your ClusterIssuer
- [Use your own CA to verify TLS with S3-compatible storage](#use-your-own-ca-to-verify-tls-with-s3-compatible-storage) - keep TLS verification on with your CA
- [Rotate TLS certificates without restarting MySQL Pods](#rotate-tls-certificates-without-restarting-mysql-pods) - reload a new leaf when the CA stays the same
- [Security builds for the Operator you already run](#security-builds-for-the-operator-you-already-run) - receive a High or Critical vulnerability fixes without a version upgrade

**Operations**

- [Manage application users from the Custom Resource](#manage-application-users-from-the-custom-resource) - declare users, grants, and passwords in the cluster spec
- [Configurable leader election for the Operator](#configurable-leader-election-for-the-operator) - tune lease timing, or turn election off
- [Persistent logging](#persistent-logging) - keep the MySQL error log after a Pod restarts

**Platforms and MySQL versions**

- [Official support for DigitalOcean Kubernetes Service (DOKS)](#official-support-for-digitalocean-kubernetes-service-doks) - run the Operator on DigitalOcean Kubernetes
- [Support for MySQL 9.7](#support-for-mysql-97) - Percona Server for MySQL 9.7 is the default for a new cluster

## Important upgrade notes

Check the following before you upgrade the Operator to 1.3.0. The upgrade steps are in the [upgrade guide](../update-operator.md).

### Leader election is enabled by default

Starting with version 1.3.0, leader election for the Operator Deployment is on by default. When you upgrade the Operator to version 1.3.0, you can disable it via the `PSO_LEADER_ELECTION_ENABLED` environment variable.

See [Configurable leader election for the Operator](#configurable-leader-election-for-the-operator).

### Enable backups on asynchronous clusters

Version 1.3.0 requires backups so a failover on an [asynchronous replication](../architecture.md#asynchronous-replication-tech-preview) cluster can recover transactions from the old primary. An asynchronous cluster with [`backup.enabled`](../operator.md#backupenabled) set to `false` fails validation, and reconciliation stops.

The status shows an error like this:

```text
Invalid configuration: When 'mysql.clusterType' is set to 'async', 'backup.enabled' must be true unless 'unsafeFlags.asyncFailoverWithPossibleDataLoss' is enabled. Without backups a failover cannot recover the transactions stranded on the old primary
```

A cluster that was valid on Operator 1.2.0 hits this check after the upgrade. Before you upgrade, do one of the following:

* [Enable and configure backups](../backups.md#configuring-backups), and set `backup.enabled` to `true`.
* Set `unsafeFlags.asyncFailoverWithPossibleDataLoss` to `true` to continue without backups. A failover then cannot recover transactions that remain on the old primary.

Group Replication clusters are not part of this check.

## Release highlights

### Automatic MySQL configuration tuning

By default, the Operator tunes only two settings from the MySQL Pod's memory limit: `innodb_buffer_pool_size` and `max_connections`. Every other setting uses the same server default, unless a database administrator (DBA) sets it by hand. Without that tuning, a cluster either keeps defaults that don't align with the Pod's allocated resources, or runs on manual settings that go stale when someone resizes the Pod.

Starting with version 1.3.0, the Operator calculates a MySQL configuration from the Pod's CPU and memory, the workload you run, and the MySQL version. The calculation covers the InnoDB buffer pool and redo log, session buffers, connection limits, and replication settings for the cluster type you run. When you change the Pod's resources or the workload, the Operator calculates those settings again.

The automatic configuration tuning is enabled for new clusters deployed with Operator 1.3.0 and `crVersion` 1.3.0 or higher. On a cluster you upgrade, turn it on in the Custom Resource.

With MySQL configuration calculated automatically, you:

* Have MySQL settings matched to the Pod's CPU, memory, and workload
* Use the resources you already allocate to the MySQL container efficiently
* Have an updated configuration when you change `mysql.resources` or the workload

If you define MySQL settings in `spec.mysql.configuration`, a ConfigMap, or a Secret, the Operator applies those settings and skips automatic tuning.

Read [Automatic configuration tuning](../autoconfig.md) for the workflow, setup, and gotchas.

### Apply dynamic MySQL configuration without restarts

Until now, every MySQL option change in the Custom Resource, ConfigMap, or a Secret triggered a rolling restart. That is correct for static variables, but many MySQL settings are dynamic and can take effect with the `SET GLOBAL` command. Restarts on every change dropped connections, flushed buffer pools, and made peak-hour tuning risky.

The Operator now applies dynamic variables at runtime. Update `mysql.configuration` in the Custom Resource and the Operator runs `SET GLOBAL` on every ready Pod without restarting it. If you set the value yourself with `SET GLOBAL` from the Pod, the Operator does not overwrite it. To keep that change after a Pod restart, add it to the Custom Resource, ConfigMap, or a Secret. If the declared value already matches, there is no restart.

Static variables, runtime-blocked changes, and removed options still trigger a rolling restart. You can tune a busy cluster and respond to an incident without a configuration restart.

Learn more in the [dynamic configuration documentation](../options.md#dynamic-configuration).

### Zero data loss failover for asynchronous clusters

Asynchronous replication copies transactions to replicas with a delay. If the primary fails, for example after an out-of-memory kill or a hardware fault, the transactions it committed but hasn't yet sent to any replica exist only in its binary log. Until now, promoting a replica in that situation meant losing those transactions.

Starting with version 1.3.0, the Operator and Orchestrator recover those transactions before promoting a new primary. The replica chosen for promotion fetches the binary logs it is missing from the failed primary and applies them. Only then does it become the new primary. The logs are read through the `xtrabackup` sidecar, so the failed primary's Pod must be reachable and its data volume intact, but `mysqld` on that Pod can be down.

You decide what happens when recovery can't finish. You set a timeout (one hour by default) and a policy for when it expires. By default, the cluster stays read-only until you act. Alternatively, you can let the Operator promote a replica and accept the possible data loss. You can also force a promotion yourself with an annotation. The cluster's status conditions and events show whether a failover is in progress or blocked.

With zero data loss failover, you gain:

- No lost transactions on primary failure — the new primary has everything the failed primary wrote to its binary log
- Predictable outcomes — the cluster waits and then follows the policy you chose instead of promoting a replica that is behind
- Visibility — status conditions and events report the state of every failover
- Declarative setup — you configure it in the cluster Custom Resource, like the rest of the cluster

This feature requires backups to be enabled for the cluster. Asynchronous replication is a tech preview, so we don't recommend it for production environments yet.

To learn more, read our [documentation](../failover-async.md).

### Switch replication type on a running cluster (tech preview)

Now you can switch between Group Replication and asynchronous replication on a running cluster. Change `spec.mysql.clusterType`, and the Operator completes the switch. You do not pause the cluster and bring it back yourself. 

The Operator converts the topology in place: it tears down the old replication setup, recreates the MySQL and proxy workloads, and bootstraps the new type on the same PersistentVolumeClaims. Users, Secrets, and the HAProxy Service stay in place, so applications keep the same connection endpoint if they already use HAProxy.

Switching the replication type on a running cluster is in tech preview stage. Try it in a staging cluster before you use it in production.

Use the switch when you need to:

- Move to Group Replication for stronger consistency, native failover, or [InnoDB ClusterSet](../replication.md). Before you switch from asynchronous replication to Group Replication, confirm every replica is caught up and take a backup from the primary. The Operator can overwrite transactions that exist only outside `mysql-0`.
- Move to asynchronous replication for lower write latency, more than nine MySQL instances, or to avoid Group Replication limits on large transactions. 
   
   If a switch from Group Replication to asynchronous replication fails during bootstrap, you cannot switch back. Make sure to make a backup before the switch. This way you can restore the cluster from that backup.

The switch causes downtime while Pods restart. It applies to the entire cluster. 

Learn more in the [Change replication type](../change-replication-type.md) documentation.

### Rejoin ClusterSet replicas automatically or by annotation

With this release, the Operator automates ClusterSet replica rejoin. If the replica is paused, stopped, or crashed, the Operator reboots and rejoins it. If the replica is healthy but the ClusterSet replication channel is down after a long primary outage, choose a safe window and trigger rejoin by annotating the ClusterSet Custom Resource. The Operator then creates a rejoin Job, tracks its progress, and removes the annotation. On failure, it deletes the job and emits the `ClusterSetMemberRejoinFailed` warning. After you fix the cause, you can retry.

You decide when to rejoin, and the Operator runs the Job. For the steps, see [Rejoin a replica cluster](../replication-setup.md#rejoin-a-replica-cluster).

### Track replication lag for InnoDB ClusterSet

You can now see how far a ClusterSet replica is behind the primary in ClusterSet status with `kubectl`, instead of connecting to MySQL Shell. Use it to:

* Confirm a replica is catching up before you run switchover
* Keep read traffic off a site that is still behind
* Spot growing lag as it happens

Learn more in [Custom resource statuses](../cr-statuses.md#per-member-cluster-status).

### Size asynchronous clusters the way you use them

Asynchronous replication uses a primary and replicas. The nodes do not form a voting group. When the primary fails, Orchestrator promotes a replica, so an even number of instances is a valid high-availability setup.

You can now set `mysql.size` to 2, 4, 6, or any larger even count on an asynchronous cluster without `unsafeFlags.mysqlSize`. A single-instance cluster (`mysql.size: 1`) still requires the flag, because there is no replica to fail over to.

Use the replica count that fits your workload. Orchestrator still requires an odd size of 3 or greater. Set [`unsafeFlags.orchestratorSize`](../operator.md#unsafeflagsorchestratorsize) to run fewer than 3 Orchestrator Pods.

Asynchronous replication remains a tech preview feature.

Learn more in [Architecture](../architecture.md#asynchronous-replication-tech-preview) and [Horizontal scaling](../scaling.md#horizontal-scaling).

### Improved bootstrapping behavior for async replication clusters

When a replica joins or rejoins an asynchronous cluster, MySQL copies the data with a native InnoDB clone (`CLONE INSTANCE`). With this release, joining works as follows:

* The `pt-heartbeat` sidecar does not start during the clone. It queries MySQL and starts `pt-heartbeat` only after the clone is no longer in progress and the `sys_operator` database is present. The sidecar waits until the clone finishes. A finished clone also restarts MySQL Pods. If `pt-heartbeat` exits in that short window, the script starts it again in the same container. A process that ran for a while and then exits is still treated as a failure, and the container restarts.
* The clone no longer has a fixed time limit. Bootstrap polls clone progress and stops the clone only when it makes no progress for `BOOTSTRAP_CLONE_STALL_TIMEOUT` (default 900 seconds). A clone that keeps moving runs until it finishes. A frozen clone, or one that cannot be observed for the whole stall window, is stopped. That fails the startup probe, kubelet restarts the container, and the clone is retried.

This behavior applies to clusters with `crVersion` set to 1.3.0. The Operator ignores `BOOTSTRAP_CLONE_TIMEOUT` for those clusters. The fixed timeout remains only for clusters with `crVersion` older than 1.3.0.

To turn off the stall check, set `BOOTSTRAP_CLONE_STALL_TIMEOUT` to `0`. See [Define environment variables for cluster components](../env-vars-custom.md) for guidelines.

### Encrypted binlogs for point-in-time recovery

Encrypted backups and data-at-rest encryption protect the database and the base backup. They do not protect the binary logs that the Binlog Server stores in object storage for point-in-time recovery. Those files are written in plaintext, which leaves a gap if you use S3-compatible storage without server-side encryption, or if you need the full recovery path encrypted.

You can now encrypt binlogs before Percona Binlog Server uploads them. Create a Kubernetes Secret with your encryption keys, reference it in the cluster Custom Resource, and set the storage encryption options. The Operator validates the Secret, encrypts each new file on the way to the bucket, and decrypts it during restore. Files already in the bucket stay as they are and are applied as-is, so you can turn encryption on without emptying storage.

During key rotation, keep all previous keys in the Secret. Keep the Secret in the cluster if you turn binlog encryption off, so the Operator can still read existing encrypted binlogs. If a key is lost, those files cannot be recovered.

Point-in-time recovery remains a tech preview feature.

To learn more, read [Binlog encryption](../backups-pitr.md#binlog-encryption).

### Point-in-time recovery for encrypted clusters

You can now restore an encrypted cluster to a specific point in time. The Operator uses your existing Vault Secret during restore, so tablespaces and binlogs stay encrypted, and you can still roll the database forward to the GTID or time you need.

Point-in-time recovery remains a tech preview. Read more in the [point-in-time recovery documentation](../backups-pitr.md).

### Backup options for start and suspend deadlines

This release adds options for how long a backup can wait.

`backup.startingDeadlineSeconds` sets how long a backup can wait to start. The backup waits when the cluster is not ready, or when another backup for this cluster is still running. If the Operator does not create the Job before this time expires, the backup state becomes `Error`.

`backup.suspendedDeadlineSeconds` sets how long a suspended backup can wait to resume. The Operator suspends a backup when the cluster is unhealthy, and resumes it when the cluster is ready again. A resumed backup starts from the beginning. If the backup does not resume before this time expires, the Operator marks it `Failed` and deletes the suspended Job.

The default for both options is `0`, which means the Operator does not enforce a deadline. Set them in the cluster Custom Resource for every backup, or on a `PerconaServerMySQLBackup` object for one backup. The value on the backup object takes precedence.

```yaml
spec:
  backup:
    startingDeadlineSeconds: 900
    suspendedDeadlineSeconds: 900
```

Read [Set a waiting time for a backup to start](../backups.md#set-a-waiting-time-for-a-backup-to-start) and [Suspend backups on an unhealthy cluster](../backups.md#suspend-backups-on-an-unhealthy-cluster) to learn more.

### Use your existing cert-manager ClusterIssuer for TLS

If you already run cert-manager with a cluster-wide issuer, you can point Percona Operator for MySQL at that `ClusterIssuer` resource. Percona Server for MySQL certificates are then signed under the same public key infrastructure (PKI) you use for the rest of the platform.

To use a `ClusterIssuer`, configure the cluster as follows:

```yaml
spec:
  tls:
    issuerConf:
      name: my-org-issuer
      kind: ClusterIssuer
      group: cert-manager.io
```

The Operator resolves the issuer by kind, creates the leaf `Certificate`, and lets cert-manager sign and renew it. The Operator does not create a separate CA or overwrite your issuer.

MySQL TLS then follows the same issuer, renewal, and trust policy as your other workloads. You keep one source of truth for certificates instead of an Operator-managed CA in every database namespace.

Learn more in the [cert-manager TLS documentation](../tls-cert-manager.md#use-an-existing-clusterissuer).

### Use your own CA to verify TLS with S3-compatible storage

You can now verify TLS to S3-compatible storage with the certificate authority (CA) your organization already trusts. That matters when you use certificates from your corporate PKI, and security policy does not let you skip certificate checks.

Create a Secret with the CA and reference it in the storage configuration. Keep TLS verification enabled. The Operator uses that CA for backups and restores. You can also use the same CA for point-in-time recovery (tech preview) by referencing it in the Binlog Server storage configuration.

```yaml
spec:
  backup:
    enabled: true
    storages:
      minio:
        type: s3
        verifyTLS: true
        s3:
          bucket: S3-BACKUP-BUCKET-NAME-HERE
          region: us-west-2
          credentialsSecret: ps-cluster1-s3-credentials
          endpointUrl: https://minio-service:9000
          caBundle:
            name: minio-ca-bundle
            key: ca.crt
    pitr:
      enabled: true
      binlogServer:
        storage:
          s3:
            bucket: my-binlogs
            credentialsSecret: my-s3-secret
            region: us-east-1
            prefix: binlogs
            endpointUrl: https://minio-service:9000
            caBundle:
              name: minio-ca-bundle
              key: ca.crt
```

With this configuration you get:

* TLS verification that stays enabled for S3-compatible storage
* The CA your organization already trusts
* The same check for backups, restores, and point-in-time recovery

Read more in [Configure TLS verification with custom certificates for S3 storage](../backups-storage.md#configure-tls-verification-with-custom-certificates-for-s3-storage).

### Rotate TLS certificates without restarting MySQL Pods

When you update the server certificate (the leaf) in the TLS Secret, the Operator reloads the updated leaf into running `mysqld` processes when the certificate authority (CA) stays the same. MySQL Pods stay up. Existing connections keep the previous certificate until they reconnect. New connections use the new one.

HAProxy, MySQL Router, and Orchestrator still restart, because they read certificates once at startup. Changing the CA still restarts MySQL Pods. If you replace the CA, follow the CA rotation procedure in the [Update certificates](../tls-update.md) documentation.

This change gives you:

* MySQL availability during routine certificate renewal
* Fewer database Pod restarts on a cert-manager schedule
* The same workflow: keep `ca.crt` unchanged and replace only `tls.crt` and `tls.key`, or let cert-manager renew the leaf

### Security builds for the Operator you already run

The Operator has access to your cluster credentials and configuration. A vulnerability in the Operator image can expose that data even when your MySQL cluster is fully patched.

Security builds close that gap on a release you already run. Apply the fix without waiting for the next Operator version or retesting a full upgrade. A security build is a new Operator image that fixes a High or Critical vulnerability in your current Operator version.

Each release now comes with the following tags:

* `1.3.0` is the original release. Use it for a standard deployment.
* `1.3.0-1` is the same release image with a numbered tag. Use it when you need a fixed digest.
* `1.3.0-2`, `1.3.0-3`, and later numbers are security builds of that release. Each numbered tag stays on its own image. The first security build is `1.3.0-2`.
* `1.3.0-latest` is the newest image for this release. The tag moves, and it points at the most recent image.

Only the Operator image is updated. Database cluster components stay on the versions from the original release. Vulnerabilities in those images are outside a security build.

To apply a security build, patch the Operator Deployment and set the image to the security tag you chose. This restarts the Operator Pod. The cluster keeps running.

Read more in the [security builds documentation](../security-builds.md).

### Manage application users from the Custom Resource

Previously, you could only create application users by connecting to MySQL after the cluster was ready and running SQL, or adding extra steps to your CI/CD pipeline. You can now declare users in the cluster Custom Resource and let the Operator create them, grant privileges, and rotate passwords.

For each user, set the name. Optionally, set the hosts they can connect from, the databases they can access, and the MySQL grants. Supply a password in a Secret, or omit it and the Operator generates one and stores it in the `<cluster-name>-user-<username>` Secret. Change the Secret to rotate the password. The Operator applies it on the next reconcile.

You can create users when you provision the cluster and update them the same way you update any other configuration.

Learn more in [Manage users](../users.md#create-users-in-the-custom-resource).

### Configurable leader election for the Operator

You can now tune leader election for the Operator Deployment with environment variables. This helps when leader election fails, for example in a high-latency or resource-constrained cluster.

Leader election is enabled by default. When you upgrade, you can turn it off with `PSO_LEADER_ELECTION_ENABLED` environment variable if the Deployment has one replica.

* Set `PSO_LEADER_ELECTION_LEASE_DURATION`, `PSO_LEADER_ELECTION_RENEW_DEADLINE`, and `PSO_LEADER_ELECTION_RETRY_PERIOD` to adjust lease timing.
* Set `PSO_LEADER_ELECTION_ENABLED` to turn leader election on or off.
* Set `PSO_LEADER_ELECTION_LEASE_NAME` to use a custom Lease for the leader lock.

Learn more about these environment variables in the [documentation](../env-vars-operator.md).

### Persistent logging

Container logs disappear when a Pod restarts, so the MySQL error log from a crash is often gone by the time you look. Now the Operator keeps that error log on the MySQL data volume and rotates it so the file does not fill the volume.

Each MySQL Pod runs two sidecars. The `logs` container uses Fluent Bit to collect the error logs and the `logrotate` container rotates those files. During a backup, Fluent Bit also tails the Percona XtraBackup log. Those files live on an emptyDir volume. The Operator does not rotate them, and they do not survive a restart of the MySQL Pod.

Persistent logging is on by default for a cluster with `crVersion` 1.3.0 or later. It covers MySQL Pods only. HAProxy, MySQL Router, Orchestrator, and Percona Binlog Server still write only to standard output.

Read [Persistent logging](../persistent-logging.md) and [Log rotation](../logrotate.md) to learn more.

### Official support for DigitalOcean Kubernetes Service (DOKS)

DigitalOcean Kubernetes Service (DOKS) is now a supported platform. Every Operator release is tested on DOKS, so you can run the Operator on DigitalOcean-managed Kubernetes clusters.

To install the Operator on DOKS, read the [installation guide](../doks.md).

### Support for MySQL 9.7

This release adds support for Percona Server for MySQL 9.7. The Operator supports the major functionality of this version.

Percona Server for MySQL 9.7 is the default MySQL version for a new database cluster.



## CRD changes

These are the Custom Resource changes since Operator 1.2.0.

### PerconaServerMySQL

New fields:

* `spec.mysql.autoConfig` sets automatic MySQL configuration tuning with `enabled`, `loadType`, and `version`. When tuning is on, the Pod needs CPU and memory resources, and `version` is required.
* `spec.users` declares application users with `name`, `hosts`, `dbs`, `grants`, `passwordSecretRef`, and `withGrantOption`. See [Manage users](../users.md#create-users-in-the-custom-resource).
* `spec.logcollector` adds persistent logging and log rotation. `logRotate.schedule` defaults to `0 0 * * *`. `image` is required when the section is set.
* `spec.backup.startingDeadlineSeconds` and `spec.backup.suspendedDeadlineSeconds` set how long a backup can wait to start or to resume. The same fields exist on `PerconaServerMySQLBackup`. See [Set a waiting time for a backup to start](../backups.md#set-a-waiting-time-for-a-backup-to-start).
* `spec.backup.storages.<name>.s3.caBundle` and `spec.backup.pitr.binlogServer.storage.s3.caBundle` name the Secret that holds your CA. `key` defaults to `ca.crt`. See [Configure TLS verification with custom certificates for S3 storage](../backups-storage.md#configure-tls-verification-with-custom-certificates-for-s3-storage).
* `spec.backup.pitr.binlogServer.storage.encryption` sets binlog encryption. `cipher` defaults to `AES-256-CTR`. `spec.backup.pitr.binlogServer.keyringSecret` is required when encryption is set. `key` defaults to `keyring.json`.
* `spec.orchestrator.failover` sets asynchronous failover behavior. `timeout` defaults to `1h`. `onTimeout` is `Abort` or `ForceWithPossibleDataLoss` and defaults to `Abort`. This section is valid only when `mysql.clusterType` is `async`.
* `spec.pmm.haproxyParams` passes HAProxy parameters to the PMM client.
* `spec.unsafeFlags.asyncFailoverWithPossibleDataLoss` lets an asynchronous cluster run without backups. See [Important upgrade notes](#enable-backups-on-asynchronous-clusters).
* `status.clusterType` reports the replication type the Operator last observed.

Validation changes:

* An asynchronous cluster can use `mysql.size` of 2 or greater, including an even count, without `unsafeFlags.mysqlSize`. Size 1 still requires that flag.
* Group Replication rejects an even `mysql.size` unless `unsafeFlags.mysqlSize` is `true`. The minimum stays 3, and a size above 9 still requires the flag.
* An asynchronous cluster requires `backup.enabled: true` unless `unsafeFlags.asyncFailoverWithPossibleDataLoss` is `true`.
* When you switch from asynchronous replication to Group Replication, `spec.orchestrator.enabled` must be `false`.
* `spec.tls.issuerConf` is an issuer reference with `name`, `kind`, and `group`, so you can point at a cert-manager `ClusterIssuer`. See [Use an existing ClusterIssuer](../tls-cert-manager.md#use-an-existing-clusterissuer).
* `spec.backup.storages` accepts at most 100 entries.
* `containerOptions.args.xtrabackup` accepts at most 100 arguments, and each argument can be at most 1024 characters. `--defaults-file` must be the first argument and use `--defaults-file=<path>`. `--defaults-extra-file` is rejected.

### PerconaServerMySQLBackup

* `spec.startingDeadlineSeconds` and `spec.suspendedDeadlineSeconds` override the cluster deadlines for one backup.
* `status.size` and `status.uncompressedSize` report the backup size after it succeeds. See [PerconaServerMySQLBackup status](../cr-statuses.md#perconaservermysqlbackup-status).

### PerconaServerMySQLRestore

* `spec.backupSource` is its own object with `destination` and `storage`. It is no longer a copy of the backup status.
* `spec.pitr.keyringSecret` supplies the keyring Secret when you restore encrypted binlogs.
* `status.erroredGeneration` records the generation of a restore that ended in `Error`.

### PerconaServerMySQLClusterSet

* `status.clusters.<name>.replicationLagSeconds` reports how far a replica cluster is behind the primary. See [Per-member cluster status](../cr-statuses.md#per-member-cluster-status).

## Changelog

### New Features

* [K8SPS-402](https://perconadev.atlassian.net/browse/K8SPS-402) - Added deadlines for backups so you can limit how long a backup waits to start or to resume. Backups for one cluster still run one at a time, and the Operator marks a backup `Error` when the start deadline passes or `Failed` when a suspended backup does not resume.

* [K8SPS-408](https://perconadev.atlassian.net/browse/K8SPS-408) - Added application user management in the Custom Resource so users, grants, and passwords are declared with the cluster. The Operator creates each user, applies the grants, and stores or rotates the password in a Secret.

* [K8SPS-500](https://perconadev.atlassian.net/browse/K8SPS-500) - Added persistent logging, so the MySQL error log stays on the data volume after a Pod restarts. A `logs` sidecar streams that log to standard output, and `logrotate` rotates the files.

* [K8SPS-646](https://perconadev.atlassian.net/browse/K8SPS-646) - Added an in-place switch between Group Replication and asynchronous replication on a running cluster (tech preview). Change `mysql.clusterType` and the Operator rebuilds the topology on the same volumes, with downtime while the Pods restart.

* [K8SPS-757](https://perconadev.atlassian.net/browse/K8SPS-757) - Added support for a read-only root filesystem on the Percona Monitoring and Management (PMM) client sidecar. The Operator stores the PMM agent configuration on a writable volume, so the sidecar can start when the container root filesystem is read-only.

* [K8SPS-762](https://perconadev.atlassian.net/browse/K8SPS-762) - Added security builds so you can patch a High or Critical vulnerability in the Operator image without upgrading to a new Operator version. Numbered tags such as `1.3.0-2` stay on a fixed image, and `1.3.0-latest` points at the newest image for your current release.

- [K8SPS-780](https://perconadev.atlassian.net/browse/K8SPS-780) - Added support for Percona Server for MySQL 9.7 so you can run clusters on this long-term support release. MySQL 9.7 is the default database version for a new cluster.

* [K8SPS-792](https://perconadev.atlassian.net/browse/K8SPS-792) - Added a custom certificate authority (CA) for S3-compatible backup storage so TLS verification can stay on with your organization's certificates. 

* [K8SPS-823](https://perconadev.atlassian.net/browse/K8SPS-823) - Added automatic MySQL configuration tuning with `mysql.autoConfig` so settings follow the Pod's CPU, memory, workload, and MySQL version. Tuning is on for a new cluster. Any value you set in `mysql.configuration` still overrides the calculated setting.

* [K8SPS-849](https://perconadev.atlassian.net/browse/K8SPS-849) - Added binlog encryption for point-in-time recovery so binary logs are encrypted before they are uploaded. The Operator validates the key Secret, encrypts each new file, and decrypts it during restore, while files already in the bucket stay unchanged.

* [K8SPS-943](https://perconadev.atlassian.net/browse/K8SPS-943) - Added official support for DigitalOcean Kubernetes Service (DOKS) so you can run the Operator on DigitalOcean-managed clusters. 

### Improvements

* [K8SPS-458](https://perconadev.atlassian.net/browse/K8SPS-458) - Added HAProxy parameters for the PMM client so monitoring follows the proxy configured on the cluster. Set `spec.pmm.haproxyParams` to pass those parameters into the client.

* [K8SPS-471](https://perconadev.atlassian.net/browse/K8SPS-471) - MySQL Pods now stay up when you rotate the server certificate and the certificate authority stays the same. The Operator reloads the new leaf into running `mysqld` processes, while HAProxy, MySQL Router, and Orchestrator still restart because they load certificates at startup.

* [K8SPS-504](https://perconadev.atlassian.net/browse/K8SPS-504) - Orchestrator updates now follow SmartUpdate and restart other Pods before the leader. The topology service stays available during the rollout instead of dropping when the leader restarts first.

* [K8SPS-514](https://perconadev.atlassian.net/browse/K8SPS-514) - The Operator now extends Orchestrator downtime on the backup source until the backup finishes. Orchestrator no longer ends that maintenance window mid-backup and fails over the Pod that is still being backed up.

- [K8SPS-528](https://perconadev.atlassian.net/browse/K8SPS-528) - You can set `mysql.size` to an even number of two or greater on an asynchronous cluster without `unsafeFlags.mysqlSize`. A single-instance cluster still requires that flag because there is no replica to fail over to.

* [K8SPS-563](https://perconadev.atlassian.net/browse/K8SPS-563) - Backup status now reports `status.size` and `status.uncompressedSize` after the backup succeeds. You can read the artifact size from `PerconaServerMySQLBackup` instead of checking object storage.

* [K8SPS-644](https://perconadev.atlassian.net/browse/K8SPS-644) - Leader election is enabled by default, and its timing is configurable with Operator environment variables. Set `PSO_LEADER_ELECTION_ENABLED` to `"false"` on a single-replica Deployment, or adjust the lease duration, renew deadline, and retry period when election fails on a slow cluster.

* [K8SPS-652](https://perconadev.atlassian.net/browse/K8SPS-652) - Disabled components no longer need an image and a size in the Custom Resource. A cluster that uses HAProxy no longer has to set MySQL Router fields, and the same applies to any other component you leave turned off.

* [K8SPS-678](https://perconadev.atlassian.net/browse/K8SPS-678) - Incremental backups can use XtraBackup page tracking so only changed InnoDB pages are copied. Pass `--page-tracking` in the `xtrabackup` container options on the storage or the base backup, and the Operator installs the `mysqlbackup` component that tracking needs.

* [K8SPS-704](https://perconadev.atlassian.net/browse/K8SPS-704) - `spec.backupSource` on a restore is now its own object with `destination` and `storage`. Restore manifests no longer reuse backup status fields that a restore does not apply.

* [K8SPS-726](https://perconadev.atlassian.net/browse/K8SPS-726) - Point-in-time recovery now works with data-at-rest encryption. The Operator uses your existing Vault Secret during restore, so tablespaces and binary logs stay encrypted while you roll forward to a GTID or a time.

* [K8SPS-730](https://perconadev.atlassian.net/browse/K8SPS-730) - The Operator now applies dynamic MySQL variables at runtime, so a change in `mysql.configuration` does not roll the Pods. A value you already set with `SET GLOBAL` on a Pod stays in place until you change the Custom Resource, and a matching value does not cause a restart.

* [K8SPS-746](https://perconadev.atlassian.net/browse/K8SPS-746) - HAProxy no longer opens a separate external check for the replica, MySQL X, and admin backends. Those backends follow the primary check, which lowers the number of connections to MySQL.

* [K8SPS-753](https://perconadev.atlassian.net/browse/K8SPS-753) - ClusterSet status now includes `replicationLagSeconds` for each replica cluster. You can read that lag with `kubectl` instead of connecting to MySQL Shell.

* [K8SPS-768](https://perconadev.atlassian.net/browse/K8SPS-768) - The Operator automatically rejoins a ClusterSet replica that was paused, stopped, or crashed. When the replica is healthy but the replication channel is down, annotate the ClusterSet and the Operator runs the rejoin Job.

- [K8SPS-802](https://perconadev.atlassian.net/browse/K8SPS-802) - The Operator now blocks deletion of a database cluster that still
belongs to a ClusterSet. The Operator adds a finalizer so that delete does not leave the ClusterSet broken.

* [K8SPS-848](https://perconadev.atlassian.net/browse/K8SPS-848) - The Group Replication liveness probe now treats a member in `RECOVERING` as alive. Kubernetes no longer kills the MySQL container while Group Replication is still catching up.

* [K8SPS-896](https://perconadev.atlassian.net/browse/K8SPS-896) - A paused Group Replication cluster no longer writes a ClusterSet status skip message on every reconcile. That message is now a debug log, so the Operator log stays readable while the cluster is paused.

* [K8SPS-934](https://perconadev.atlassian.net/browse/K8SPS-934) - Restores that end in the `Error` state are no longer run again when the Operator restarts. The Operator records `status.erroredGeneration` and skips that restore, so a restart does not pause the cluster or apply an unexpected backup.

### Bug Fixes

* [K8SPS-552](https://perconadev.atlassian.net/browse/K8SPS-552) - Fixed asynchronous cluster creation on OpenShift when you set a custom Orchestrator service account. Reconciliation no longer fails with an owner-reference error on the Orchestrator Role, so the cluster can start.

* [K8SPS-649](https://perconadev.atlassian.net/browse/K8SPS-649) - Fixed TLS issuer lookup so `tls.issuerConf.kind: ClusterIssuer` uses your cert-manager ClusterIssuer. The Operator previously looked only for an Issuer in the database namespace, so a cluster-wide issuer was ignored.

* [K8SPS-763](https://perconadev.atlassian.net/browse/K8SPS-763) - Fixed XtraBackup argument order so `--defaults-file` is the first option on backup and restore. XtraBackup rejects that flag in any other position, and jobs that set it in `containerOptions.args.xtrabackup` now start.

* [K8SPS-782](https://perconadev.atlassian.net/browse/K8SPS-782) - Fixed the HAProxy `mysql-x` backend so the primary is listed on the MySQL X Protocol port. The primary was registered on port 3306, so X Protocol clients through HAProxy did not reach it. (Thank you Wojciech Polnik for reporting this issue)

* [K8SPS-784](https://perconadev.atlassian.net/browse/K8SPS-784) - Fixed HAProxy routing so only a current primary that can accept writes is placed in the writable backend. A replica that was made writable by hand is rejected, and a newly elected primary stays unavailable until it finishes applying events.

* [K8SPS-786](https://perconadev.atlassian.net/browse/K8SPS-786) - Fixed Operator debug logs that printed Secret contents, including passwords, while updating the binlog server configuration. Secret data is omitted from those logs, and the configuration Secret is no longer rewritten on every reconcile.

* [K8SPS-791](https://perconadev.atlassian.net/browse/K8SPS-791) - Fixed restore of a backup taken on a ClusterSet replica onto a new cluster. Bootstrap clears the leftover `clusterset_replication` channel, so creating the InnoDB Cluster no longer fails on that asynchronous channel.

* [K8SPS-830](https://perconadev.atlassian.net/browse/K8SPS-830) - Fixed SmartUpdate so it continues when Pods are stuck Pending on an outdated spec. The Operator deletes those Pods and proceeds with the update instead of waiting until you delete them yourself.

* [K8SPS-840](https://perconadev.atlassian.net/browse/K8SPS-840) - Fixed cluster status so a new reconcile error replaces the previous one when the cluster is already in an error state. `status.conditions` now shows the latest failure instead of an older message.

* [K8SPS-846](https://perconadev.atlassian.net/browse/K8SPS-846) - Fixed `admin_address` selection so MySQL binds to the Pod's routable address on IPv6 and dual-stack clusters. The entrypoint used the first address from `hostname -I`, which on Amazon EKS can be a non-routable link-local address. (Thank you Domantas Speciunas for reporting this issue and contributing the fix)

* [K8SPS-851](https://perconadev.atlassian.net/browse/K8SPS-851) - The Operator no longer treats a minority Group Replication network split as a full cluster crash. Healthy Pods stay up when only some members lose connectivity. (Thank you Somanchi Poorna Sobhita for reporting this issue)

* [K8SPS-859](https://perconadev.atlassian.net/browse/K8SPS-859) - Fixed an error loop that appeared when you resized PersistentVolumeClaims after scaling the MySQL cluster up and down. The Operator no longer retries that resize and logs a missing StatefulSet error on every reconcile.

* [K8SPS-863](https://perconadev.atlassian.net/browse/K8SPS-863) - Fixed reconciliation that stalled after the MySQL StatefulSet was deleted while custom configuration was set. Applying dynamic variables no longer fails the reconcile when a Pod hostname is missing, so the Operator can recreate the StatefulSet.

* [K8SPS-866](https://perconadev.atlassian.net/browse/K8SPS-866) - Fixed the `pt-heartbeat` sidecar crash with "Unknown database 'sys_operator'" while an asynchronous replica is cloning. The sidecar now waits until the clone finishes and `sys_operator` exists before it starts.

* [K8SPS-871](https://perconadev.atlassian.net/browse/K8SPS-871) - Fixed point-in-time recovery failures when the binlog list exceeded the 1 MiB ConfigMap limit. The Operator stores a smaller compressed manifest, so restore still works as the binlog history grows.

### Documentation updates

* Added the [Recover from a full cluster crash](../crash-recovery.md) page. It explains how the Operator detects a full cluster crash on Group Replication, how recovery runs, and what to do when automatic recovery is off or does not succeed.
* Added troubleshooting pages for marker files in the MySQL data directory. [Special files in the data directory](../datadir-special-files.md) describes each file. Use them to [pause a MySQL Pod](../pause-mysql-pod.md), [pause a point-in-time recovery](../pause-pitr.md), or [unblock a stuck rolling update](../pause-mysql-pod.md#unblock-a-stuck-rolling-update).
  

## Supported software

--8<-- [start:software]

The Operator was developed and tested with the following software:

* Percona Server for MySQL 9.7.2-2.1
* Percona Server for MySQL 8.4.11-11.1
* Percona Server for MySQL 8.0.46-37.1
* XtraBackup 9.7.1-rc1.1
* XtraBackup 8.4.0-7.1
* XtraBackup 8.0.35-36.1
* MySQL Router 9.7.2
* MySQL Router 8.4.11
* MySQL Router 8.0.46
* HAProxy 3.4.4-1
* Orchestrator 3.2.6-24
* Percona Toolkit 3.7.1-4
* Log collector (Fluent Bit) 5.1.4-1
* PMM Client 3.8.1
* Cert Manager 1.21.2
* Percona Binlog Server 0.4.1

Other options may also work but have not been tested.

--8<-- [end:software]

## Supported platforms

Percona Operators are designed for compatibility with all [CNCF-certified :octicons-link-external-16:](https://www.cncf.io/training/certification/software-conformance/) Kubernetes distributions. Our release process includes targeted testing and validation on major cloud provider platforms and OpenShift, as detailed below:

--8<-- [start:platforms]

* [Google Kubernetes Engine (GKE) :octicons-link-external-16:](https://cloud.google.com/kubernetes-engine) 1.34 - 1.35
* [Amazon Elastic Kubernetes Service (EKS) :octicons-link-external-16:](https://aws.amazon.com/eks/) 1.34 - 1.37
* [DigitalOcean Kubernetes Service (DOKS) :octicons-link-external-16:](https://docs.digitalocean.com/products/kubernetes/) 1.37
* [OpenShift :octicons-link-external-16:](https://www.openshift.com) 4.19 - 4.22
* [Minikube :octicons-link-external-16:](https://minikube.sigs.k8s.io/docs/) 1.39.0 with Kubernetes v1.37.0

--8<-- [end:platforms]

This list only includes the platforms on which the Percona Operators are specifically tested as part of the release process. Compatibility with other Kubernetes flavors and versions depends on the backward compatibility provided by Kubernetes itself.

## Percona certified images

Find Percona's certified Docker images that you can use with Percona Operator for MySQL based on Percona Server for MySQL in the following table:

--8<-- [start:images]

Image                                                    | Digest                                                           |
|:---------------------------------------------------------|:-----------------------------------------------------------------|
| percona/percona-server-mysql-operator:1.2.0             | 76deed6a6daca2846fba6046b6646e25d22bca2d6d58a0b567e0a2c1240fe103 |
| percona/percona-server-mysql-operator:1.2.0 (ARM64)     | e0dd1e6bf1fd90b2149290500997ee791101f4500b5162bcea5694b1b9d7ab58 |
| percona/percona-server:8.4.10-10.1                       | d24391a363426239220c35b9707d6b26ce7522ac27abe55689baebfb48bd9fb3 |
| percona/percona-server:8.4.10-10.1 (ARM64)               | 70f6c4d01b5807737cdd423ab32af1feb1d00513b5420a84361773b167aeca87 |
| percona/percona-server:8.0.46-37.1                       | 1552a3b1860bb12325755295fb833890eb920c34fc212dbadb34c59baf0c378a |
| percona/percona-server:8.0.46-37.1 (ARM64)               | e41dfb981de432da1a117077e7230008422ab49d6c0e9dd8d17a03d7ffde5dc0 |
| percona/percona-xtrabackup:8.4.0-6.1                     | d135aadaae9e2f947cb2002f982f7b4c6e177b1c7e3d543ef7795aea999feedd |
| percona/percona-xtrabackup:8.4.0-6.1 (ARM64)             | fcf2b3fc20cfbfa6d47ec60cecd881f915beacdae838f994dda984baea825293 |
| percona/percona-xtrabackup:8.0.35-36.1                   | 5416f19ac087e4d8e06eeff63cf1e075dc3b4e45577abbb9c3d87ae1ea3816c5 |
| percona/percona-xtrabackup:8.0.35-36.1 (ARM64)           | b604421b30bdd7ddfbc716220a8f8f32077c12a762d1eae622dcf4e5085b115a |
| percona/percona-mysql-router:8.4.10-10.1                 | 7edd16793022a518842aa6e709582af9175ee9ab145faf11e930f8175f16c588 |
| percona/percona-mysql-router:8.4.10-10.1 (ARM64)         | e3be4405858a4198ecb1265365763de33dc6991bdb811bbc10803a92d06606a0 |
| percona/percona-mysql-router:8.0.46-37.1                 | 826cd7a26e918fc5b75cad6ba19d74b508dd1a73f93e49cfac727f6f40b74a02 |
| percona/percona-mysql-router:8.0.46-37.1 (ARM64)         | d7a835fff71c6fa881d35cc54fb126c4027ccd9692575c6b95c2cd6329915b90 |
| percona/percona-orchestrator:3.2.6-22                    | 384bcf3121f50e9536fc911532386b9b485a52701e1e99ada51a5faf91d667c3 |
| percona/percona-orchestrator:3.2.6-22 (ARM64)            | 7ed29d0cde9396687fa42e1640ac2554125fd3a1e2a9f8d70667bbd00b386703 |
| percona/haproxy:2.8.18-1                                 | 09e4d2ce9e65dc4aec9195e818e6da2041aea1a2bdb04f868d8c42ee81090dbf |
| percona/haproxy:2.8.18-1 (ARM64)                         | 563d84d64e1668cb4f6b2202fbe15a18e0733b48fe963383bb877c9e3a8a0abd |
| percona/percona-toolkit:3.7.1-4                          | 0865492cb600f1092618de63e91ae480606a0459d86e5eb876c7e7fb6e6cdda1 |
| percona/percona-toolkit:3.7.1-4 (ARM64)                  | c0ebb11297c3bd83bbbc7acd9195dfa754e7e9be9da70800d146381a7d652129 |
| percona/pmm-client:3.8.1                                 | a92cfb7f912bd85d8245575c3ee5c423664ad2baedb674d159a87b113dbd4de2 |
| percona/pmm-client:3.8.1 (ARM64)                         | 3fe427c0666337df7613824da5f3b5fb7397e849f70402ac557c1324c5d996e6 |
| percona/percona-server-mysql-operator:1.2.0-binlog-server-0.3.1 | 53336b6ccbe463c255f7ca9caaf9390ceba2b9c7672b91998cbe5f44d84dc4e4 |
| percona/percona-server-mysql-operator:1.2.0-binlog-server-0.3.1 (ARM64) | 361695d2b77443e67aa7f2858e9345cff08967afa3e2a8820d4c5981963fa858 |


--8<-- [end:images]

[Find images for previous versions :octicons-link-external-16:](https://docs.percona.com/legacy-documentation/){.md-button}
