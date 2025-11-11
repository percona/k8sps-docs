# Install Percona Server for MySQL using Helm

[Helm :octicons-link-external-16:](https://github.com/helm/helm) is the package manager for Kubernetes. Percona Helm charts can be found in [percona/percona-helm-charts :octicons-link-external-16:](https://github.com/percona/percona-helm-charts) repository on Github.

## Prerequisites

Install Helm v3 and above following its [official installation instructions :octicons-link-external-16:](https://docs.helm.sh/using_helm/#installing-helm).

## Installation {.power-number}

1. Add the Percona Helm charts repository and make your Helm client up to
    date with it:

    ```bash
    helm repo add percona https://percona.github.io/percona-helm-charts/
    helm repo update
    ```

2. Install the Percona Operator for MySQL. It is a good practice to isolate workloads in Kubernetes by installing the Operator in a custom namespace. Replace the `my-namespace` value with your desired namespace in the following command:

    ```bash
    helm install my-op percona/ps-operator --namespace my-namespace --create-namespace 
    ```

    The `my-op` parameter in the above example is the name of [a new release object :octicons-link-external-16:](https://helm.sh/docs/intro/using_helm/#three-big-concepts)
    which is created for the Operator when you install its Helm chart. You can use any other name you like instead.

    ??? example "Expected output"

        ```{.text .no-copy}
        NAME: my-op
        LAST DEPLOYED: Sun Nov  9 10:23:13 2025
        NAMESPACE: my-namespace
        STATUS: deployed
        REVISION: 1
        TEST SUITE: None
        ```

3. Install Percona Server for MySQL:

    ```bash
    helm install my-db percona/ps-db --namespace my-namespace
    ```

    The `my-db` parameter in the above example is the name of [a new release object :octicons-link-external-16:](https://helm.sh/docs/intro/using_helm/#three-big-concepts) which is created for the Percona Server for MySQL when you install its Helm chart (use any name you like).

    ??? example "Expected output"

        ```{.text .no-copy}
        NAME: my-db
        LAST DEPLOYED: Sun Nov  9 10:26:41 2025
        NAMESPACE: my-namespace
        STATUS: deployed
        REVISION: 1
        TEST SUITE: None
        NOTES:
        ```        

The command above installs Percona Server for MySQL with [default parameters](operator.md). Custom options can be passed to a `helm install` command as a `--set key=value[,key=value]` argument. The options passed with a chart can be any of the [Custom Resource options :octicons-link-external-16:](https://github.com/percona/percona-helm-charts/tree/main/charts/ps-db#installing-the-chart).

The following example will deploy a Percona Server for MySQL in the `my-namespace` namespace, with disabled backups and 20 Gi storage:

```bash
helm install my-db percona/ps-db \
  --set mysql.volumeSpec.pvc.resources.requests.storage=20Gi \
  --set backup.enabled=false
```

You can find in the documentation for the charts which [Operator :octicons-link-external-16:](https://github.com/percona/percona-helm-charts/tree/main/charts/ps-operator#installing-the-chart) and [database :octicons-link-external-16:](https://github.com/percona/percona-helm-charts/tree/main/charts/ps-db#installing-the-chart) parameters can be customized during installation.

## Next steps

[Connect to Percona Server for MySQL :material-arrow-right:](connect.md){.md-button}
