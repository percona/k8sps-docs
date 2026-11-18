> For the complete documentation index, see [llms.txt](https://docs.percona.com/percona-operator-for-mysql/1.3.0/llms.txt).

# Percona Operator for MySQL single-namespace and multi-namespace deployment

There are two design patterns that you can choose from when deploying Percona Operator for MySQL and Percona Server for MySQL clusters in Kubernetes:

- Namespace-scope - one Operator per Kubernetes namespace,
- Cluster-wide - one Operator can manage clusters in multiple namespaces.

This how-to explains how to configure Percona Operator for MySQL based on Percona Server for MySQL for each scenario.

## Namespace-scope

By default, Percona Operator for MySQL functions in a specific Kubernetes namespace. You can create one during the installation (like it is shown in the [installation instructions](https://docs.percona.com/percona-operator-for-mysql/1.3.0/kubernetes.html)) or just use the `default` namespace. This approach allows several Operators to co-exist in one Kubernetes-based environment, being separated in different namespaces:

Normally this is a recommended approach, as isolation minimizes impact in case of various failure scenarios. This is the default configuration of our Operator.

Let’s say you will use a Kubernetes Namespace called `percona-db-1`.

1. Clone `percona-server-mysql-operator` repository:

   ```
   git clone -b v1.3.0 https://github.com/percona/percona-server-mysql-operator
   cd percona-server-mysql-operator
   ```

1. Create your `percona-db-1` Namespace (if it doesn’t yet exist) as follows:

   ```
   kubectl create namespace percona-db-1
   ```

1. Deploy the Operator [using](https://kubernetes.io/docs/reference/using-api/server-side-apply/) the following command:

   ```
   kubectl apply --server-side -f deploy/bundle.yaml -n percona-db-1
   ```

1. Once Operator is up and running, deploy the database cluster itself:

   ```
   kubectl apply -f deploy/cr.yaml -n percona-db-1
   ```

You can deploy multiple clusters in this namespace.

### Add more namespaces

What if there is a need to deploy clusters in another namespace? The solution for namespace-scope deployment is to have more than one Operator. We will use the `percona-db-2` namespace as an example.

1. Create your `percona-db-2` namespace (if it doesn’t yet exist) as follows:

   ```
   kubectl create namespace percona-db-2
   ```

1. Deploy the Operator:

   ```
   kubectl apply --server-side -f deploy/bundle.yaml -n percona-db-2
   ```

1. Once Operator is up and running deploy the database cluster itself:

   ```
   kubectl apply -f deploy/cr.yaml -n percona-db-2
   ```

   Note

   Cluster names may be the same in different namespaces.

## Install the Operator cluster-wide

Sometimes it is more convenient to have one Operator watching for Percona Server for MySQL custom resources in several namespaces.

We recommend running Percona Operator for MySQL in a traditional way, limited to a specific namespace, to limit the blast radius. But it is possible to run it in so-called *cluster-wide* mode, one Operator watching several namespaces, if needed:

To use the Operator in such cluster-wide mode, you should install it with a different set of configuration YAML files, which are available in the deploy folder and have filenames with a special `cw-` prefix: e.g. `deploy/cw-bundle.yaml`.

While using this cluster-wide versions of configuration files, you should set the following information there:

- `subjects.namespace` option should contain the namespace which will host the Operator,
- `WATCH_NAMESPACE` key-value pair in the `env` section should have `value` equal to a comma-separated list of the namespaces to be watched by the Operator (or just a blank string to make the Operator deal with *all namespaces* in a Kubernetes cluster).

The following simple example shows how to install Operator cluster-wide on Kubernetes.

1. Clone `percona-server-mysql-operator` repository:

   ```
   git clone -b v1.3.0 https://github.com/percona/percona-server-mysql-operator
   cd percona-server-mysql-operator
   ```

1. Let’s say you will use `ps-operator` namespace for the Operator, and `percona-db-1` namespace for the cluster. Create these namespaces, if needed:

   ```
   kubectl create namespace ps-operator
   kubectl create namespace percona-db-1
   ```

1. Edit the `deploy/cw-bundle.yaml` configuration file to make sure it contains proper namespace name for the Operator:

   ```
   ...
   subjects:
   - kind: ServiceAccount
     name: percona-server-mysql-operator
     namespace: ps-operator
   ...
   spec:
     containers:
     - command:
       ...
       env:
       - name: WATCH_NAMESPACE
         value: "percona-db-1"
       ...
   ```

1. Apply the `deploy/cw-bundle.yaml` file with the following command:

   ```
   kubectl apply --server-side -f deploy/cw-bundle.yaml -n ps-operator
   ```

   Right now the operator deployed in cluster-wide mode will monitor all namespaces in the cluster, either already existing or newly created ones.

1. Deploy the cluster in the namespace of your choice:

   ```
   kubectl apply -f deploy/cr.yaml -n percona-db-1
   ```

## Verifying the cluster operation

When creation process is over, you can try to connect to the cluster.

To connect to Percona Server for MySQL, use the connection Secret that the Operator creates for the `root` user. It is named `<cluster_name>-psuser-root` (by default, `ps-cluster1-psuser-root`) and contains hostnames, ports, credentials, and ready-to-use connection URIs. Read [Connection secrets](https://docs.percona.com/percona-operator-for-mysql/1.3.0/connection-secrets.html) for the full reference.

Here’s how to connect:

1. Export the namespace, cluster name and the Secret name as environment variables:

   ```
   export NAMESPACE=my-namespace
   export CLUSTER_NAME=ps-cluster1
   export SECRET_NAME=${CLUSTER_NAME}-psuser-root
   ```

   Replace `ps-cluster1` with the [name of your cluster](https://docs.percona.com/percona-operator-for-mysql/1.3.0/operator.html#metadata-name) if you changed it during installation.

1. List the Secrets objects.

   ```
   $ kubectl get secrets -n $NAMESPACE
   ```

   Look for the Secret named `<cluster_name>-psuser-root`. By default, it is `ps-cluster1-psuser-root`.

1. Retrieve the user credentials from the Secret:

   ```
   kubectl get secret "$SECRET_NAME" -n "$NAMESPACE" \
   -o jsonpath='{.data.user}' | base64 --decode && echo
   kubectl get secret "$SECRET_NAME" -n "$NAMESPACE" \
   -o jsonpath='{.data.password}' | base64 --decode && echo
   ```

1. Run a container with the `mysql` tool and connect its console output to your terminal:

   ```
   kubectl run -i --rm --tty percona-client --image=percona/percona-server:8.4 --restart=Never -- bash -il
   ```

   It may require some time to execute the command and deploy the corresponding Pod.

1. Now run `mysql` tool in the `percona-client` command shell using the password obtained from the Secret instead of the `<root password>` placeholder. The command will look different depending on whether the cluster uses load balancing with [HAProxy](https://docs.percona.com/percona-operator-for-mysql/1.3.0/haproxy-conf.html) (the default behavior) or uses [MySQL Router](https://docs.percona.com/percona-operator-for-mysql/1.3.0/router-conf.html) (can be used with Group Replication clusters):

   **If using HAProxy (default)**

   ```
   mysql -h ps-cluster1-haproxy -uroot -p<root password>
   ```

   **If using MySQL Router**

   ```
   mysql -h ps-cluster1-router -uroot -p<root password>
   ```

   Expected output

   ```
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

   ```
   SHOW VARIABLES LIKE "max_connections";
   ```

   Expected output

   ```
   +-----------------+-------+
   | Variable_name   | Value |
   +-----------------+-------+
   | max_connections | 158   |
   +-----------------+-------+
   1 row in set (0.02 sec)

   mysql>
   ```

Note

Some Kubernetes-based environments are specifically configured to have communication across Namespaces is not allowed by default network policies. In this case, you should specifically allow the Operator communication across the needed Namespaces. Following the above example, you would need to allow ingress traffic for the `ps-operator` Namespace from the `percona-db-1` Namespace, and also from the `default` Namespace. You can do it with the NetworkPolicy resource, specified in the YAML file as follows:

```
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: percona
  namespace: ps-operator
spec:
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: percona-db-1
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: default
  podSelector: {}
  policyTypes:
  - Ingress
```

Don’t forget to apply the resulting file with the usual `kubectl apply` command.

You can find more details about Network Policies [in the official Kubernetes documentation](https://kubernetes.io/docs/concepts/services-networking/network-policies/) .

## Upgrading the Operator in cluster-wide mode

Cluster-wide Operator is upgraded similarly to a single-namespace one. Both deployment variants provide you with the same three upgradable components:

- the Operator;
- [Custom Resource Definition (CRD)](https://docs.percona.com/percona-operator-for-mysql/1.3.0/operator.html),
- Database Management System (Percona Server for MySQL).

To upgrade the cluster-wide Operator you follow the [standard upgrade scenario](https://docs.percona.com/percona-operator-for-mysql/1.3.0/update-operator.html) concerning the Operator’s namespace and a different YAML configuration file: the one with a special `cw-` prefix, `deploy/cw-rbac.yaml`. The resulting steps will look as follows.

1. Update the [Custom Resource Definition](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/) for the Operator, and do the same for the Role-based access control:

   ```
   kubectl apply -f deploy/crd.yaml
   kubectl apply -f deploy/cw-rbac.yaml
   ```

1. Now you should [apply a patch](https://kubernetes.io/docs/tasks/run-application/update-api-object-kubectl-patch/) to your deployment, supplying the necessary image name with a newer version tag. You can find the proper image name for the current Operator release [in the list of certified images](https://docs.percona.com/percona-operator-for-mysql/1.3.0/images.html). For example, updating to the `1.3.0` version in the `ps-operator` namespace should look as follows.

   ```
   kubectl patch deployment percona-server-mysql-operator \
     -p'{"spec":{"template":{"spec":{"containers":[{"name":"percona-server-mysql-operator","image":"percona/percona-server-mysql-operator:1.3.0"}]}}}}' -n ps-operator
   ```

1. The deployment rollout will be automatically triggered by the applied patch. You can track the rollout process in real time with the `kubectl rollout status` command with the name of your cluster:

   ```
   kubectl rollout status deployments percona-server-mysql-operator -n ps-operator
   ```
