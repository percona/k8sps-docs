> For the complete documentation index, see [llms.txt](https://docs.percona.com/percona-operator-for-mysql/1.3.0/llms.txt).

# Install Percona Server for MySQL on Minikube

[Minikube](https://github.com/kubernetes/minikube) lets you run a Kubernetes cluster locally without a cloud provider. It works on Linux, Windows, and macOS using a hypervisor like VirtualBox, KVM/QEMU, VMware Fusion, Hyper-V, or Docker. This makes it perfect for testing the Operator before deploying it in a cloud or in production

## Prerequisites

Before you begin, you need to [install Minikube](https://kubernetes.io/docs/tasks/tools/install-minikube/) on your system. The installation includes three components:

1. **kubectl** - the Kubernetes command-line tool
1. **A hypervisor** - if you don’t already have one installed
1. **Minikube** - the Minikube package itself

After installing Minikube, start it with increased resources to ensure the Operator runs smoothly:

```bash
minikube start --memory=4096 --cpus=3
```

This command downloads the necessary virtualized images, then initializes and starts your local Kubernetes cluster. The `--memory=4096` and `--cpus=3` parameters allocate more resources to the virtual machine, which helps the Operator run reliably.

Optional: Kubernetes Dashboard

You can optionally start the Kubernetes dashboard to visualize your cluster. Run:

```bash
minikube dashboard
```

This opens the dashboard in your default web browser, giving you a visual view of your cluster’s state.

## Install the Operator

1. Clone the repository and navigate into it:

   ```bash
   git clone -b v1.3.0 https://github.com/percona/percona-server-mysql-operator
   cd percona-server-mysql-operator
   ```

1. Deploy the Operator to your Minikube cluster

   ```bash
   kubectl apply --server-side -f deploy/bundle.yaml
   ```

   Expected output

   ```text
   customresourcedefinition.apiextensions.k8s.io/perconaservermysqlbackups.ps.percona.com created
   customresourcedefinition.apiextensions.k8s.io/perconaservermysqlrestores.ps.percona.com created
   customresourcedefinition.apiextensions.k8s.io/perconaservermysqls.ps.percona.com created
   serviceaccount/percona-server-mysql-operator created
   role.rbac.authorization.k8s.io/percona-server-mysql-operator-leaderelection created
   role.rbac.authorization.k8s.io/percona-server-mysql-operator created
   rolebinding.rbac.authorization.k8s.io/percona-server-mysql-operator-leaderelection created
   rolebinding.rbac.authorization.k8s.io/percona-server-mysql-operator created
   configmap/percona-server-mysql-operator-config created
   deployment.apps/percona-server-mysql-operator created
   ```

## Configure and deploy your MySQL cluster

Since Minikube runs on a single node, the default configuration doesn’t fit. Use the minimal configuration adjusted for Minikube environment.

```bash
kubectl apply -f deploy/cr-minimal.yaml
```

Expected output

```text
perconaservermysql.ps.percona.com/ps-cluster1 created
```

This creates a group-replication cluster with one Percona Server for MySQL instances and one HAProxy instance. For more configuration options, see the `deploy/cr.yaml` file and the [Custom Resource Options](https://docs.percona.com/percona-operator-for-mysql/1.3.0/operator.md) reference.

### Check the cluster status

The cluster creation process takes a few minutes. Monitor the status with:

```bash
kubectl get ps
```

Wait until the `STATE` column shows `ready`. This indicates your cluster is fully operational.

Expected output

```text
NAME           REPLICATION         ENDPOINT                   STATE   MYSQL   ORCHESTRATOR   HAPROXY   ROUTER   AGE
ps-cluster1   group-replication    ps-cluster1-haproxy.default   ready   1                     1                  5m50s
```

## Verify the cluster operation

It typically takes about ten minutes for the cluster to start. Once `kubectl get ps` shows the cluster status as `ready`, you can connect to it and start using your MySQL database.

To connect to Percona Server for MySQL, use the connection Secret that the Operator creates for the `root` user. It is named `<cluster_name>-psuser-root` (by default, `ps-cluster1-psuser-root`) and contains hostnames, ports, credentials, and ready-to-use connection URIs. Read [Connection secrets](https://docs.percona.com/percona-operator-for-mysql/1.3.0/connection-secrets.md) for the full reference.

Here’s how to connect:

1. Export the namespace, cluster name and the Secret name as environment variables:

   ```bash
   export NAMESPACE=my-namespace
   export CLUSTER_NAME=ps-cluster1
   export SECRET_NAME=${CLUSTER_NAME}-psuser-root
   ```

   Replace `ps-cluster1` with the [name of your cluster](https://docs.percona.com/percona-operator-for-mysql/1.3.0/operator.md#metadata-name) if you changed it during installation.

1. List the Secrets objects.

   ```bash
   $ kubectl get secrets -n $NAMESPACE
   ```

   Look for the Secret named `<cluster_name>-psuser-root`. By default, it is `ps-cluster1-psuser-root`.

1. Retrieve the user credentials from the Secret:

   ```bash
   kubectl get secret "$SECRET_NAME" -n "$NAMESPACE" \
   -o jsonpath='{.data.user}' | base64 --decode && echo
   kubectl get secret "$SECRET_NAME" -n "$NAMESPACE" \
   -o jsonpath='{.data.password}' | base64 --decode && echo
   ```

1. Run a container with the `mysql` tool and connect its console output to your terminal:

   ```bash
   kubectl run -i --rm --tty percona-client --image=percona/percona-server:8.4 --restart=Never -- bash -il
   ```

   It may require some time to execute the command and deploy the corresponding Pod.

1. Now run `mysql` tool in the `percona-client` command shell using the password obtained from the Secret instead of the `<root password>` placeholder. The command will look different depending on whether the cluster uses load balancing with [HAProxy](https://docs.percona.com/percona-operator-for-mysql/1.3.0/haproxy-conf.md) (the default behavior) or uses [MySQL Router](https://docs.percona.com/percona-operator-for-mysql/1.3.0/router-conf.md) (can be used with Group Replication clusters):

   **If using HAProxy (default)**

   ```bash
   mysql -h ps-cluster1-haproxy -uroot -p<root password>
   ```

   **If using MySQL Router**

   ```bash
   mysql -h ps-cluster1-router -uroot -p<root password>
   ```

   Expected output

   ```text
   mysql: [Warning] Using a password on the command line interface can be insecure.
   Welcome to the MySQL monitor.  Commands end with ; or \g.
   Your MySQL connection id is 1665
   Server version: 8.4.11-11.1 Percona Server (GPL), Release 6, Revision dbba4396

   Copyright (c) 2009-2026 Percona LLC and/or its affiliates
   Copyright (c) 2000, 2026, Oracle and/or its affiliates.

   Oracle is a registered trademark of Oracle Corporation and/or its
   affiliates. Other names may be trademarks of their respective
   owners.

   Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

   mysql>
   ```

   The following example uses the MySQL prompt to check the `max_connections` variable:

   ```sql
   SHOW VARIABLES LIKE "max_connections";
   ```

   Expected output

   ```text
   +-----------------+-------+
   | Variable_name   | Value |
   +-----------------+-------+
   | max_connections | 158   |
   +-----------------+-------+
   1 row in set (0.02 sec)

   mysql>
   ```
