# What's next?

Congratulations! You've successfully completed the getting started guide. Your MySQL cluster is up and running. Now it's time to prepare it for production use and learn the essential day-to-day operations.

## Immediate next steps

These are the most important tasks to tackle right away:

### 1. Set up automated backups

You've created a single backup, but production workloads need automated backup schedules to protect your data continuously.

- [Configure backup storage](backups-storage.md) - Set up S3 or Azure Blob Storage for your backups
- [Schedule automatic backups](backups-scheduled.md) - Configure daily, weekly, or custom backup schedules with retention policies
- [Restore from backup](backups-restore.md) - Learn how to restore your data when needed

### 2. Create application users

Your cluster is currently using the root user. For production, you'll want to create dedicated users for your applications with appropriate permissions.

- [Create application and system users](users.md) - Set up unprivileged users for your applications with fine-grained access control

### 3. Enable high availability

Ensure your cluster can survive node failures by distributing pods across different nodes.

- [Configure anti-affinity and tolerations](constraints.md) - Control pod placement to prevent single points of failure

## Production preparation

Once you've covered the basics, prepare your cluster for production workloads:

### Security

- [Enable TLS/SSL encryption](TLS.md) - Secure connections between your applications and the database
- [Configure data-at-rest encryption](encryption.md) - Protect your data at rest with encryption keys

### Performance and reliability

- [Scale your cluster](scaling.md) - Add more nodes for better performance or increase resources for existing nodes
- [Configure MySQL options](options.md) - Tune MySQL settings for your workload requirements
- [Expose your cluster](expose.md) - Configure external access if your applications need it
- [Fine-tune backups and restores](backups-fine-tune.md) - Optimize backup performance and customize restore operations

### Monitoring and observability

- [Monitor with Percona Monitoring and Management (PMM)](monitoring.md) - Set up comprehensive monitoring, alerts, and performance insights beyond the basic setup

## Advanced operations

As you become more comfortable with the Operator, explore these advanced features:

- [Configure HAProxy](haproxy-conf.md) or [MySQL Router](router-conf.md) - Customize load balancing behavior
- [Change replication type](change-replication-type.md) - Switch between group replication and asynchronous replication
- [Add sidecar containers](sidecar.md) - Extend functionality with custom containers
- [Multi-namespace deployment](cluster-wide.md) - Configure Operator-wide or namespace-specific deployments

## Learn more

- [Understand the architecture](architecture.md) - Deep dive into how the Operator works and its components
- [Review all configuration options](operator.md) - Complete reference for Custom Resource settings

## Get help

If you run into issues or have questions:

- [Troubleshooting guide](debug.md) - Common issues and how to resolve them
- [Get help](get-help.md) - Community support and resources
