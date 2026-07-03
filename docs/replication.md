# Cross-site replication

Enterprises running MySQL at scale often need to span multiple regions, availability zones, or clouds, with a live copy of data in each location. Each site must be a live replica of the primary site, protected from accidental writes and ready to take over traffic during an outage or planned failover. Group Replication keeps nodes in sync within a single cluster, but it does not by itself connect separate clusters across sites.

Cross-site replication closes that gap. It links multiple Group Replication clusters into a single [MySQL InnoDB ClusterSet :octicons-link-external-16:](https://dev.mysql.com/doc/mysql-shell/8.4/en/innodb-clusterset.html) managed through a dedicated `PerconaServerMySQLClusterSet` Custom Resource (`ps-clusterset`). Each site keeps its own `PerconaServerMySQL` cluster of the Group Replication type. The ClusterSet Custom Resource coordinates replication and topology between them.

## Why to use cross-site replication

With cross-site replication, you can achieve the following scenarios:

* **Disaster recovery** — Keep a live replica cluster in a second region that you can promote during an outage.
* **Geo-redundancy** — Protect against regional outages by maintaining independent but synchronized clusters in separate geographic locations, ensuring high data availability and business continuity.
* **Read distribution** — Serve regional read traffic from a local replica cluster while writes stay on the primary cluster.
* **Deployment flexibility** — Run your replica cluster in the same Kubernetes cluster, a different cluster, or outside Kubernetes entirely.

## Architecture

Cross-site replication is implemented via a separate `PerconaServerMySQLClusterSet` Custom Resource.

You declare which clusters participate, which one is the primary, and how replicas receive the data when they join the ClusterSet in the `PerconaServerMySQLClusterSet` Custom Resource manifest. The Operator automates the ClusterSet provisioning and lifecycle management in a similar way it does for a standalone Percona Server for MySQL cluster. It bootstraps the ClusterSet, adds or removes replica sites, refreshes status, and runs switchover when you change the primary.

The Operator uses a dedicated `clusterset` [system user](users.md#system-users) with the grants required for ClusterSet AdminAPI operations. Each cluster must share this user's credentials.

![Cross-site replication architecture](assets/images/innodb-
clusterset.svg)

* The **primary cluster** accepts writes and replicates changes asynchronously to replica clusters over a dedicated replication channel.
* Each **replica cluster** is a full Group Replication cluster (read-only at the ClusterSet level) that receives async replication from the primary cluster's PRIMARY member.
* The **ClusterSet controller** (in the Operator Pod) reconciles the `PerconaServerMySQLClusterSet` Custom Resource, manages the `mysqlshell-runner` Pod, and runs long operations (such as `createReplicaCluster`) as Kubernetes Jobs.

The ClusterSet controller is a **pure orchestrator**: it does not manage Pods in remote clusters. It only needs network reachability to MySQL endpoints and the ClusterSet Custom Resource in one Kubernetes namespace.

The communication in the ClusterSet is done through the MySQL protocol, which enables linking replica clusters deployed in the same or a different Kubernetes environment, or outside Kubernetes on-premises. All replicas must be reachable over the network.

The Operator starts a separate `mysqlshell-runner` Pod with **MySQL Shell (`mysqlsh`)** and uses it to manage the ClusterSet. The `mysqlsh` version must be compatible with the Percona Server for MySQL version you run in your clusters.

## Data recovery modes

When a replica cluster joins the ClusterSet, it must receive the data from the primary. This can be done in two ways:

* Using the `clone` recovery method (default) — A replica cluster to join the ClusterSet must be without any data. MySQL  makes a physical snapshot of the full dataset using the [`CLONE` plugin :octicons-link-external-16:](https://dev.mysql.com/doc/refman/8.0/en/clone-plugin.html) on the primary cluster and transfers it to the replica.
* Using the `incremental` method — Restore the data from the primary cluster on the replica before adding it to the ClusterSet. When it joins the ClusterSet, it catches up the binlog changes that have occurred on the primary.
   
    !!! important
       
        Binlogs must exist on the primary cluster for the incremental recovery mode to work.

### When to use each recovery mode

| Recovery mode | Usage |
| ------------- | ----- |
| CLONE | For small datasets and low-latency networks |
| Incremental | WAN links and multi-TB datasets where a full online clone can take a long time and is expensive to retry. Requires restoring the backup from the primary on the replica before adding it to the ClusterSet |

## TLS for replication channels

Cross-site replication data flows over asynchronous replication channels between the primary and replica clusters. To secure those channels, configure TLS as follows:

1. **Enable TLS on each participating cluster** — Set up transport encryption on every `PerconaServerMySQL` cluster as described in [Transport Layer Security (TLS)](TLS.md). Each site uses its own certificates and Secrets.
2. **Set `spec.sslMode` on the ClusterSet CR** — This tells MySQL Shell how to configure TLS on the ClusterSet replication channels.

### Supported SSL modes

* `Auto` (default) – use TLS when the cluster supports it
* `DISABLED` - disable TLS encryption for the ClusterSet
replication channels.
* `REQUIRED` - enable TLS encryption for the ClusterSet
replication channels.
* `VERIFY_CA` - enable TLS encryption for the ClusterSet `REQUIRED`, and additionally verify the
peer server TLS certificate against the configured Certificate
Authority (CA) certificates. Server certificates do not need to be identical, but they must chain to a **mutually trusted CA** (in practice, often the same CA on both sides)
* `VERIFY_IDENTITY` - same CA trust level as for `VERIFY_CA` mode, plus the **primary** server's certificate must list the endpoint hostname replicas connect to in its SAN.

For cross-region links, prefer `REQUIRED` or a stricter mode over the default `AUTO`.

## Availability

| Requirement | Supported versions |
| ----------- | ------------------ |
| **Operator** | Percona Operator for MySQL **1.2.0** and later |
| **Percona Server for MySQL** | **8.0.27** and later, **8.4** (tested with {{ ps80recommended }} and {{ ps84recommended }}) |
| **MySQL Shell** | `mysqlsh` version must match MySQL endpoints it talks to |
| **Cluster type** | `group-replication` only |
| **Kubernetes** | Same platforms as the Operator — see [Versions compatibility](versions.md) |

## Requirements

Before you create a ClusterSet, ensure the following:

* **Network connectivity** — ClusterSet members are linked by the network address, not Kubernetes references. Clusters can live in different Kubernetes clusters, on-premises or in another cloud but they must be reachable and managed by the Operator.
* **Matching system user credentials** — All system user credentials must be identical across every cluster in the ClusterSet. The primary's user table
is cloned to replicas during `createReplicaCluster`, so
credentials cannot differ per site.
* **Unique endpoint hosts** — Each `host` value must be unique across all clusters in the ClusterSet (CEL-validated at admission). You can use Services or load balancers as endpoints.
* **Group replication-compatible configuration** — Each cluster must be of group replication type and have the CLONE plugin loaded, `gtid_mode=ON`, `enforce_gtid_consistency=ON`, and other [InnoDB ClusterSet instance requirements :octicons-link-external-16:](https://dev.mysql.com/doc/mysql-shell/8.4/en/innodb-clusterset-requirements.html#innodb-clusterset-requirements-mysql-instances). The group replication configuration of Percona Server for MySQL already includes these settings by default.
* **Clean replicas** — Replica clusters must either be clean or have the dataset restored from the primary before joining the ClusterSet.

## Implementation specifics

* **MySQL versioning** — Primary and replicas can have different but compatible MySQL versions. Replication is supported from one release series to the next higher series. For example, from the primary running Percona Server for MySQL 8.0.27+ to the replica running Percona Server for MySQL 8.4.x.
* **Manual bootstrap for replicas** — When you deploy a replica site, specify `spec.mysql.bootstrap.mode: manual` to prevent the replica from starting as a Group Replication cluster. Instead, Pod-0 comes up and waits for the ClusterSet controller to create the group. Pod-1+ do not start until Pod-0 is Ready.
* **Long operations as Jobs** — `createReplicaCluster`, switchover, and cluster removal run as Kubernetes Jobs so the reconcile loop is not blocked for hours during CLONE.
* **Finalizer on delete** — The `percona.com/clusterset-dissolve` finalizer ensures that the ClusterSet dissolves when the `PerconaServerMySQLClusterSet` Custom Resource is removed. Data in underlying clusters is preserved.
* **No automatic switchover** — All switchovers are user-initiated. You must edit the ClusterSet Custom Resource for a planned or a forced failover.

## Known limitations

* **No automatic rejoin to ClusterSet after replication stops** — If replication on a ClusterSet replica is interrupted (for example, if a cluster is paused or stopped), the Operator does not automatically rejoin it to the ClusterSet when it starts. You must restore replication manually. Determine the safe window, connect to the replica cluster and run the `dba.rebootClusterFromCompleteOutage()` command to re-initialize the cluster metadata. Then connect to the primary cluster and run the `dba.getCluster().getClusterSet().rejoinCluster("<innodb_cluster_name>")` command to rejoin the replica.
* **No adopting existing ClusterSets** — The controller only bootstraps a new ClusterSet or refuses if the metadata is inconsistent. You cannot adopt into management any ClusterSet that was created manually with `mysqlsh`.
* **Restoring backups onto replica clusters in a ClusterSet is not supported** — While a replica is part of a ClusterSet, restoring a backup onto it is not supported. If you attempt to do so, the replica will fail to rejoin the ClusterSet afterward. In this case, you must manually reboot the cluster (using `dba.rebootClusterFromCompleteOutage()`) and rejoin it to the ClusterSet from the primary.
* **Backups taken on a ClusterSet cannot be restored on a fresh cluster** — Backups include the ClusterSet metadata that is tied to the specific topology and identities of the clusters within that ClusterSet. Restoring such a backup onto a new, unrelated cluster will lead to inconsistencies or errors, since the metadata will not match the new environment or cluster configuration.
* **Removal is one-way** — After a cluster is removed from a ClusterSet, it cannot be added back to the same ClusterSet.
* **Deletion of ClusterSet object is stuck if the cluster is deleted beforehand** - Ensure your ClusterSet members are running before you delete the ClusterSet object. If the deletion is stuck, edit the ClusterSet object and remove the `percona.com/clusterset-dissolve` finalizer to proceed.
* **Credential rotation on replicas** — The `clusterset` user password is always replicated from the primary; you cannot rotate it independently on replica clusters while they are ClusterSet members.
* **Minimum replica size** — A replica Group Replication cluster still needs enough members for local high availability (typically 3). Single-node replicas are supported for testing but not recommended for production.

## Deployment

For step-by-step instructions, see [Cross-site replication: setup and use](replication-setup.md).
