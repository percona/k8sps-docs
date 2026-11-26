> For the complete documentation index, see [llms.txt](https://docs.percona.com/percona-operator-for-mysql/1.3.0/llms.txt).

# Features

Percona Operator for MySQL is a Kubernetes-native controller that automatically manages the full lifecycle of Percona Server for MySQL clusters. The Operator offloads your teams from manual day-to-day database management operations empowering them to focus on tasks that matter instead.

## Core capabilities

Here’s what the Operator brings to your infrastructure:

### High availability and failover

Never lose sleep over database downtime again. The Operator provides robust high availability through:

- Automatic failover with intelligent primary election handled by the Orchestrator
- Configurable recovery timeout and policy for async clusters, with zero-data-loss recovery by default and a manual override for emergencies
- Multi-node deployments with anti-affinity rules to prevent single points of failure
- Health monitoring with automatic recovery from node failures
- Zero-downtime upgrades with rolling update strategies

Choose between [group replication](https://docs.percona.com/percona-operator-for-mysql/1.3.0/architecture.md#group-replication) (GA) for stronger consistency or [asynchronous replication](https://docs.percona.com/percona-operator-for-mysql/1.3.0/architecture.md#asynchronous-replication-tech-preview) (tech preview) for lower latency—both with automatic failover capabilities.

### Cross-site replication

Link Group Replication clusters across regions, availability zones, or Kubernetes environments into the InnoDB ClusterSet managed by the Operator. Instead of building custom replication tooling between sites, you apply a `PerconaServerMySQLClusterSet` Custom Resource and let the Operator handle topology lifecycle.

Cross-site replication requires Percona Operator for MySQL 1.2.0 or later and Group Replication clusters on Percona Server for MySQL 8.0.27+ or 8.4. Learn more in the [cross-site replication documentation](https://docs.percona.com/percona-operator-for-mysql/1.3.0/replication.md).

### Automated backup and restore flows

Protect your data with Percona XtraBackup - an enterprise-grade backup solution for hot, non blocking backups. Run:

- Scheduled backups with configurable retention policies
- On-demand backups for critical operations
- [Encrypted backups](https://docs.percona.com/percona-operator-for-mysql/1.3.0/backups-encrypted.md) for compliance-ready protection in cloud object storage

### Automated scaling and resource management

Scale your database infrastructure effortlessly:

- Horizontal scaling with automatic replica management
- Vertical scaling with resource limit adjustments
- Storage expansion with volume growth capabilities
- Load balancing through HAProxy or MySQL Router
- Resource optimization with intelligent pod placement

### Automatic MySQL configuration tuning

Get your cluster production-ready without deep MySQL tuning expertise. Specify the CPU and memory you allocate to MySQL, your workload profile, and the MySQL version. The Operator [automatically calculates and applies the MySQL configuration](https://docs.percona.com/percona-operator-for-mysql/1.3.0/autoconfig.md) for you and recalculates it whenever those resources change, so you pay only for the resources you actually use.

### Security and compliance

Keep your data secure with built-in security features:

- Transport encryption with TLS/SSL support
- Data-at-rest encryption with key management integration
- Encrypted backups for object storage
- [Encrypted binlogs](https://docs.percona.com/percona-operator-for-mysql/1.3.0/backups-pitr.md#binlog-encryption) for point-in-time recovery, without depending on S3 server-side encryption
- Additional trusted CA certificates from your PKI for TLS verification with S3-compatible backup storage (available starting with Operator version 1.3.0)
- Role-based access control with fine-grained permissions
- Secret management with Kubernetes-native secrets
- Orchestrator API authentication for async replication clusters (available starting with Operator version 1.2.0)

### Monitoring and observability

Gain deep insights into your database performance:

- Percona Monitoring and Management (PMM) integration for comprehensive monitoring
- Custom metrics and alerting capabilities
- Logging — Gain insights into MySQL logs even after Pod restarts with [persistent logging](https://docs.percona.com/percona-operator-for-mysql/1.3.0/persistent-logging.md). Configure [log rotation](https://docs.percona.com/percona-operator-for-mysql/1.3.0/logrotate.md) for optimized storage usage.
- Performance insights with query analysis
- Health dashboards for operational visibility

## How Operator works

The Operator extends Kubernetes with custom resources that represent your MySQL cluster’s desired state.

Here’s what happens under the hood:

1. You define your cluster requirements in a `PerconaServerMySQL` custom resource
1. The Operator watches for changes and reconciles the actual state with your desired state
1. Kubernetes resources are automatically created and managed (Pods, Services, StatefulSets, etc.)
1. The cluster self-heals by detecting and recovering from failures
1. Updates and scaling happen automatically based on your configuration changes

This declarative approach means you describe what you want, not how to achieve it. The Operator handles all the complex orchestration, ensuring your database cluster always matches your specifications.

[Explore the architecture](https://docs.percona.com/percona-operator-for-mysql/1.3.0/architecture.md)

## What’s next?

- [Quickstart guides](https://docs.percona.com/percona-operator-for-mysql/1.3.0/quickstart.md) - Get up and running in minutes
- [Installation options](https://docs.percona.com/percona-operator-for-mysql/1.3.0/kubernetes.md) - Deploy on your preferred platform
- [Backup and restore](https://docs.percona.com/percona-operator-for-mysql/1.3.0/backups.md) - Protect your data with automated backups
- [Monitoring setup](https://docs.percona.com/percona-operator-for-mysql/1.3.0/monitoring.md) - Gain visibility into your database performance
- [Security configuration](https://docs.percona.com/percona-operator-for-mysql/1.3.0/TLS.md) - Secure your database communications
- [Cross-site replication](https://docs.percona.com/percona-operator-for-mysql/1.3.0/replication.md) - Link Group Replication clusters across regions and sites
