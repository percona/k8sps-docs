# Install Percona Server for MySQL cluster using kubectl

A Kubernetes Operator is a special type of controller introduced to simplify complex deployments. The Operator extends the Kubernetes API with custom resources.

The Percona Operator for MySQL is based on best practices for configuration and setup of a [Percona Server for MySQL :octicons-link-external-16:](https://www.percona.com/mysql/software/percona-server) in a Kubernetes-based environment on-premises or in the cloud.

We recommend installing the Operator with the [kubectl :octicons-link-external-16:](https://kubernetes.io/docs/tasks/tools/) command line utility. It is the universal way to interact with Kubernetes. Alternatively, you can install it using the [Helm :octicons-link-external-16:](https://github.com/helm/helm) package manager.

[Install with kubectl :material-arrow-down:](#prerequisites){.md-button} [Install with Helm :material-arrow-right:](helm.md){.md-button}

## Prerequisites

To install Percona Server for MySQL cluster, you need the following:
{.power-number}

1. The **kubectl** tool to manage and deploy applications on Kubernetes, included in most Kubernetes distributions. If not already installed, [follow its official installation instructions :octicons-link-external-16:](https://kubernetes.io/docs/tasks/tools/install-kubectl/).

2. A Kubernetes environment. You can deploy it on [Minikube :octicons-link-external-16:](https://github.com/kubernetes/minikube) for testing purposes or using any cloud provider of your choice. Check the list of our [officially supported platforms](System-Requirements.md#supported-platforms).

    !!! note "See also"

        * [Set up Minikube](minikube.md)
        * [Create and configure the GKE cluster](gke.md)
        * [Set up Amazon Elastic Kubernetes Service](eks.md)

## Procedure

Here's a sequence of steps to follow:
{.power-number}

1. Create the Kubernetes namespace for your cluster. It is a good practice to isolate workloads in Kubernetes by installing the Operator in a custom namespace. Replace the `<namespace>` placeholder with your value.

    ``` {.bash data-prompt="$" }
    $ kubectl create namespace <namespace>
    ```

    ??? example "Expected output"

        ``` {.text .no-copy}
        namespace/<namespace> was created
        ```

2. Deploy the Operator with the following command:

    ```{.bash data-prompt="$" }
    $ kubectl apply -f https://raw.githubusercontent.com/percona/percona-server-mysql-operator/v{{ release }}/deploy/bundle.yaml  -n <namespace>
    ```

    ??? example "Expected output"

        ```{.text .no-copy}
        customresourcedefinition.apiextensions.k8s.io/perconaservermysqlbackups.ps.percona.com created
        customresourcedefinition.apiextensions.k8s.io/perconaservermysqlrestores.ps.percona.com created
        customresourcedefinition.apiextensions.k8s.io/perconaservermysqls.ps.percona.com created
        serviceaccount/percona-server-mysql-operator created
        role.rbac.authorization.k8s.io/percona-server-mysql-operator-leaderelection created
        role.rbac.authorization.k8s.io/percona-server-mysql-operator created
        rolebinding.rbac.authorization.k8s.io/percona-server-mysql-operator-leaderelection created
        rolebinding.rbac.authorization.k8s.io/percona-server-mysql-operator created
        configmap/percona-server-mysql-operator-config created
        deployment.apps/percona-server-mysql-operator created
        ```

    As the result you will have the Operator Pod up and running.

3. Deploy Percona Server for MySQL cluster:

    ```{.bash data-prompt="$" }
    $ kubectl apply -f https://raw.githubusercontent.com/percona/percona-server-mysql-operator/v{{ release }}/deploy/cr.yaml -n <namespace>
    ```

    ??? example "Expected output"

        ```{.text .no-copy}
        perconaservermysql.ps.percona.com/ps-cluster1 created
        ```

4. Check the Operator and the database Pods status.

    ```{.bash data-prompt="$" }
    $ kubectl get ps -n <namespace>
    ```

    ??? example "Expected output"

        ```{.text .no-copy}
        NAME       REPLICATION         ENDPOINT                   STATE   MYSQL   ORCHESTRATOR   HAPROXY   ROUTER   AGE
        ps-cluster1   group-replication   ps-cluster1-haproxy.<namespace>   ready   3                                3        20m
        ```

    The creation process may take some time. When the process is over your cluster obtains the `ready` status.

You have successfully installed and deployed the Operator with default parameters.

The default configuration includes three HAProxy and three Percona Server for MySQL instances.

You can check the rest of the Operator's parameters in the [Custom Resource options reference](operator.md).

## Next steps

[Connect to Percona Server for MySQL :material-arrow-right:](connect.md){.md-button}

