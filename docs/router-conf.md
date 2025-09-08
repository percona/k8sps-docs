# MySQL Router Configuration

[MySQL Router :octicons-link-external-16:](https://dev.mysql.com/doc/mysql-router/8.0/en/) is lightweight middleware that provides transparent routing between your application and back-end MySQL servers. [MySQL Router is part of the Operator](architecture.md#design-overview) and is deployed during the installation. MySQL Router can be used as an alternative to [HAProxy based load balancing](haproxy-conf.md) when group replication between MySQL instances is turned on.

To use the Router, enable it and make sure that HAProxy is disabled. 

## Enable MySQL Router 

1. Edit the `deploy/cr.yaml` file

    ```yaml
    ...
    mysql:
      clusterType: group-replication
      ...
    proxy:
      haproxy:
        enabled: false
        ...
      router:
        enabled: true
        ...
    ```

2. Update the cluster to apply the new configuration:

    ```{.bash data-prompt="$"}
    $ kubectl apply -f deploy/cr.yaml
    ```

    When the process is over your cluster will obtain the `ready` status. You
    can check it with the following command:

    ```{.bash data-prompt="$"}
    $ kubectl get ps
    ```

    ??? example "Expected output"

        ```{.text .no-copy}
        NAME       REPLICATION         ENDPOINT                  STATE   MYSQL   ORCHESTRATOR   HAPROXY   ROUTER   AGE
        ps-cluster1   group-replication   ps-cluster1-router.default   ready   3                                3        53m
        ```

## Configure MySQL Router 

When enabled, the MySQL Router operates with the reasonable default settings and can be used in a variety of use cases such as high-availability and scalability.

If you need to fine-tune the Router for the needs of your application and/or usage scenario, you can do this using the following methods:

- Edit the `deploy/cr.yaml` file
- Use the ConfigMap

To illustrate this, let’s override the verbosity level and set it to `INFO`.

Before you start, check that you have [enabled the MySQL Router](#enable-mysql-router) for the Operator. 

=== "deploy/cr.yaml"
    
    The `router.configuration` subsection of the `deploy.cr.yaml` file contains the MySQL Router configuration. 

    1. To change the verbosity level, edit the configuration file as follows:

        ```yaml
        configuration: |
         [default]
         logging_folder=/tmp/router/log
         [logger]
         level=INFO
        ```

    2. Update the cluster to apply the new configuration

        ```{.bash data-prompt="$"}
        $ kubectl apply -f deploy.cr.yaml
        ```

=== "ConfigMap"

    A ConfigMap is a Kubernetes mechanism to pass or update configuration data inside a containerized application. 

    You can create a ConfigMap from a file using the `kubectl create configmap` command. For more information about ConfigMap usage, see [Configure a Pod to use a ConfigMap :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/configure-pod-configmap/#create-a-configmap).

    To pass the new verbosity level of MySQL Router to the Operator using the ConfigMap, do the following:

    1. Create the `mysqlrouter.conf` configuration file and specify the new verbosity level within. 

        ```ini
        [logger]
        level = INFO
        ```

    2. Get the name of your cluster to pass the configuration

        ```{.bash data-prompt="$"}
        $ kubectl get ps
        ```

    3. Create the ConfigMap. You should use the combination of the cluster name with the `-router` suffix as the naming convention for the ConfigMap. For example, to create the ConfigMap for the cluster `ps-cluster1`, the command is the following:


        ```{.bash data-prompt="$"}
        $ kubectl create configmap ps-cluster1-router --from-file=mysqlrouter.conf
        ```
        
        Replace the `ps-cluster1` with the corresponding name of your cluster.

    4. View the created ConfigMap using the following command:

        ```{.bash data-prompt="$"}
        $ kubectl describe configmaps ps-cluster1-mysql
        ```

 
