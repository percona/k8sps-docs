# Architecture

The Percona Operator for MySQL automates deploying and operating Percona Server for MySQL clusters on Kubernetes. This document explains what components the Operator uses and how they work together to provide a highly available MySQL database. Also, read more about [How the Operator works](how-it-works.md).

## Components

The [StatefulSet :octicons-link-external-16:](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/) deployed with the Operator includes the following components:

* [Percona Server for MySQL :octicons-link-external-16:](https://www.percona.com/doc/percona-server/LATEST/index.html) - a free, fully compatible, enhanced, and open source drop-in replacement for any MySQL database

* [Percona XtraBackup :octicons-link-external-16:](https://www.percona.com/doc/percona-xtrabackup/8.0/index.html) - a hot backup utility for MySQL based servers that doesn’t lock your database during the backup

* [Orchestrator :octicons-link-external-16:](https://github.com/openark/orchestrator) - a replication topology manager for MySQL used when [asynchronous replication :octicons-link-external-16:](https://dev.mysql.com/doc/refman/8.0/en/group-replication-primary-secondary-replication.html) between MySQL instances [is turned on](operator.md#mysqlclustertype),

* [HAProxy :octicons-link-external-16:](https://haproxy.org) - a proxy and load balancing  service serving as the entry point to your database cluster. It is compatible with both [asynchronous replication :octicons-link-external-16:](https://dev.mysql.com/doc/refman/8.0/en/group-replication-primary-secondary-replication.html) and [group replication :octicons-link-external-16:](https://dev.mysql.com/doc/refman/8.0/en/group-replication.html)  between MySQL instances,

* [MySQL Router :octicons-link-external-16:](https://dev.mysql.com/doc/mysql-router/8.0/en/) - a proxy solution which can be used instead of HAProxy for MySQL clusters with [group replication :octicons-link-external-16:](https://dev.mysql.com/doc/refman/8.0/en/group-replication.html) is turned on,

* [Percona Toolkit :octicons-link-external-16:](https://docs.percona.com/percona-toolkit/) - a set of tools for debugging MySQL Pods.

## Replication types

The Operator supports two replication types, each with different characteristics for performance, consistency, and availability. You [choose the replication type](operator.md#mysqlclustertype) when configuring your cluster.

### Asynchronous replication (Beta)

With asynchronous replication, writes complete on the primary instance without waiting for replicas. After a write completes, the primary records the change in its binary log, and replicas apply these changes independently.

![image](assets/images/replication.svg)

**Characteristics:**

* **Performance** - Faster write operations with lower latency
* **Read scaling** - Distribute read requests across multiple replica instances
* **Consistency** - Eventual consistency; replicas may lag behind the primary
* **Failover** - Orchestrator handles automatic primary election and topology recovery
* **Status** - Currently in Beta and not recommended for production use

![image](assets/images/operator.svg)

### Group replication

With group replication, write transactions require consensus from the group before completing. Read transactions can execute on any instance, while writes only occur on the primary.

**Characteristics:**

* **Consistency** - Stronger consistency guarantees (depending on transaction consistency level)
* **Read scaling** - Horizontal scaling of reads with prevention of stale reads
* **Performance** - Slightly slower due to consensus mechanism
* **Failover** - Native group membership protocol handles recovery automatically
* **Limitations** - Maximum of 9 MySQL instances per group; large transactions may cause performance issues
* **Status** - General Availability (GA) and recommended for production use

![image](assets/images/operator-GR.svg)

!!! note

    MySQL documentation may also use the terms "source/replica" instead of "primary/replica".

### Replication comparison

| Feature | Asynchronous replication + HAProxy | Group Replication + HAProxy/MySQL Router |
| --- | --- | --- |
| Writes | Single primary | Single primary |
| Read scaling | Yes | Yes |
| Write scaling | No | No |
| Consistency | Eventual on replicas | Stronger (depending the [Transaction Consistency](https://dev.mysql.com/doc/refman/8.4/en/group-replication-configuring-consistency-guarantees.html)) |
| Latency | Low | Higher (due to sync)
| Failover | Orchestrator elects new primary | Native group membership |
| Max nodes | Higher (practical limits) | 9 per group |
| Proxy | HAProxy | HAProxy or MySQL Router |

**Tip:** Choose Group Replication for stronger consistency and read scaling; choose asynchronous replication for lower write latency and simpler topology when it reaches GA status.

You can change the replication type if needed. Refer to the [Change replication type](change-replication-type.md) guide for step-by-step instructions. Note that replication type change is not supported on a running cluster.

## High availability

The Operator provides high availability through multiple layers of protection:

### Pod distribution

The Operator uses [node affinity](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity) to distribute Percona Server for MySQL instances across separate worker nodes when possible. This prevents a single node failure from taking down multiple database instances.

### Automatic recovery

If a node fails, Kubernetes automatically reschedules the affected Pod on another healthy node. The Operator then:

* With **asynchronous replication**: Orchestrator detects the failure, promotes a healthy replica to primary, and updates the replication topology.

* With **group replication**: The native group membership protocol automatically handles member removal, primary election, and topology recovery.

### Client connectivity

Clients connect through HAProxy or MySQL Router, which automatically route traffic to healthy MySQL instances. These proxies detect failures and redirect connections away from failed nodes, ensuring your applications always connect to available database instances.

## Proxy solutions

The proxy you use depends on your replication type and requirements:

* **HAProxy** - Works with both asynchronous replication and group replication. Provides load balancing, health checks, and connection pooling.

* **MySQL Router** - Available only for group replication. Offers intelligent routing, connection pooling, and read-write splitting capabilities.

For configuration details, see:

* [HAProxy configuration](haproxy-conf.md)
* [MySQL Router configuration](router-conf.md)

## What to read next

Now that you understand the architecture, explore these topics:

* [Operator configuration and Custom Resources](operator.md) - Learn how to configure your cluster
* [Backups](backups.md) - Understand backup and restore operations
* [Scaling](scaling.md) - Scale your cluster horizontally or vertically
* [High availability configuration](constraints.md) - Configure anti-affinity and pod distribution
* [Updating and upgrades](update.md) - Keep your cluster up to date
