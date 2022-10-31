# Monitoring

Percona Monitoring and Management (PMM) [provides an excellent
solution](https://www.percona.com/doc/percona-xtradb-cluster/LATEST/manual/monitoring.html#using-pmm)
to monitor Percona Distribution for MySQL.

!!! note

    Only PMM 2.x versions are supported by the Operator.

PMM is a client/server application. *PMM Client* runs on each node with the
database you wish to monitor: it collects needed metrics and sends gathered data
to *PMM Server*. As a user, you connect to PMM Server to see database metrics on
a number of dashboards.

That’s why PMM Server and PMM Client need to be installed separately.

## Installing the PMM Server

PMM Server runs as a *Docker image*, a *virtual appliance*, or on an *AWS instance*.
Please refer to the [official PMM documentation](https://www.percona.com/doc/percona-monitoring-and-management/2.x/setting-up/server/index.html)
for the installation instructions.

## Installing the PMM Client

The following steps are needed for the PMM client installation in your
Kubernetes-based environment:


1. The PMM client installation is initiated by updating the `pmm`
    section in the
    [deploy/cr.yaml](https://github.com/percona/percona-server-mysql-operator/blob/main/deploy/cr.yaml)
    file.

    * set `pmm.enabled=true`
    * set the `pmm.serverHost` key to your PMM Server hostname,
    * authorize PMM Client within PMM Server:
        <a name="operator-monitoring-client-token"></a>
        [Acquire the API Key from your PMM Server](https://docs.percona.com/percona-monitoring-and-management/details/api.html#api-keys-and-authentication) and set `pmmserverkey` in the [users Secrets](users.md/#system-users) object to this obtained API Key value. For example, setting the PMM Server API Key to `new_key` in the `cluster1-secrets` object can be done with the following command:

        === "in Linux"

            ``` { .python data-prompt="$" }
            $ kubectl patch secret/cluster1-secrets -p '{"data":{"pmmserverkey": '$(echo -n new_key | base64 --wrap=0)'}}'
            ```

        === "in macOS"

            ```bash
            $ kubectl patch secret/cluster1-secrets -p '{"data":{"pmmserverkey": '$(echo -n new_key | base64)'}}'
            ```

    When done, apply the edited `deploy/cr.yaml` file:

    ```bash
    $ kubectl apply -f deploy/cr.yaml
    ```

2. Check that corresponding Pods are not in a cycle of stopping and restarting.
    This cycle occurs if there are errors on the previous steps:

    ``` {.bash data-prompt="$" }
    $ kubectl get pods
    $ kubectl logs cluster1-mysql-0 -c pmm-client
    ```

3. Now you can access PMM via *https* in a web browser, with the
    login/password authentication, and the browser is configured to show
    Percona Server for MySQL metrics.
