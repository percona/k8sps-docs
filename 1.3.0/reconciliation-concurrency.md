> For the complete documentation index, see [llms.txt](https://docs.percona.com/percona-operator-for-mysql/1.3.0/llms.txt).

# Configure concurrency for a cluster reconciliation

Reconciliation is the process by which the Operator continuously compares the desired state with the actual state of the cluster. The desired state is defined in a Kubernetes custom resource, like PerconaServerMySQL.

If the actual state does not match the desired state, the Operator takes actions to bring the system into alignment. This means creating, updating, or deleting Kubernetes resources (Pods, Services, ConfigMaps, etc.) or performing database-specific operations like scaling, backups, or failover.

Reconciliation is triggered by a variety of events, including:

- Changes to the cluster configuration
- Changes to the cluster state
- Changes to the cluster resources

By default, the Operator has one reconciliation worker. This means that if you deploy or update 2 clusters at the same time, the Operator will reconcile them sequentially.

The `MAX_CONCURRENT_RECONCILES` environment variable in the `percona-server-mysql-operator` deployment controls the number of concurrent workers that can reconcile resources in Percona Server for MySQL clusters in parallel.

Thus, to extend the previous example, if you set the number of reconciliation workers to `2`, the Operator will reconcile both clusters in parallel. This also helps you with benchmarking the Operator performance.

The general recommendation is to set the number of concurrent workers equal to the number of Percona Server for MySQL clusters. When the number of workers is greater, the excessive workers will remain idle.

## Set the number of reconciliation workers

1. Check the current value of the `MAX_CONCURRENT_RECONCILES` environment variable:

   ```
   kubectl get deployment percona-server-mysql-operator -o jsonpath='{.spec.template.spec.containers[0].env[?(@.name=="MAX_CONCURRENT_RECONCILES")].value}'
   ```

   Sample output

   ```
   1
   ```

1. Set a new value with `kubectl set env`. The following command sets the number of workers to `2`:

   ```
   kubectl set env deployment/percona-server-mysql-operator MAX_CONCURRENT_RECONCILES=2
   ```

   You can set the value to any positive integer.

1. Verify the change by re-running the command from step 1:

   ```
   kubectl get deployment percona-server-mysql-operator -o jsonpath='{.spec.template.spec.containers[0].env[?(@.name=="MAX_CONCURRENT_RECONCILES")].value}'
   ```

   Sample output

   ```
   2
   ```

After the environment variable is updated, Kubernetes rolls out a new Operator Pod with the new setting.
