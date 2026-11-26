> For the complete documentation index, see [llms.txt](https://docs.percona.com/percona-operator-for-mysql/1.3.0/llms.txt).

# Install Percona Server for MySQL on DigitalOcean Kubernetes (DOKS)

This guide shows you how to deploy Percona Operator for MySQL on DigitalOcean Kubernetes (DOKS). The document assumes some experience with the platform. For more information on DOKS, see the [DigitalOcean Kubernetes documentation](https://docs.digitalocean.com/products/kubernetes/) .

## Prerequisites

Prepare the following before you create a cluster:

1. Install [doctl](https://docs.digitalocean.com/reference/doctl/how-to/install/) , the DigitalOcean command-line interface (CLI), to create and manage DOKS clusters.

1. Create a [DigitalOcean personal access token](https://docs.digitalocean.com/reference/api/create-personal-access-token/) so `doctl` can access your account. After you create the token, authenticate `doctl`:

   ```bash
   doctl auth init
   ```

1. Install [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/) to manage Kubernetes resources.

## Before you start

Check the [System requirements](https://docs.percona.com/percona-operator-for-mysql/1.3.0/System-Requirements.md) to confirm your environment meets the prerequisites. Use a cluster with at least three nodes.

## Create a DigitalOcean Kubernetes cluster

1. Decide on the following details:

   - Cluster name
   - Region where you deploy the cluster
   - Kubernetes version
   - Node size and count for the [node pool](https://docs.digitalocean.com/products/kubernetes/how-to/add-node-pools/)

1. Create the cluster in the DigitalOcean control panel, or with `doctl`:

   ```bash
   doctl kubernetes cluster create <cluster-name> --region <region> --version <version> --size <node-size> --count 3
   ```

   Replace the `<cluster-name>`, `<region>`, `<version>` and `<node-size>` placeholders with your values. Cluster creation takes several minutes.

   For the full list of options, see [How to create Kubernetes clusters](https://docs.digitalocean.com/products/kubernetes/how-to/create-clusters/) .

1. Save the cluster credentials to your `kubeconfig` file so `kubectl` can connect:

   ```bash
   doctl kubernetes cluster kubeconfig save <cluster-name>
   ```

   For more connection options, see [How to connect to a DigitalOcean Kubernetes cluster](https://docs.digitalocean.com/products/kubernetes/how-to/connect-to-cluster/) .

## Install the Operator and deploy your MySQL cluster

1. Create a namespace and set it as the current context. Replace `<namespace>` with a descriptive name:

   ```bash
   kubectl create namespace <namespace>
   kubectl config set-context $(kubectl config current-context) --namespace=<namespace>
   ```

   Expected output

   ```text
   namespace/<namespace> created
   Context "<context>" modified.
   ```

1. Deploy the Operator:

   ```bash
   kubectl apply --server-side -f https://raw.githubusercontent.com/percona/percona-server-mysql-operator/v1.3.0/deploy/bundle.yaml
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

   The Operator Pod is now running.

1. Deploy the Percona Server for MySQL cluster.

   DOKS installs the DigitalOcean Container Storage Interface (CSI) driver and sets `do-block-storage` as the default StorageClass. The default cluster manifest uses that StorageClass. Set `storageClassName` only if you want a different volume type.

   ```bash
   kubectl apply -f https://raw.githubusercontent.com/percona/percona-server-mysql-operator/v1.3.0/deploy/cr.yaml
   ```

   Expected output

   ```text
   perconaservermysql.ps.percona.com/ps-cluster1 created
   ```

1. Check the cluster status. Creation takes several minutes:

   ```bash
   kubectl get ps
   ```

   Expected output

   ```text
   NAME          REPLICATION         ENDPOINT                          STATE   MYSQL   ORCHESTRATOR   HAPROXY   ROUTER   AGE
   ps-cluster1   group-replication   ps-cluster1-haproxy.<namespace>   ready   3                                3        20m
   ```

   When the `STATE` column shows `ready`, the cluster is running.

## Verify the cluster operation

When `kubectl get ps` shows the cluster status as `ready`, connect to the cluster.

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

## Delete the DigitalOcean Kubernetes cluster

To delete the cluster, run the following command:

```bash
doctl kubernetes cluster delete <cluster-name>
```

Cluster deletion takes several minutes.

Deleting the cluster leaves its load balancers, volumes, and volume snapshots in your DigitalOcean account. You can still pay for those resources until you delete them.

For more ways to delete a cluster, and for how to remove the associated load balancers, volumes, and volume snapshots, see [How to destroy DigitalOcean Kubernetes clusters](https://docs.digitalocean.com/products/kubernetes/how-to/destroy-clusters/) .

Warning

Deleting the cluster removes access to the database. Data on any volumes that remain is deleted only when you delete those volumes.
