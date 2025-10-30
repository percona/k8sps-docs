# How the Operator works

The Percona Operator for MySQL acts as your assistant in managing databases on Kubernetes. It extends the Kubernetes API with a custom `PerconaServerMySQL` resource. Think of it as a blueprint that defines how you want your MySQL database to look and behave.

Whenever you create or update a `PerconaServerMySQL` Custom Resource, the Operator steps in and handles the hard work for you. It automatically does the following:

1. Creates and manages the necessary Kubernetes resources (StatefulSets, Services, Pods)
2. Ensures your cluster matches the desired state you've defined
3. Monitors the cluster health and automatically recovers from failures
4. Coordinates upgrades and scaling operations

These operations ensure that your actual database environment always matches your request.

Each MySQL node in your cluster contains a complete copy of your data, synchronized across all nodes. 

![image](assets/images/replication.svg)

The recommended configuration is to use at least 3 nodes. Such setup provides high availability — if any node fails, the cluster continues operating normally. Read more about [high-availability](architecture.md#high-availability) 

To keep your data safe and persistent, the Operator uses Kubernetes storage systems called Persistent Volumes (PVs) and PersistentVolumeClaims (PVCs). When you request storage for your database, a PVC automatically finds and attaches available storage for you. If a node fails, the Kubernetes storage system can move your data to another node, making sure your database remains available and your data stays protected.

Ready to get started? Continue to the [quickstart guide](quickstart.md) to deploy your first cluster, or explore the [architecture overview](architecture.md) to understand the inner workings of the Operator. For hands-on steps and best practices, check out [What next?](what-next.md).
