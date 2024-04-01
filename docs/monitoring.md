# Monitoring

Percona Monitoring and Management (PMM) [provides an excellent
solution :octicons-link-external-16:](https://www.percona.com/doc/percona-xtradb-cluster/LATEST/manual/monitoring.html#using-pmm)
to monitor Percona Distribution for MySQL.

!!! note

    Only PMM 2.x versions are supported by the Operator.

PMM is a client/server application. *PMM Client* runs on each node with the
database you wish to monitor: it collects needed metrics and sends gathered data
to *PMM Server*. As a user, you connect to PMM Server to see database metrics on
a number of dashboards.

PMM Server and PMM Client are installed separately.

## Install PMM Server

You must have PMM server up and running. You can run PMM Server as a *Docker image*, a *virtual appliance*, or on an *AWS instance*.
Please refer to the [official PMM documentation :octicons-link-external-16:](https://www.percona.com/doc/percona-monitoring-and-management/2.x/setting-up/server/index.html)
for the installation instructions.

## Install PMM Client

To install PMM Client as a side-car container in your Kubernetes-based environment, do the following:
{.power-number}

1. [Get the PMM API key from PMM Server :octicons-link-external-16:](https://docs.percona.com/percona-monitoring-and-management/details/api.html#api-keys-and-authentication). The API key must have the role "Admin". You need this key to authorize PMM Client within PMM Server. 

    === ":material-view-dashboard-variant: From PMM UI" 

        [Generate the PMM API key :octicons-link-external-16:](https://docs.percona.com/percona-monitoring-and-management/details/api.html#api-keys-and-authentication){.md-button} 

    === ":material-console: From command line"

        You can query your PMM Server installation for the API
        Key using `curl` and `jq` utilities. 

        Retrieve the user credentials from the PMM Server:

        ```.bash
        PMM_AUTH=$(echo -n admin:$(kubectl get secret pmm-secret -o jsonpath='{.data.PMM_ADMIN_PASSWORD}' | base64 --decode) | base64)
        ```

        Replace the `$PMM_SERVER_IP` placeholder with your real PMM Server hostname in the following command:
        
        ```.bash 
        export API_KEY=$(curl --insecure -X POST -H "Authorization: Basic $PMM_AUTH" -H 'Content-Type: application/json'  -d '{"name":"operator", "role": "Admin"}' "https://$PMM_SERVER_IP/graph/api/auth/keys" | jq .key)
        ```

        To get the API_KEY value, run:

        ```.bash
        echo $API_KEY
        ```

        The output shows the base64 encoded API key. 

    !!! note

        The API key is not rotated. 

2. Specify the API key as the `pmmserverkey` value in the [users Secrets](users.md/#system-users) object.

    === "in Linux"

        ```{.bash data-prompt="$"}
        $ kubectl patch secret/cluster1-secrets -p '{"data":{"pmmserverkey": '$(echo -n new_key | base64 --wrap=0)'}}'
        ```

    === "in macOS"

        ```{.bash data-prompt="$"}
        $ kubectl patch secret/cluster1-secrets -p '{"data":{"pmmserverkey": '$(echo -n new_key | base64)'}}'
        ```

3. Update the `pmm`
    section in the
    [deploy/cr.yaml :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/main/deploy/cr.yaml)
    file.

    * set `pmm.enabled=true`
    * set the `pmm.serverHost` key to your PMM Server hostname or IP address
        (it should be resolvable and reachable from within your cluster)
    
4. When done, apply the edited `deploy/cr.yaml` file:

    ```{.bash data-prompt="$"}
    $ kubectl apply -f deploy/cr.yaml
    ```

5. Check that corresponding Pods are not in a cycle of stopping and restarting.
    This cycle occurs if there are errors on the previous steps:

    ```{.bash data-prompt="$"}
    $ kubectl get pods
    $ kubectl logs cluster1-mysql-0 -c pmm-client
    ```

6. Now you can access PMM via *https* in a web browser, with the
    login/password authentication, and the browser is configured to show
    Percona Server for MySQL metrics.
