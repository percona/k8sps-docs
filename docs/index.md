# Percona Operator for MySQL based on Percona Server for MySQL

Percona Operator for MySQL is a custom controller that extends Kubernetes to automate the entire lifecycle of [Percona Server for MySQL :octicons-link-external-16:](https://www.percona.com/doc/percona-server/LATEST/index.html) clusters. The Operator makes it much simpler to run and reliably manage databases that traditionally require a lot of manual effort on Kubernetes.

You declare how you want your Percona Server for MySQL cluster to run (e.g., "I need a 3-node Percona Server for MySQL cluster with backups enabled") using a special Kubernetes configuration file called a Custom Resource. The Operator then takes over. It constantly watches your cluster, understands its unique needs, and automatically performs tasks like deployment, scaling, handling failures, managing backups, and coordinating upgrades.

[What's new in version {{release}}](ReleaseNotes/Kubernetes-Operator-for-PS-RN{{release}}.md){.md-button}


!!! note

    Version {{ release }} of the [Percona Operator for MySQL :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator) is **a tech preview release** and it is **not recommended for production environments**. **As of today, we recommend using** [Percona Operator for MySQL based on Percona XtraDB Cluster](https://www.percona.com/doc/kubernetes-operator-for-pxc/index.html), which is production-ready and contains everything you need to quickly and consistently deploy and scale MySQL clusters in a Kubernetes-based environment, on-premises or in the cloud.


