# Percona Operator for MySQL 1.0.0 ({{date.1_0_0}})

[Installation](../System-Requirements.md#installation-guidelines){.md-button}

Percona Operator for MySQL brings production-grade automation to MySQL deployments on Kubernetes. It handles provisioning, scaling, backups, failover, and upgrades using declarative Custom Resources, thus reducing manual effort and human error. With built-in support for Percona XtraBackup, proxies such as HAProxy or MySQL Router and Percona Toolkit, it ensures resilient, secure, and performant MySQL clusters.

## Release highlights

This release marks the **General Availability (GA) of Percona Operator for MySQL using Percona Server for MySQL with the group replication type**. The asynchronous replication has the tech preview status and we don't recommend using it in production yet.

With the GA status of the Operator, you can confidently deploy and run it in production environments, benefiting from long-term maintenance and enterprise-grade reliability.

Alternatively, you may opt for [Percona Operator for MySQL based on Percona XtraDB Cluster](https://www.percona.com/doc/kubernetes-operator-for-pxc/index.html), which is production-ready and contains everything you need to quickly and consistently deploy and scale MySQL clusters in a Kubernetes-based environment, on-premises or in the cloud.

This release focuses on stability and bug fixing, ensuring the Operator is ready for production use. Additionally, it introduces these improvements:

### Seamless Operator lifecycle management on OpenShift OLM

The Operator images are passing official certification for OpenShift. When passed, this unlocks full support for the Operator Lifecycle Manager (OLM) so that you can install, upgrade and manage the Operator's lifecycle directly from the OpenShift console.

What this means for you:

* Simplified installation: Deploy Operators directly from the OpenShift UI with just a few clicks.
* Streamlined updates: Stay current with automatic or manual updates via OLM.
* Enterprise-grade assurance: Certified images meet Red Hat's security and compatibility standards.
* Better integration: Leverage OpenShift-native workflows for lifecycle management, RBAC, and monitoring.
* Scalable operations: Simplify cluster-wide rollouts and reduce manual overhead.

All OpenShift-related features will become available to users as soon as certification is confirmed. Whether you're a platform engineer, DBA, or architect, this advancement will bring you closer to a secure, scalable, and policy-driven infrastructure.

### Streamlined custom configuration usage for backup and restore processes

In previous version we have added the ability to fine-tune backups and restores by defining `xtrabackup`, `xbstream`, and `xbcloud` settings globally via the Custom Resource manifest, or individually via a specific backup / restore manifest. 

In this release we improved how the Operator applies these settings: now individual configuration always takes precedence over global settings. 

With this improvement you have maximum flexibility: you can define consistent default settings for the entire cluster, but still tailor individual backup or restore operations as needed. This way you can optimize performance, troubleshoot, or customize specific scenarios without affecting the global configuration.

### Increased timeouts for read, write and clone operations inside MySQL cluster

To improve reliability of clone operations in asynchronous MySQL clusters, especially when transferring large datasets, we've increased the default timeouts for read,write and clone operations to 3600 seconds. This change helps prevent premature failures caused by network delays or slow disk I/O during large data transfers.

The following timeouts are now set to 3600s by default:

* `BOOTSTRAP_CLONE_TIMEOUT`
* `BOOTSTRAP_READ_TIMEOUT`
* `BOOTSTRAP_WRITE_TIMEOUT`

You can fine-tune the timeout for cloning in your custom resource (CR) using environment variables:

```yaml
spec:
  mysql:
    env:
      - name: BOOTSTRAP_CLONE_TIMEOUT
        value: "3600"
      - name: BOOTSTRAP_READ_TIMEOUT
        value: "3600"
      - name: BOOTSTRAP_WRITE_TIMEOUT
        value: "3600"
```

This update ensures smoother provisioning and bootstrapping of new database nodes, especially in environments with large datasets or variable network conditions.

## Deprecation, rename and removal

* Changed paths for example configuration files for backups and restores. They are now stored in the `deploy/backup/` folder. Adjust your automation worklfows with this new path, if needed.
* The Custom Resource options `spec.pmm.readinessProbes` and `spec.pmm.livenessProbes` have been renamed to the singular `spec.pmm.readinessProbe` and `spec.pmm.livenessProbe`, respectively. Please update your application configurations to use these new field names as needed.

## Known limitations

If you defined several schedules for the same remote backup storage, be aware of the following limitations:

1. **Retention policy conflicts.** The Operator applies retention policies only to the first schedule in your configuration. For example, if you set daily backups to keep 5 copies and monthly backups to keep 3 copies, the Operator will only keep 5 total backups in storage, not 8 as you might expect. However, all backup objects will still appear in `kubectl get ps-backup` output.

2. **Concurrent backup conflicts.** When multiple schedules run simultaneously and write to the same storage path, backups can overwrite each other, resulting in incomplete or corrupted data.

To avoid these issues and ensure each schedule maintains its own retention policy, configure separate storage locations for each schedule. Refer to the [documentation](../backups-scheduled.md#managing-multiple-backup-schedules-in-the-same-storage) for more information and  configuration steps.

## Changelog

### Improvements

* [K8SPS-469](https://perconadev.atlassian.net/browse/K8SPS-469) - Improved log message to display clearer and more informative error messages in case of authorization issues to a backup storage.
* [K8SPS-537](https://perconadev.atlassian.net/browse/K8SPS-537) - Extended the test suite for the automatic update process to include MySQL version 8.4.
* [K8SPS-574](https://perconadev.atlassian.net/browse/K8SPS-574) - Align readiness and liveness probe naming to be in the singular form to correspond to  to the Kubernetes API structure

### Fixed bugs

* [K8SPS-491](https://perconadev.atlassian.net/browse/K8SPS-491) - Percona Operator for MySQL  now automatically generates the secrets object in the format `<cluster-name>-secrets`, if it's not explicitly defined in the Custom resource, preventing common startup errors.

* [K8SPS-492](https://perconadev.atlassian.net/browse/K8SPS-492) - Fixed the issue with the Operator sending the unsupported `Error` event type during the Group Replication cluster startup by sending the `Warning` event type instead.  

* [K8SPS-498](https://perconadev.atlassian.net/browse/K8SPS-498) - Stopped unnecessary updates to the `resourceVersion` field of the cluster objects during its initialization.

* [K8SPS-501](https://perconadev.atlassian.net/browse/K8SPS-501) - Fixed the issue with the Operator failing to update the PVC when expanding database volumes by retrying the operation.

* [K8SPS-517](https://perconadev.atlassian.net/browse/K8SPS-517) - Fixed an issue that prevented MySQL clone operations from completing successfully due to a default 10-second read timeout, which caused "query interrupted" errors. This was resolved by increasing the default read/write timeouts to 3600 seconds (1 hour) for long-running operations and enhancing error handling for better reliability and debugging.

* [K8SPS-518](https://perconadev.atlassian.net/browse/K8SPS-518) - ConfigMap settings were fixed to ensure proper labels are applied when deploying clusters with various replication and router configurations.

* [K8SPS-521](https://perconadev.atlassian.net/browse/K8SPS-521) - Fixed an issue where mysql-shell would overwrite Group Replication options in my.cnf during cluster creation. The operator now parses my.cnf and explicitly passes user-defined settings (like group_replication_single_primary_mode and group_replication_paxos_single_leader) to dba.createCluster(), ensuring user customizations are respected.

* [K8SPS-524](https://perconadev.atlassian.net/browse/K8SPS-524) - Fixed the issue with successful backups displaying the incorrect state description. The state description field is irrelevant for successful backups and is not present.

* [K8SPS-529](https://perconadev.atlassian.net/browse/K8SPS-529) - Removed reconciliation of backups that entered the error state due to underlying configuration issues and keep their state for troubleshooting.

* [K8SPS-533](https://perconadev.atlassian.net/browse/K8SPS-533) - The individual configuration for `xbcloud`, `xbstream` and `xtrabackup` tools specified directly for a backup or a restore object now fully overrides any default arguments set in the cluster's custom resource.

* [K8SPS-535](https://perconadev.atlassian.net/browse/K8SPS-535) - Backup deletion operations no longer display an erroneous failure message when the backup is successfully removed from storage.

* [K8SPS-539](https://perconadev.atlassian.net/browse/K8SPS-539) - Fixed the issue with excessive CPU utilization of the `ps-entrypoint.sh` recovery by adding a backoff mechanism to the file existence check. This improves cluster operation in envionments where CPU resources are a concern.

* [K8SPS-548](https://perconadev.atlassian.net/browse/K8SPS-548) - Improved Group Replication self-healing test and resolved a sporadic failure where a pod would not become ready after a full cluster crash.

* [K8SPS-550](https://perconadev.atlassian.net/browse/K8SPS-550) - Fixed the issue with service accounts defined for HAProxy Pods via Custom Resource not being applied.

* [K8SPS-560](https://perconadev.atlassian.net/browse/K8SPS-560) - Fixed the issue with scheduled backups failing due to conflicting job names when multiple backups run concurrently.

* [K8SPS-564](https://perconadev.atlassian.net/browse/K8SPS-564) - Fixed the issue with both  HAProxy or Router being deployed when both are enabled by validating the configuration and either reporting the error or deploying only one proxy. This prevents unintended dual deployments.

* [K8SPS-565](https://perconadev.atlassian.net/browse/K8SPS-565) - Restores now complete successfully when using an auto-generated secrets name for clusters.

## Supported software

--8<-- [start:software]

The Operator was developed and tested with the following software:

* Percona Server for MySQL 8.4.6-6.1
* Percona Server for MySQL 8.0.43-34.1
* XtraBackup 8.4.0-4.1
* XtraBackup 8.0.35-34.1
* MySQL Router 8.4.6-6.1
* MySQL Router 8.0.43-34.1
* HAProxy 2.8.15
* Orchestrator 3.2.6-18
* Percona Toolkit 3.7.0-2
* PMM Client 3.4.1
* Cert Manager 1.19.1

Other options may also work but have not been tested.

--8<-- [end:software]

## Supported platforms

Percona Operators are designed for compatibility with all [CNCF-certified :octicons-link-external-16:](https://www.cncf.io/training/certification/software-conformance/) Kubernetes distributions. Our release process includes targeted testing and validation on major cloud provider platforms and OpenShift, as detailed below:

--8<-- [start:platforms]

* [Google Kubernetes Engine (GKE) :octicons-link-external-16:](https://cloud.google.com/kubernetes-engine) 1.31 - 1.33
* [Amazon Elastic Container Service for Kubernetes (EKS) :octicons-link-external-16:](https://aws.amazon.com) 1.31 - 1.34
* [OpenShift :octicons-link-external-16:](https://www.openshift.com) 4.16 - 4.20
* [Minikube :octicons-link-external-16:](https://minikube.sigs.k8s.io/docs/) 1.37.0 with Kubernetes v1.34.0

--8<-- [end:platforms]

This list only includes the platforms that the Percona Operators are specifically tested on as part of the release process. Other Kubernetes flavors and versions depend on backward compatibility offered by Kubernetes itself.

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
