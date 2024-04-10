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

        You can query your PMM Server installation to generate and get
        the API Key using `curl` and `jq` utilities. 

        To do it, you will need your PMM Server IP address or hostname, and the admin user credentials.

        !!! note

            If your PMM Server is installed [on your Kubernetes cluster](https://docs.percona.com/percona-monitoring-and-management/setting-up/server/helm.html),
            you can find the admin password as follows:

            ```{.bash data-prompt="$"}
            $ kubectl get secret pmm-secret -o jsonpath='{.data.PMM_ADMIN_PASSWORD}' | base64 --decode
            ```

            Also, such installation allows you to find out the proper PMM Server external IP using the appropriate
            Kubernetes Service:
   
            ```{.bash data-prompt="$"}
            $ kubectl get services monitoring-service -oyaml -o jsonpath='{.status.loadBalancer.ingress[0].ip}
            ```

        To generate API_KEY and get the value, run the following command, substituting the `<ADMIN_PASSWORD>`
        and `<PMM_SERVER_IP>` placeholders with appropriate values:

        ```{.bash data-prompt="$"}
        $ curl --insecure -X POST -H "Authorization: Basic  admin:<ADMIN_PASSWORD>" -H 'Content-Type: application/json'  -d '{"name":"operator", "role": "Admin"}' "https://<PMM_SERVER_IP>/graph/api/auth/keys" | jq .key | base64 --decode
        ```

        The above command generates new API Key named `operator`. API Key names are unique within the PMM Severer; to generate another API Key, you should use some different
        key name.

    !!! note

        The API key is not rotated. 

3. Specify the API key as the `pmmserverkey` value in the [users Secrets](users.md/#system-users) object.

    === "in Linux"

        ```{.bash data-prompt="$"}
        $ kubectl patch secret/cluster1-secrets -p '{"data":{"pmmserverkey": '$(echo -n new_key | base64 --wrap=0)'}}'
        ```

    === "in macOS"

        ```{.bash data-prompt="$"}
        $ kubectl patch secret/cluster1-secrets -p '{"data":{"pmmserverkey": '$(echo -n new_key | base64)'}}'
        ```

4. Update the `pmm`
    section in the
    [deploy/cr.yaml :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/main/deploy/cr.yaml)
    file.

    * set `pmm.enabled=true`
    * set the `pmm.serverHost` key to your PMM Server hostname or IP address
        (it should be resolvable and reachable from within your cluster)
    
5. When done, apply the edited `deploy/cr.yaml` file:

    ```{.bash data-prompt="$"}
    $ kubectl apply -f deploy/cr.yaml
    ```

6. Check that corresponding Pods are not in a cycle of stopping and restarting.
    This cycle occurs if there are errors on the previous steps:

    ```{.bash data-prompt="$"}
    $ kubectl get pods
    $ kubectl logs cluster1-mysql-0 -c pmm-client
    ```

7. Now you can access PMM via *https* in a web browser, with the
    login/password authentication, and the browser is configured to show
    Percona Server for MySQL metrics.
