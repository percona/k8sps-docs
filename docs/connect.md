# Connect to Percona Server for MySQL

In this tutorial, you will connect to the Percona Server for MySQL you deployed previously.

The Operator creates a dedicated Secret named `<cluster_name>-psuser-root` that contains all connection details for the `root` user: hostname, port, username, password, and ready-to-use URIs. The Operator keeps this Secret up to date on every reconciliation. 

Here's how to connect:
{.power-number}

1. Export the namespace, cluster name and the Secret name as environment variables:

    ```bash
    export NAMESPACE=my-namespace
    export CLUSTER_NAME=ps-cluster1
    export SECRET_NAME=${CLUSTER_NAME}-psuser-root
    ```

    Replace `ps-cluster1` with the [name of your cluster](operator.md#metadata-name) if you changed it during installation.

2. Verify that the connection Secret exists:

    ```bash
    kubectl get secret $SECRET_NAME -n $NAMESPACE
    ```

    Look for the Secret named `<cluster_name>-psuser-root`. The
    default name differs on how you installed the Operator:

    === "via kubectl"

        `ps-cluster1-psuser-root`

    === "via Helm"

        `my-db-ps-db-psuser-root`

3. Retrieve the user credentials from the Secret:
   
    ```bash
kubectl get secret "$SECRET_NAME" -n "$NAMESPACE" \
  -o jsonpath='{.data.user}' | base64 --decode && echo
kubectl get secret "$SECRET_NAME" -n "$NAMESPACE" \
  -o jsonpath='{.data.password}' | base64 --decode && echo
    ```

4. Run a container with the `mysql` client and connect its console output to your terminal. The following command does this, naming the new Pod `percona-client`:

    ```bash
    kubectl run -n $NAMESPACE -i --rm --tty percona-client \
    --image=percona/percona-server:8.4 --restart=Never -- bash -il
    ```

    Executing it may require some time to deploy the corresponding Pod.

5. Connect to Percona Server for MySQL. To do this, run `mysql` tool in the `percona-client` command shell using your cluster name and the password obtained from the secret instead of the `<root_password>` placeholder. The command will look different depending on whether your cluster  uses load balancing with [HAProxy](haproxy-conf.md) (the default behavior) or uses [MySQL Router](router-conf.md) (can be used with Group Replication clusters only):

    === "with HAProxy (default)"

        ```bash
        mysql -h <cluster_name>-haproxy -uroot -p'<root_password>'
        ```

    === "with MySQL Router"

        ```bash
        mysql -h <cluster_name>-router -uroot -p'<root_password>'
        ```

Congratulations! You have connected to Percona Server for MySQL.

## Next steps

[Insert sample data :material-arrow-right:](data-insert.md){.md-button}
