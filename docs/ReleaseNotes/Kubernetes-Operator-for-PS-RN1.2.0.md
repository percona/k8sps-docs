# Percona Operator for MySQL 1.2.0 ({{date.1_2_0}})

[Installation](../System-Requirements.md#installation-guidelines){.md-button}

Percona Operator for MySQL brings production-grade automation to MySQL deployments on Kubernetes. It handles provisioning, scaling, backups, failover, and upgrades using declarative Custom Resources, thus reducing manual effort and human error. With built-in support for Percona XtraBackup, proxies such as HAProxy or MySQL Router, and Percona Toolkit, it ensures resilient, secure, and performant MySQL clusters.

## Release highlights

This release delivers key features such as cross-site replication, encrypted backups, and automated storage resizing, which harden the Operator for production use. Additionally, it improves security with Orchestrator API authentication and Vault encryption secret validation, and includes a bunch of improvements for day-to-day operations.

### Cross-site replication for Group Replication clusters

Until now, each Percona Server for MySQL cluster stood on its own. That worked well for high availability within a cluster where group replication keeps cluster nodes in sync. But to scale and span MySQL geographically for disaster recovery, migration or read distribution, you had to build and maintain custom tooling outside the Operator to interconnect sites and replicate data between them.

Cross-site replication closes that gap by linking Group Replication clusters into a [MySQL InnoDB ClusterSet :octicons-link-external-16:](https://dev.mysql.com/doc/mysql-shell/8.4/en/innodb-clusterset.html). You manage the topology declaratively from Kubernetes with a new `PerconaServerMySQLClusterSet` Custom Resource where you declare which clusters participate, which one is the primary, and how replicas receive data when they join the ClusterSet.

The Operator automates the ClusterSet provisioning and lifecycle
management in a similar way it does for a standalone Percona
Server for MySQL cluster. It bootstraps the ClusterSet, adds or
removes replica clusters, refreshes status, and runs switchover
when you change the primary. Because management runs over the MySQL protocol, replica clusters can run in the same Kubernetes cluster, a different cluster, or outside Kubernetes entirely.

With cross-site replication, you gain:

* Faster recovery — promote a live replica in a second region during an outage instead of restoring from backup alone.
* Regional read scaling — serve read traffic locally while writes stay on the primary.
* Unified operations — one Custom Resource and the same declarative model you already use for a single cluster.

Learn more about the workflow, setup and usage in the [cross-cluster replication documentation](../replication.md).

### Encrypted backups

You can now encrypt your backup data with Percona Operator for MySQL, so backup files stored in S3, GCS, or Azure are protected at rest. This helps you meet compliance requirements without adding external encryption tools or changing how you run scheduled and on-demand backups.

Encrypted backups are supported for both Group Replication and asynchronous replication cluster types.

The Operator uses Percona XtraBackup’s native encryption and automates the full workflow for you. You create a Kubernetes Secret with the encryption key and reference it in the cluster Custom Resource either on the global level or per storage. The storage-level setting takes precedence. The Operator uses that Secret to encrypt the backup stream during backup and to decrypt it automatically during in-place restore on the same cluster. 

For a restore on a new cluster or in a different Kubernetes environment, provide the same encryption key in the restore resource, because the Operator has no access to Secrets from the source cluster. **The key used for the restore must match the key used to encrypt the backup**. If the key is lost, the backup cannot be recovered.

The default encryption algorithm is **AES256**. If your security policy requires a different cipher or you want to tune performance, you can override the algorithm and related settings through Percona XtraBackup options in `containerOptions.args.xtrabackup`.

To learn more about encrypted backups, read our [documentation](../backups-encrypted.md).

### Automatic storage resizing

Starting with version 1.2.0, the Operator can automatically resize Persistent Volume Claims (PVCs) for Percona Server for MySQL Pods based on your configured thresholds. The Operator monitors storage usage and when it exceeds the defined threshold, triggers resizing until it reaches the maximum storage size. 

This improvement gives you:

* Fewer outages from full disks because storage grows with demand
* Less guesswork in capacity planning and fewer last-minute fixes
* Lower operational effort for developers and platform engineers
* Cost control by expanding only when needed
* A more predictable environment so teams can focus on delivery

To enable automatic storage resizing, edit the Custom Resource manifest as follows:

```yaml
spec:
  storageScaling:
    enableVolumeScaling: true
    autoscaling:
      enabled: true
      triggerThresholdPercent: 80
      growthStep: 2Gi
      maxSize: "10Gi"
```

Learn more about the workflow and troubleshooting tips in our [documentation](../scaling.md#scale-storage).

### Delegate PVC resizing to an external autoscaler

You can now configure the Operator to use an external storage autoscaler instead of its own resizing logic. This ability may be useful for organizations needing centralized, advanced, or cross-application scaling policies.

To use an external autoscaler, set the `spec.storageScaling.enableExternalAutoscaling` option to `true` in the Custom Resource manifest.

```yaml
spec:
  storageScaling:
    enableExternalAutoscaling: true
```

### Connection details exposed in the user Secret

Connecting applications to your cluster no longer means hunting down endpoints and credentials across Services and Secrets. With this release, the Operator creates and maintains a dedicated Secret for a `root` user that gives your application developers and administrators a single, reliable source of connection information. The Secret name follows the format `<cluster-name>-psuser-root` (`ps-cluster1-psuser-root` by default).

The Secret is owned by the Operator and updated on every reconciliation, so you always get current values without manual upkeep. The `host`, `port`, and `uri` fields point to the direct MySQL primary Service and are automatically updated when failover moves the primary to another Pod.

If you have enabled HAProxy or MySQL Router, the Secret also includes `proxy-host`, `proxy-port`, and `proxy-uri` values, so applications can connect through your proxy without extra configuration. These fields are generic — they do not reveal which proxy technology is in use.

When you expose the proxy with a `LoadBalancer` Service type and an external IP is assigned, the Secret adds `proxy-external-host`, `proxy-external-port`, and `proxy-external-uri` for connections from outside the cluster.

You can mount this Secret in your application Pods, reference it in your CI/CD pipeline, or use it with External Secrets. However you consume credentials today, you now have everything in one place.

### Configure binlog settings in the restore object for point-in-time recovery

You can now specify binlog storage directly in the `PerconaServerMySQLRestore` object when performing point-in-time recovery to a new cluster. Instead of configuring Binlog Server on the target cluster just to replay binary logs from the source environment, you define the binlog location alongside your existing `backupSource` settings. This simplifies the cross-cluster point-in-time recovery configuration as a single restore manifest carries everything needed for the operation.

When you trigger the restore, the Operator starts a temporary Binlog Server using those settings, uses it to locate and fetch the required binlogs from the object storage, and removes it when the restore completes. 

This improvement makes the restore path straightforward. By separating binlog collection on the source cluster from binlog access during restore on the target, the Operator makes disaster recovery and migration scenarios much easier to plan and execute.

Point-in-time recovery remains a tech preview feature. We do not recommend using it in production environments yet, but we encourage you to try this workflow in staging or test clusters and share your feedback.

Read more about point-in-time recovery and restore to a new cluster in our [documentation](../backups-restore-to-new-cluster.md#restore-with-point-in-time-recovery).

### Disable NodePort allocation for LoadBalancer Services

By default, Kubernetes assigns a `NodePort` behind every `LoadBalancer` Service, even when the underlying load balancer does not require it.

With this release, you can now turn off `NodePort` allocation for the `LoadBalancer` Services created by the Operator. Update your cluster Custom Resource with the following configuration:

```yaml
spec:
  expose:
    type: LoadBalancer
    allocateLoadBalancerNodePorts: false
```

This setting keeps the `LoadBalancer` Service behavior intact while preventing Kubernetes from reserving `NodePorts`. It's useful when:

* Your load balancer implementation doesn't rely on NodePorts
* You want to reduce the attack surface by avoiding unintended node level exposure
* You run many LoadBalancer services and want to avoid port exhaustion

### Independent resource configuration for HAProxy sidecar containers

HAProxy Pods include the `mysql-monit` sidecar, a lightweight DNS-polling container that monitors MySQL endpoints. Previously, it inherited resource requests and limits from the main HAProxy container. Since the sidecar needs far fewer resources than HAProxy itself, it was over-provisioned.

Now you can configure the resource requests and limits for each HAProxy sidecar container independently. Use the `spec.proxy.haproxy.sidecarResources` subsection in the Custom Resource and specify the required values for each sidecar:

```yaml
proxy:
  haproxy:
    sidecarResources:
      mysql-monit:
        requests:
          cpu: 50m
          memory: 64Mi
        limits:
          cpu: 100m
          memory: 128Mi
```

This improvement helps you use cluster resources more efficiently and thereby lower your infrastructure costs.

### Vault encryption secret validation

The Operator now validates the Vault Secret when you enable data-at-rest encryption with HashiCorp Vault. If the Secret is missing or invalid, you see a clear error in the cluster status right away, so you can fix the configuration without digging through Pod logs.

With this validation, you can now deploy Vault and the database cluster together, such as using Helm integration charts. You can define the Secret reference up front and let the Operator wait until the Secret is present and valid before continuing cluster setup.

Read more about [configuring data-at-rest encryption with Vault](../encryption-setup.md).

### Improve operational efficiency with the support for concurrent cluster reconciliation

Reconciliation is a Kubernetes mechanism to keep your cluster in sync with its desired state. Previously, the Operator ran only one reconciliation loop at a time. This sequential processing meant that other clusters managed by the same Operator had to wait for the current reconciliation to complete before receiving updates.

With this release, the Operator supports concurrent reconciling and can process several clusters simultaneously. You can define the maximum number of concurrent reconciles with the `MAX_CONCURRENT_RECONCILES` environment variable for the Operator deployment.

This enhancement significantly improves scalability and responsiveness, especially in multi-cluster environments.

### Configurable DNS suffix for Operator connections

You can now specify a custom DNS suffix that the Operator uses when it generates service names. This is useful when the Operator runs in a vcluster or in a cluster with a custom DNS configuration. In those setups, the default `cluster.local` suffix can cause incorrect domain name resolution and, as a result, failed connections to external services such as PMM. By setting the `clusterServiceDNSSuffix` in the Custom Resource to your cluster’s DNS suffix, the Operator generates hostnames that match your DNS configuration. This ensures the service discoverability and correct communication between workloads.

### Secure Orchestrator API access with authentication

The Orchestrator HTTP API is the control plane for your MySQL clusters with asynchronous replication. It handles failovers, topology changes, and other critical operations.

Starting with this release, the Orchestrator API requires authentication. Clients must present valid user credentials to connect, and unauthenticated requests are rejected. 

The Operator handles authentication automatically for its own API calls, reading credentials from the mounted secret, so day-to-day cluster management continues to work as before. For custom integrations or scripts that call the Orchestrator API directly, you will need to include the appropriate credentials.

This change hardens your deployment by ensuring only authorized callers can initiate failover or topology operations. As a result, you have a stronger protection against accidental or malicious disruption of your MySQL cluster.

### Fine-tune Orchestrator failover behavior

Until now, you could not adjust the Orchestrator behavior beyond the Operator defaults. This release makes the `spec.orchestrator.configuration` field effective, so you can tune failover settings per cluster directly in the Custom Resource.

Provide Orchestrator options as a JSON string. For example, with the `FailMasterPromotionOnLagMinutes` option, you can control how long Orchestrator waits before promoting a new primary when replication is lagging. Using the `RecoveryPeriodBlockSeconds` option, define how long to block recovery after a failover. 

```yaml
spec:
  orchestrator:
    enabled: true
    configuration: '{"FailMasterPromotionOnLagMinutes": 30, "RecoveryPeriodBlockSeconds": 300}'
```

The Operator merges your settings into the Orchestrator configuration. When you change the `spec.orchestrator.configuration` field, Orchestrator Pods restart in a rolling fashion to apply the new settings.

Options that the Operator manages itself such as Raft topology, topology TLS, HTTP authentication, failover hooks, alias detection queries, and storage paths are reserved and ignored if you set them, so cluster automation continues to work reliably.

### Improved monitoring for clusters in multi-region or multi-namespace deployments in PMM

Now you can define a custom name for your clusters deployed in different data centers. This name helps Percona Management and Monitoring (PMM) Server to correctly recognize clusters as connected and monitor them as one deployment. Similarly, PMM Server identifies clusters deployed with the same names in different namespaces as separate ones and correctly displays performance metrics for you on dashboards.

To assign a custom name, define this configuration in the Custom Resource manifest for your cluster:

```yaml
spec:
  pmm:
    customClusterName: testClusterName
```

### Percona Server for MySQL clusters 8.4 have NUMA disabled by default

`innodb_numa_interleave` is a MySQL configuration variable that spreads memory allocation across multiple NUMA (Non Uniform Memory Access) nodes. MySQL 8.4 turns this setting on by default to improve performance on servers with NUMA architecture, particularly when using a large InnoDB buffer pool.

In Kubernetes, containers are not allowed to modify memory allocation policies due to common security restrictions. When MySQL tries to enable NUMA interleaving, Kubernetes blocks the request, which can lead to warnings or confusing log messages.

Because most cloud servers for Kubernetes use servers with only a single NUMA node, this MySQL setting provides no performance benefit in containerized environments. To keep MySQL behavior predictable and reduce unnecessary noise, the Operator now sets `innodb_numa_interleave` to `OFF` by default when it deploys Percona Server for MySQL 8.4. This reduces false alarms, and ensures MySQL runs smoothly in hardened Kubernetes environments.

You can still enable NUMA interleaving for your Percona Server for MySQL by passing custom MySQL options through the Operator. Be sure you understand the implications, as this requires a Kubernetes environment that allows NUMA policies.

### Documentation updates

Updated the README in the Helm chart to include the all available options.

## Deprecation, rename and removal

### Deprecated options

The `spec.enableVolumeExpansion` option is deprecated. It remains working for backward compatibility but it will be removed in version 1.5.0. Use the `spec.storageScaling.enableVolumeScaling` option instead.

## Known limitations

### Binlog Server image incompatibility notice

The new version of the Binlog Server image included in this release is not compatible with the previous version. 

To upgrade the Binlog Server you must start a fresh binlog collection. Here's how to do it:

1. Stop point-in-time recovery binlog collection
2. Create a new full backup
3. Change the binlog storage settings in your cluster configuration. It can be a new bucket or a new prefix for the existing bucket
4. Update the Binlog Server image
5. Re-enable point-in-time recovery


## CRD changes

* A new CRD `PerconaServerMySQLClusterSet` is added

## Changelog

### New Features

* [K8SPS-127](https://perconadev.atlassian.net/browse/K8SPS-127) - Added automatic storage scaling that monitors PVC usage and triggers resizing when usage crosses your configured threshold. This helps prevent outages from full disks and reduces manual capacity planning by expanding storage only when it is needed.

* [K8SPS-409](https://perconadev.atlassian.net/browse/K8SPS-409) - Added encrypted backups to ensure backup data stored in S3, GCS, or Azure is protected at rest with a customer-controlled key.

* [K8SPS-496](https://perconadev.atlassian.net/browse/K8SPS-496) - Added the ability to disable NodePort allocation for LoadBalancer Services created by the Operator when your load balancer does not need them.

* [K8SPS-508](https://perconadev.atlassian.net/browse/K8SPS-508) - Added cross-site replication for Group Replication clusters with declarative topology management from Kubernetes via a new `PerconaServerMySQLClusterSet` Custom Resource. 

* [K8SPS-512](https://perconadev.atlassian.net/browse/K8SPS-512) - Added HAProxy version reporting in the cluster status so proxy version information is available from the start of the cluster lifecycle. This ensures telemetry and monitoring integrations receive accurate HAProxy version data instead of an empty value.

* [K8SPS-627](https://perconadev.atlassian.net/browse/K8SPS-627) - Added the `pmm.customClusterName` option so you can assign a custom name to clusters monitored by Percona Monitoring and Management (PMM). PMM can now correctly group source and replica clusters across regions or namespaces as a single deployment on dashboards.

* [K8SPS-689](https://perconadev.atlassian.net/browse/K8SPS-689) - Added a dedicated root user Secret that exposes connection details for your cluster in a single, operator-maintained resource. 

### Improvements

* [K8SPS-19](https://perconadev.atlassian.net/browse/K8SPS-19) - Enabled authentication for the Orchestrator HTTP API so only authorized clients can trigger failovers or topology changes. The Operator handles credentials automatically for its own calls, while custom scripts that access the API directly must provide valid credentials.

* [K8SPS-434](https://perconadev.atlassian.net/browse/K8SPS-434) - Introduce the ability to configure the maximum number of concurrent reconciles via an environment variable so that the Operator can continue reconciling other clusters while an upgrade is in progress. This improves responsiveness in multi-cluster environments where a long-running upgrade previously stalled all other reconciliation work.

* [K8SPS-46](https://perconadev.atlassian.net/browse/K8SPS-46) - Added the ability to pass custom Orchestrator configuration to the Operator without changing Operator defaults.

* [K8SPS-487](https://perconadev.atlassian.net/browse/K8SPS-487) - Improved Vault encryption Secret handling by validating the Secret when data-at-rest encryption is enabled and reporting clear status errors when it is missing or invalid. This lets you deploy Vault and the database cluster together and see configuration problems immediately instead of digging through Pod logs.

* [K8SPS-497](https://perconadev.atlassian.net/browse/K8SPS-497) - Improved graceful shutdown of the pt-heartbeat sidecar by handling SIGTERM in the entrypoint script. MySQL Pods now terminate faster during deletion or rolling updates instead of waiting for the full termination grace period while heartbeat keeps running.

* [K8SPS-503](https://perconadev.atlassian.net/browse/K8SPS-503) - Improved Group Replication bootstrap logging to reflect clone-based recovery when `group_replication_clone_threshold` requires it. Bootstrap logs now match the actual recovery method, making troubleshooting less confusing for users.

* [K8SPS-525](https://perconadev.atlassian.net/browse/K8SPS-525) - Added timestamps to failed backup Pod logs so you can tell whether a log entry belongs to the failed backup job or an earlier run. This makes it easier to correlate backup failures with the correct attempt when reviewing Pod or sidecar logs.

* [K8SPS-716](https://perconadev.atlassian.net/browse/K8SPS-716) - Added ability to specify binlog storage through the `backupSource` field in the `PerconaServerMySQLRestore` object. You can configure point-in-time recovery to a new cluster from a single restore manifest without pre-configuring binlog storage on the target cluster.

* [K8SPS-742](https://perconadev.atlassian.net/browse/K8SPS-742) - Added independent resource configuration for the `mysql-monit` sidecar container in HAProxy Pods via `spec.proxy.haproxy.sidecarResources`. You can set appropriate CPU and memory limits for the lightweight monitoring sidecar without over-provisioning it and save on infrastructure costs.

### Bug Fixes

* [K8SPS-296](https://perconadev.atlassian.net/browse/K8SPS-296) - Improved the logging behavior for unhandled errors and stack traces that appeared when changing passwords in asynchronous replication clusters. Password rotation now completes cleanly without noisy reconciler errors in the Operator logs.

* [K8SPS-454](https://perconadev.atlassian.net/browse/K8SPS-454) - Fixed an issue where MySQL cluster primary selection failed after a minor version upgrade, leaving all instances read-only with no primary. The Operator now handles post-upgrade topology recovery correctly so the cluster regains a writable primary. (Thank you Alexander Kuleshov for reporting this issue)

* [K8SPS-607](https://perconadev.atlassian.net/browse/K8SPS-607) - Fixed reconciler errors that flooded Operator logs after deleting a `PerconaServerMySQLRestore` object. The restore controller now stops reconciling gracefully once the restore resource is removed.

* [K8SPS-638](https://perconadev.atlassian.net/browse/K8SPS-638) - Fixed an issue where the Group Replication plugin and related configuration were loaded even when `spec.mysql.clusterType` was set to `async`. Asynchronous clusters no longer show Group Replication settings in Pod specs, logs, or configuration that were never requested.

* [K8SPS-680](https://perconadev.atlassian.net/browse/K8SPS-680) - Fixed an issue where the `mysql-0` Pod could remain stuck in Terminating state until the termination grace period expired when deleting a cluster. Cluster deletion now completes promptly on affected platforms.

* [K8SPS-682](https://perconadev.atlassian.net/browse/K8SPS-682) - Fixed an issue where the default enablement of NUMA interleaving in MySQL 8.4 caused container deployment errors under hardened security policies. The Operator now correctly restricts this option inside host VMs where MPOL_INTERLEAVE limits are active to guarantee pod initialization stability.

* [K8SPS-683](https://perconadev.atlassian.net/browse/K8SPS-683) - Fixed the SmartUpdate behavior so that the Operator performs an explicit switchover before updating the primary Pod instead of deleting it directly. This applies to both Group Replication and asynchronous replication and reduces disruption during rolling upgrades.

* [K8SPS-686](https://perconadev.atlassian.net/browse/K8SPS-686) - Fixed an issue where scheduled backups could start while a cluster was still initializing after a restore with `unsafeFlags.backupNonReadyCluster` enabled. Backups now wait until the database is ready again after restore completes.

* [K8SPS-699](https://perconadev.atlassian.net/browse/K8SPS-699) - Fixed incremental backup restore when a failed backup exists in the chain by verifying the incremental chunk's completeness when building the restore chain. Failed or incomplete incremental backups are now skipped to ensure the restore succeeds.

* [K8SPS-707](https://perconadev.atlassian.net/browse/K8SPS-707) - Improved validation for the `spec.incrementalBaseBackupName` field to prevent specifying an incremental backup as the base one. The Operator now rejects invalid base backup references instead of creating an unsupported nested incremental chain.

* [K8SPS-709](https://perconadev.atlassian.net/browse/K8SPS-709) - Fixed binlog server crashes when an S3-compatible bucket accumulated a very large number of objects over sustained operation. The Operator handles large binlog inventories more reliably so point-in-time recovery does not require manual bucket cleanup and Pod recreation. 

* [K8SPS-739](https://perconadev.atlassian.net/browse/K8SPS-739) - Fixed password propagation for MySQL Router clusters by using `Router.Size` instead of `HAProxy.Size` in the passwords-propagated check. Router-based deployments now receive credentials on all database Pods as intended. (Thank you user @jackiesre721 for contribution)

* [K8SPS-741](https://perconadev.atlassian.net/browse/K8SPS-741) - Fixed a race when a partially pre-created user Secret caused the Operator to copy incomplete credentials to the internal Secret before auto-generating missing system user passwords. MySQL Pods now start reliably even when the user-supplied Secret contains only a subset of required keys.

* [K8SPS-744](https://perconadev.atlassian.net/browse/K8SPS-744) - Fixed an issue where a custom `replica_parallel_workers` value in the cluster configuration was overridden to the default during bootstrap. The Operator now preserves your configured parallel applier thread count instead of resetting it to default value.

* [K8SPS-751](https://perconadev.atlassian.net/browse/K8SPS-751) - Fixed Version Service request errors when `spec.upgradeOptions.apply` was not set in the Custom Resource. Clusters with telemetry enabled no longer generate repeated HTTP 500 errors against the version check endpoint on every reconcile loop.

* [K8SPS-755](https://perconadev.atlassian.net/browse/K8SPS-755) - Fixed AutoRecovery bootstrap order so the Operator does not bootstrap `mysql-0` first when another Pod was the Group Replication primary before a full cluster crash. Recovery now respects the correct member order to avoid data loss after quorum loss.

* [K8SPS-760](https://perconadev.atlassian.net/browse/K8SPS-760) - Fixed an Operator panic when `spec.backup` was omitted from the Custom Resource entirely. Clusters without a backup section now reconcile normally instead of crashing the controller. (Thank you Wilfried ROSET for contributing to this issue)

## Supported software

--8<-- [start:software]

The Operator was developed and tested with the following software:

* Percona Server for MySQL 8.4.10-10.1
* Percona Server for MySQL 8.0.46-37.1
* XtraBackup 8.4.0-6.1
* XtraBackup 8.0.35-36.1
* MySQL Router 8.4.10-10.1
* MySQL Router 8.0.46-37.1
* HAProxy 2.8.18-1
* Orchestrator 3.2.6-22
* Percona Toolkit 3.7.1-3
* PMM Client 3.8.1
* Cert Manager 1.19.1
* Percona Binlog Server 0.3.1

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
| percona/percona-server-mysql-operator:1.2.0             | a9ab659068574c247151427178dd05ea9cf11a3789acc0b84a3cb6713a7916eb |
| percona/percona-server-mysql-operator:1.2.0 (ARM64)     | 482d6757d2d7697889e2538c5b229aa4253a936cc08257860ed18357a05b82af |
| percona/percona-server:8.4.10-10.1                       | d24391a363426239220c35b9707d6b26ce7522ac27abe55689baebfb48bd9fb3 |
| percona/percona-server:8.4.10-10.1 (ARM64)               | 70f6c4d01b5807737cdd423ab32af1feb1d00513b5420a84361773b167aeca87 |
| percona/percona-server:8.0.46-37.1                       | a9bca94cb483502b03a54866d15c597b5043ee95d95370e8dcc7253c202e096b |
| percona/percona-server:8.0.46-37.1 (ARM64)               | c3cf8d599e1e8fdcf4f9a178e0d65efd2e3d07ea61f127a109e928917e155542 |
| percona/percona-xtrabackup:8.4.0-6.1                     | d135aadaae9e2f947cb2002f982f7b4c6e177b1c7e3d543ef7795aea999feedd |
| percona/percona-xtrabackup:8.4.0-6.1 (ARM64)             | fcf2b3fc20cfbfa6d47ec60cecd881f915beacdae838f994dda984baea825293 |
| percona/percona-xtrabackup:8.0.35-36.1                   | dbe8749e015dd363c530660fd9b7c01b2d5feddc30709dbc84a26714dc162423 |
| percona/percona-xtrabackup:8.0.35-36.1 (ARM64)           | fad27bd8e9bc4840653999d67401af63504b29af1038edbb023b276ac0688bab |
| percona/percona-mysql-router:8.4.10-10.1                 | 7edd16793022a518842aa6e709582af9175ee9ab145faf11e930f8175f16c588 |
| percona/percona-mysql-router:8.4.10-10.1 (ARM64)         | e3be4405858a4198ecb1265365763de33dc6991bdb811bbc10803a92d06606a0 |
| percona/percona-mysql-router:8.0.46-37.1                 | 7ee5b442c19b3bd8cbfd0177a3bfcb93071ad0016d0df7ded35ca06296656613 |
| percona/percona-mysql-router:8.0.46-37.1 (ARM64)         | c47751f9f436f0239145b1c369d6c5eaf33695036dfcea2621da1eae30191eaa |
| percona/percona-orchestrator:3.2.6-22                    | 384bcf3121f50e9536fc911532386b9b485a52701e1e99ada51a5faf91d667c3 |
| percona/percona-orchestrator:3.2.6-22 (ARM64)            | 7ed29d0cde9396687fa42e1640ac2554125fd3a1e2a9f8d70667bbd00b386703 |
| percona/haproxy:2.8.18-1                                 | 09e4d2ce9e65dc4aec9195e818e6da2041aea1a2bdb04f868d8c42ee81090dbf |
| percona/haproxy:2.8.18-1 (ARM64)                         | 563d84d64e1668cb4f6b2202fbe15a18e0733b48fe963383bb877c9e3a8a0abd |
| percona/percona-toolkit:3.7.1-3                          | 7fd2092b0ac8addf44163a5a7e1999acf5ae34ccffe77aeb005aa6ea8a8cfc5d |
| percona/percona-toolkit:3.7.1-3 (ARM64)                  | afa0a0c7826433071da8f16077830977522240f03959e0b57db14ecad2357cca |
| percona/pmm-client:3.8.1                                 | a92cfb7f912bd85d8245575c3ee5c423664ad2baedb674d159a87b113dbd4de2 |
| percona/pmm-client:3.8.1 (ARM64)                         | 3fe427c0666337df7613824da5f3b5fb7397e849f70402ac557c1324c5d996e6 |
| perconalab/percona-binlog-server:0.3.1                   | 53336b6ccbe463c255f7ca9caaf9390ceba2b9c7672b91998cbe5f44d84dc4e4 |
| perconalab/percona-binlog-server:0.3.1 (ARM64)           | 361695d2b77443e67aa7f2858e9345cff08967afa3e2a8820d4c5981963fa858 |


--8<-- [end:images]

[Find images for previous versions :octicons-link-external-16:](https://docs.percona.com/legacy-documentation/){.md-button}
