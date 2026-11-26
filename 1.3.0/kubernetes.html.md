> For the complete documentation index, see [llms.txt](https://docs.percona.com/percona-operator-for-mysql/1.3.0/llms.txt).

# Install Percona Server for MySQL on Kubernetes

1. First of all, clone the percona-server-mysql-operator repository:

   ```bash
   git clone -b v1.3.0 https://github.com/percona/percona-server-mysql-operator
   cd percona-server-mysql-operator
   ```

   Note

   It is crucial to specify the right branch with `-b` option while cloning the code on this step. Please be careful.

1. Now Custom Resource Definition for Percona Server for MySQL should be created from the `deploy/crd.yaml` file. Custom Resource Definition extends the standard set of resources which Kubernetes “knows” about with the new items (in our case ones which are the core of the operator). [Apply it](https://kubernetes.io/docs/reference/using-api/server-side-apply/) as follows:

   ```bash
   kubectl apply --server-side -f deploy/crd.yaml
   ```

   This step should be done only once; it does not need to be repeated with the next Operator deployments, etc.

1. The next thing to do is to add the `mysql` namespace to Kubernetes, not forgetting to set the correspondent context for further steps:

   ```bash
   kubectl create namespace mysql
   kubectl config set-context $(kubectl config current-context) --namespace=mysql
   ```

   Note

   You can use different namespace name or even stay with the *Default* one.

1. Now RBAC (role-based access control) for Percona Server for MySQL should be set up from the `deploy/rbac.yaml` file. Briefly speaking, role-based access is based on specifically defined roles and actions corresponding to them, allowed to be done on specific Kubernetes resources (details about users and roles can be found in [Kubernetes documentation](https://kubernetes.io/docs/reference/access-authn-authz/rbac/#default-roles-and-role-bindings) ).

   ```bash
   kubectl apply -f deploy/rbac.yaml
   ```

   Note

   Setting RBAC requires your user to have cluster-admin role privileges. For example, those using Google Kubernetes Engine can grant user needed privileges with the following command: `$ kubectl create clusterrolebinding cluster-admin-binding --clusterrole=cluster-admin --user=$(gcloud config get-value core/account)`

   Finally it’s time to start the operator within Kubernetes:

   ```bash
   kubectl apply -f deploy/operator.yaml
   ```

1. Now that’s time to add the Percona Server for MySQL Users secrets to Kubernetes. They should be placed in the data section of the `deploy/secrets.yaml` file as logins and plaintext passwords for the user accounts (see [Kubernetes documentation](https://kubernetes.io/docs/concepts/configuration/secret/) for details).

   After editing is finished, users secrets should be created using the following command:

   ```bash
   kubectl create -f deploy/secrets.yaml
   ```

   More details about secrets can be found in [Users](https://docs.percona.com/percona-operator-for-mysql/1.3.0/users.md).

1. Now certificates should be generated. By default, the Operator generates certificates automatically, and no actions are required at this step. Still, you can generate and apply your own certificates as secrets according to the [TLS instructions](https://docs.percona.com/percona-operator-for-mysql/1.3.0/TLS.md).

1. After the operator is started and user secrets are added, Percona Server for MySQL can be created at any time with the following command:

   ```bash
   kubectl apply -f deploy/cr.yaml
   ```

   Creation process will take some time. The process is over when both operator and replica set pod have reached their Running status. `kubectl get pods` output should look like this:

   ```text
   NAME                                                 READY   STATUS    RESTARTS        AGE
   ps-cluster1-mysql-0                                     1/1     Running   0               7m6s
   ps-cluster1-mysql-1                                     1/1     Running   1 (5m39s ago)   6m4s
   ps-cluster1-mysql-2                                     1/1     Running   1 (4m40s ago)   5m7s
   ps-cluster1-orc-0                                       2/2     Running   0               7m6s
   percona-server-for-mysql-operator-54c5c87988-xfmlf   1/1     Running   0               7m42s
   ```

## Verify the cluster operation

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
