# Features

Percona Operator for MySQL is a Kubernetes-native controller that automatically manages the full lifecycle of Percona Server for MySQL clusters. The Operator offloads your teams from manual day-to-day database management operations empowering them to focus on tasks that matter instead.

## Core capabilities

Here's what the Operator brings to your infrastructure:

### High availability and failover

Never lose sleep over database downtime again. The Operator provides robust high availability through:

- Automatic failover with intelligent primary election handled by the Orchestrator
- Multi-node deployments with anti-affinity rules to prevent single points of failure  
- Health monitoring with automatic recovery from node failures
- Zero-downtime upgrades with rolling update strategies

Choose between [group replication](architecture.md#group-replication) (GA) for stronger consistency or [asynchronous replication](architecture.md#asynchronous-replication-tech-preview) (tech preview) for lower latency—both with automatic failover capabilities.

### Automated backup and restore flows

Protect your data with Percona XtraBackup - an enterprise-grade backup solution for hot, non blocking backups. Run:

- Scheduled backups with configurable retention policies
- On-demand backups for critical operations

### Automated scaling and resource management

Scale your database infrastructure effortlessly:

- Horizontal scaling with automatic replica management
- Vertical scaling with resource limit adjustments
- Storage expansion with volume growth capabilities
- Load balancing through HAProxy or MySQL Router
- Resource optimization with intelligent pod placement

### Security and compliance

Keep your data secure with built-in security features:

- Transport encryption with TLS/SSL support
- Data-at-rest encryption with key management integration
- Role-based access control with fine-grained permissions
- Secret management with Kubernetes-native secrets

### Monitoring and observability

Gain deep insights into your database performance:

- Percona Monitoring and Management (PMM) integration for comprehensive monitoring
- Custom metrics and alerting capabilities
- Log aggregation and centralized logging
- Performance insights with query analysis
- Health dashboards for operational visibility

## How Operator works

The Operator extends Kubernetes with custom resources that represent your MySQL cluster's desired state. 

Here's what happens under the hood:

1. You define your cluster requirements in a `PerconaServerMySQL` custom resource
2. The Operator watches for changes and reconciles the actual state with your desired state
3. Kubernetes resources are automatically created and managed (Pods, Services, StatefulSets, etc.)
4. The cluster self-heals by detecting and recovering from failures
5. Updates and scaling happen automatically based on your configuration changes

This declarative approach means you describe what you want, not how to achieve it. The Operator handles all the complex orchestration, ensuring your database cluster always matches your specifications.

[Explore the architecture :material-arrow-right:](architecture.md){ .md-button }

## What's next?

- [Quickstart guides](quickstart.md) - Get up and running in minutes
- [Installation options](kubernetes.md) - Deploy on your preferred platform  
- [Backup and restore](backups.md) - Protect your data with automated backups
- [Monitoring setup](monitoring.md) - Gain visibility into your database performance
- [Security configuration](TLS.md) - Secure your database communications
