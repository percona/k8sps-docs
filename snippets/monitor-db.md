# Monitor database with Percona Monitoring and Management (PMM)

In this section you will learn how to monitor Percona Server for MySQL cluster with [Percona Monitoring and Management (PMM) :octicons-link-external-16:](https://www.percona.com/doc/percona-monitoring-and-management/2.x/index.html).

!!! note

    Only PMM 2.x versions are supported by the Operator.

PMM is a client/server application. It includes the [PMM Server :octicons-link-external-16:](https://www.percona.com/doc/percona-monitoring-and-management/2.x/details/architecture.html#pmm-server) and the number of [PMM Clients :octicons-link-external-16:](https://www.percona.com/doc/percona-monitoring-and-management/2.x/details/architecture.html#pmm-client) running on each node with the database you wish to monitor.

A PMM Client collects needed metrics and sends gathered data to the PMM Server.
 As a user, you connect to the PMM Server to see database metrics on
a number of dashboards.

PMM Server and PMM Client are installed separately.

## Install PMM Server

You must have PMM Server up and running. You can run PMM Server as a *Docker image*, a *virtual appliance*, or on an *AWS instance*.
Please refer to the [official PMM documentation :octicons-link-external-16:](https://www.percona.com/doc/percona-monitoring-and-management/2.x/setting-up/server/index.html)
for the installation instructions.

## Install PMM Client

The following steps are needed for the PMM Client installation as a side-car
container in your Kubernetes-based environment:
{.power-number}

1. Authorize PMM Client within PMM Server.
    <a name="operator-monitoring-client-token"></a>
    1. [Acquire the API Key from your PMM Server :octicons-link-external-16:](https://docs.percona.com/percona-monitoring-and-management/details/api.html#api-keys-and-authentication). Specify the Admin role when getting the API Key. 

        <i warning>:material-alert: Warning:</i> The API key is not rotated automatically.

    2. Set `pmmserverkey` in the [users Secrets](users.md/#system-users) object to this obtained API Key value. For example, setting the PMM Server API Key to `new_key` in the `cluster1-secrets` object can be done with the following command:

        === "in Linux"

            ```bash
            kubectl patch secret/cluster1-secrets -p '{"data":{"pmmserverkey": '$(echo -n new_key | base64 --wrap=0)'}}'
            ```

        === "in macOS"

            ```bash
            kubectl patch secret/cluster1-secrets -p '{"data":{"pmmserverkey": '$(echo -n new_key | base64)'}}'
            ```

2. Update the `pmm` section in the [deploy/cr.yaml :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/v{{ release }}/deploy/cr.yaml) file:

    * Set `pmm.enabled`=`true`.
    * Specify your PMM Server hostname or an IP address for the `pmm.serverHost` option. The PMM Server IP address should be resolvable and reachable from within your cluster.

     ```yaml
     pmm:
       enabled: true
       image: percona/pmm-client:{{pmm3recommended}}
       serverHost: monitoring-service
     ``` 

3. Apply the changes:

    ```bash
    $ kubectl apply -f deploy/cr.yaml -n <namespace>
    ```

4. Check that corresponding Pods are not in a cycle of stopping and restarting.
    This cycle occurs if there are errors on the previous steps:

    ```bash
    kubectl get pods -n <namespace>
    kubectl logs  <cluster-name>-mysql-0 -c pmm-client -n <namespace>
    ```

## Check the metrics

Let's see how the collected data is visualized in PMM.

Now you can access PMM via *https* in a web browser, with the login/password
authentication, and the browser is configured to show Percona Server for MySQL
metrics.
