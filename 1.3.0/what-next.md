> For the complete documentation index, see [llms.txt](https://docs.percona.com/percona-operator-for-mysql/1.3.0/llms.txt).

# What’s next?

Congratulations! You’ve successfully completed the getting started guide. Your MySQL cluster is up and running. Now it’s time to prepare it for production use and learn the essential day-to-day operations.

## Immediate next steps

These are the most important tasks to tackle right away:

### 1. Set up automated backups

You’ve created a single backup, but production workloads need automated backup schedules to protect your data continuously.

- [Schedule automatic backups](https://docs.percona.com/percona-operator-for-mysql/1.3.0/backups-scheduled.md) - Configure daily, weekly, or custom backup schedules with retention policies
- [Restore from a backup](https://docs.percona.com/percona-operator-for-mysql/1.3.0/backups-restore.md) - Learn how to restore your data when needed

### 2. Create application users

Your cluster is currently using the root user. For production, you’ll want to create dedicated users for your applications with appropriate permissions.

- [Create application and system users](https://docs.percona.com/percona-operator-for-mysql/1.3.0/users.md) - Set up unprivileged users for your applications with fine-grained access control

### 3. Enable high availability

Ensure your cluster can survive node failures by distributing pods across different nodes.

- [Configure anti-affinity and tolerations](https://docs.percona.com/percona-operator-for-mysql/1.3.0/constraints.md) - Control pod placement to prevent single points of failure

## Production preparation

Once you’ve covered the basics, prepare your cluster for production workloads:

### Security

- [Enable TLS/SSL encryption](https://docs.percona.com/percona-operator-for-mysql/1.3.0/TLS.md) - Secure connections between your applications and the database
- [Configure data-at-rest encryption](https://docs.percona.com/percona-operator-for-mysql/1.3.0/encryption.md) - Protect your data at rest with encryption keys
- [Configure encrypted backups](https://docs.percona.com/percona-operator-for-mysql/1.3.0/backups-encrypted.md) - Protect backup files stored in cloud object storage

### Configure access to your cluster for external applications

- [Configure HAProxy](https://docs.percona.com/percona-operator-for-mysql/1.3.0/haproxy-conf.md) or [MySQL Router](https://docs.percona.com/percona-operator-for-mysql/1.3.0/router-conf.md) - Customize load balancing behavior
- [Expose your cluster](https://docs.percona.com/percona-operator-for-mysql/1.3.0/expose.md) - Configure external access if your applications need it

### Performance and reliability

- [Scale your cluster](https://docs.percona.com/percona-operator-for-mysql/1.3.0/scaling.md) - Add more nodes for better performance or increase resources for existing nodes
- [Configure MySQL options](https://docs.percona.com/percona-operator-for-mysql/1.3.0/options.md) - Tune MySQL settings for your workload requirements
- [Let the Operator tune MySQL automatically](https://docs.percona.com/percona-operator-for-mysql/1.3.0/autoconfig.md) - Calculate a full configuration from your cluster’s resources and workload instead of tuning by hand
- [Fine-tune backups and restores](https://docs.percona.com/percona-operator-for-mysql/1.3.0/backups-fine-tune.md) - Optimize backup performance and customize restore operations

### Monitoring and observability

- [Monitor with Percona Monitoring and Management (PMM)](https://docs.percona.com/percona-operator-for-mysql/1.3.0/monitoring.md) - Set up comprehensive monitoring, alerts, and performance insights beyond the basic setup
- [Persistent logging](https://docs.percona.com/percona-operator-for-mysql/1.3.0/persistent-logging.md) - Retain and rotate logs for troubleshooting.

## Advanced operations

As you become more comfortable with the Operator, explore these advanced features:

- [Add sidecar containers](https://docs.percona.com/percona-operator-for-mysql/1.3.0/sidecar.md) - Extend functionality with custom containers
- [Multi-namespace deployment](https://docs.percona.com/percona-operator-for-mysql/1.3.0/cluster-wide.md) - Configure Operator-wide or namespace-specific deployments

## Learn more

- [Understand the architecture](https://docs.percona.com/percona-operator-for-mysql/1.3.0/architecture.md) - Deep dive into how the Operator works and its components
- [Review all configuration options](https://docs.percona.com/percona-operator-for-mysql/1.3.0/operator.md) - Complete reference for Custom Resource settings
