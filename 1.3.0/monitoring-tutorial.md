> For the complete documentation index, see [llms.txt](https://docs.percona.com/percona-operator-for-mysql/1.3.0/llms.txt).

# Monitor database with Percona Monitoring and Management (PMM)

In this section you will learn how to monitor Percona Server for MySQL cluster with [Percona Monitoring and Management (PMM)](https://docs.percona.com/percona-monitoring-and-management/3/index.html) .

PMM is a client/server application. It includes the [PMM Server](https://docs.percona.com/percona-monitoring-and-management/3/reference/index.html#pmm-server) and the number of [PMM Clients](https://docs.percona.com/percona-monitoring-and-management/3/reference/index.html#pmm-client) running on each node with the database you wish to monitor.

A PMM Client collects server metrics, general system metrics, query analytics and sends it to the server As a user, you connect to the PMM Server to see database metrics on a number of dashboards.

PMM Server and PMM Client are installed separately.

## Considerations

1. Starting with the version 0.10.0, the Operator supports only PMM 3.x versions. The support for PMM 2.x is dropped.
1. You must run the Operator version 0.10.0 and later to monitor your database with PMM 3.x. Check the [Upgrade the Operator](https://docs.percona.com/percona-operator-for-mysql/1.3.0/update-operator.md) tutorial for the update steps.
1. To use PMM3, PMM Server version must be equal to or newer than the PMM Client.
1. Query Analytics (QAN) reads MySQL queries from Performance Schema, which the Operator configures for each node. If your applications use server-side prepared statements (common with drivers such as JDBC), expect QAN to show query examples as placeholders (`?`) rather than literal values, and EXPLAIN to be unavailable for them. This is how upstream MySQL exposes prepared statements to Performance Schema. This is expected behavior, not a limitation of PMM or the Operator.

## Install PMM Server

You must have PMM Server up and running. You can run PMM Server as a *Docker container*, a *virtual appliance*, or on an *AWS instance*. Please refer to the [official PMM documentation](https://docs.percona.com/percona-monitoring-and-management/3/install-pmm/install-pmm-server/index.html) for the installation instructions.

For Kubernetes environment, we recommend to install PMM from the [Helm chart](https://docs.percona.com/percona-monitoring-and-management/3/install-pmm/install-pmm-server/deployment-options/helm/index.html) .

## Install PMM Client

PMM Client is installed as a sidecar container in the database Pods in your Kubernetes-based environment. To install PMM Client, do the following:

1. Authorize PMM Client within PMM Server.

   1. PMM3 uses Grafana service accounts to control access to PMM server components and resources. To authenticate in PMM server, you need a service account token. Use PMM documentation to [generate a service account with the **Admin** role and token](https://docs.percona.com/percona-monitoring-and-management/3/api/authentication.html?h=authe#generate-a-service-account-and-token) .

      The token must have the format `glsa_*************************_9e35351b`.

      Warning

      When you create a service account token, you can select its lifetime: it can be either a permanent token that never expires or the one with the expiration date. PMM server cannot rotate service account tokens after they expire. So you must take care of reconfiguring PMM Client in this case.

   1. Add the service account token to the `pmmservertoken` option in the [users Secrets](https://docs.percona.com/percona-operator-for-mysql/1.3.0/users.md#system-users) object. Use the following command and replace the `<my-token>` placeholder with your value:

      **in Linux**

      ```bash
      kubectl patch secret/ps-cluster1-secrets -p "$(echo -n '{"data":{"pmmservertoken":"'$(echo -n <my-token> | base64 --wrap=0)'"}}')"
      ```

      **in macOS**

      ```bash
      kubectl patch secret/ps-cluster1-secrets -p "$(echo -n '{"data":{"pmmservertoken":"'$(echo -n new_key | base64)'"}}')"
      ```

1. Update the `pmm` section in the [deploy/cr.yaml](https://github.com/percona/percona-server-mysql-operator/blob/v1.3.0/deploy/cr.yaml) file:

   - Set `pmm.enabled`=`true`.
   - Specify your PMM Server hostname or an IP address for the `pmm.serverHost` option. The PMM Server IP address should be resolvable and reachable from within your cluster.

   ```yaml
   pmm:
      enabled: true
      image: percona/pmm-client:3.10.0
      serverHost: monitoring-service
   ```

1. Apply the changes:

   ```bash
   kubectl apply -f deploy/cr.yaml -n <namespace>
   ```

   This triggers the Operator to restart your cluster Pods.

1. Check that corresponding Pods are not in a cycle of stopping and restarting. This cycle occurs if there are errors on the previous steps:

   ```bash
   kubectl get pods -n <namespace>
   kubectl logs  <cluster-name>-mysql-0 -c pmm-client -n <namespace>
   ```

## Check the metrics

Let’s see how the collected data is visualized in PMM.

1. Log in to PMM Server.
1. Click **MySQL** from the left-hand navigation menu.
1. Select your cluster from the **Clusters** drop-down menu and the desired time range on the top of the page. You should see the metrics.
1. Click **MySQL** → Other dashboards to see the list of available dashboards that allow you to drill down to the metrics you are interested in.
1. Click **Explore** from the left-hand navigation menu. In the **Metric** drop-down, start typing `mysql` to see the list of available metrics.
1. To see the data for the selected metric, click **Run query**.

## Next steps

[What’s next](https://docs.percona.com/percona-operator-for-mysql/1.3.0/what-next.md)
