# Change replication type

By default, Percona Operator for MySQL is deployed with [group-replication](architecture.md#replication-types-and-proxy-solutions) replication type and HAProxy enabled. 

You can change the proxy from HAProxy to MySQL Router or vice versa. Note that you can use MySQL router only with the group-replication replication type.

To change a proxy, edit the `deploy/cr.yaml` file and set the `proxy.haproxy.enabled` option to `false` and the `proxy.router.enabled` option to `true`. Then apply the new configuration with the `kubectl apply -f deploy/cr.yaml` command.

You can also change the replication type for your cluster from group replication to asynchronous replication. To do it, do the following:

1. [Pause](pause.md) the cluster. Since the cluster is running, run the `kubectl patch` command to update the cluster configuration. Replace the `<namespace>` placeholder with your namespace. For example, for the cluster with the name `ps-cluster1`, the command is:

    ```bash
    kubectl patch ps ps-cluster1 -n <namespace> --type json -p='[{"op":"add","path":"/spec/pause","value":true}]'    
    ```
     
2. Edit the `deploy/cr.yaml` file and set the `mysql.clusterType` option to `async`. Make sure you have HAProxy enabled as a proxy in your configuration.

    ```yaml
    mysql:
      clusterType: async
      ...
    proxy:
      haproxy:
        enabled: true
        ...
    ```

3. Apply the new configuration:

    ```bash
    kubectl apply -f deploy/cr.yaml -n <namespace>
    ```

4. Unpause the cluster.

    ```bash
    kubectl patch ps ps-cluster1 -n <namespace> --type json -p='[{"op":"add","path":"/spec/pause","value":false}]'    
    ```

5. Wait for the cluster to be resumed. Check the status with the `kubectl get ps` command.

Changing replication type on a running cluster is not supported.
