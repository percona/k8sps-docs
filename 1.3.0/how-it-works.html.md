> For the complete documentation index, see [llms.txt](https://docs.percona.com/percona-operator-for-mysql/1.3.0/llms.txt).

# How the Operator works

The Percona Operator for MySQL acts as your assistant in managing databases on Kubernetes. It extends the Kubernetes API with a custom `PerconaServerMySQL` resource. Think of it as a blueprint that defines how you want your MySQL database to look and behave.

Whenever you create or update a `PerconaServerMySQL` Custom Resource, the Operator steps in and handles the hard work for you. It automatically does the following:

1. Creates and manages the necessary Kubernetes resources (StatefulSets, Services, Pods)
1. Ensures your cluster matches the desired state you’ve defined
1. Monitors the cluster health and automatically recovers from failures
1. Coordinates upgrades and scaling operations

These operations ensure that your actual database environment always matches your request.

Each MySQL node in your cluster contains a complete copy of your data, synchronized across all nodes.

*Image: image*

The recommended configuration is to use at least 3 nodes. Such setup provides high availability — if any node fails, the cluster continues operating normally. Asynchronous clusters can also run with even number of instances (minimum for high availability). Read more about [high availability](https://docs.percona.com/percona-operator-for-mysql/1.3.0/architecture.md#high-availability) and [cluster size limits](https://docs.percona.com/percona-operator-for-mysql/1.3.0/limitations.md#replication-and-topology).

To keep your data safe and persistent, the Operator uses Kubernetes storage systems called Persistent Volumes (PVs) and PersistentVolumeClaims (PVCs). When you request storage for your database, a PVC automatically finds and attaches available storage for you. If a node fails, the Kubernetes storage system can move your data to another node, making sure your database remains available and your data stays protected.

Ready to get started? Continue to the [quickstart guide](https://docs.percona.com/percona-operator-for-mysql/1.3.0/quickstart.md) to deploy your first cluster, or explore the [architecture overview](https://docs.percona.com/percona-operator-for-mysql/1.3.0/architecture.md) to understand the inner workings of the Operator. For hands-on steps and best practices, check out [What next?](https://docs.percona.com/percona-operator-for-mysql/1.3.0/what-next.md).
