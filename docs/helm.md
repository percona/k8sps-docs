# Install Percona Server for MySQL using Helm

[Helm :octicons-link-external-16:](https://github.com/helm/helm) is the package manager for Kubernetes. Percona Helm charts can be found in [percona/percona-helm-charts :octicons-link-external-16:](https://github.com/percona/percona-helm-charts) repository on Github.

## Pre-requisites

Install Helm following its [official installation instructions :octicons-link-external-16:](https://docs.helm.sh/using_helm/#installing-helm).

!!! note

    Helm v3 is needed to run the following steps.

## Installation {.power-number}

1. Add the Percona’s Helm charts repository and make your Helm client up to
    date with it:

    ```{.bash data-prompt="$"}
    $ helm repo add percona https://percona.github.io/percona-helm-charts/
    $ helm repo update
    ```

2. Install the Percona Operator for MySQL:

    ```{.bash data-prompt="$"}
    $ helm install my-op percona/ps-operator
    ```

    The `my-op` parameter in the above example is the name of [a new release object :octicons-link-external-16:](https://helm.sh/docs/intro/using_helm/#three-big-concepts)
    which is created for the Operator when you install its Helm chart (use any
    name you like).

    !!! note

        If nothing explicitly specified, `helm install` command will work with `default` namespace. To use different namespace, provide it with the following additional parameter: `--namespace my-namespace`.

3. Install Percona Server for MySQL:

    ```{.bash data-prompt="$"}
    $ helm install my-db percona/ps-db
    ```

    The `my-db` parameter in the above example is the name of [a new release object :octicons-link-external-16:](https://helm.sh/docs/intro/using_helm/#three-big-concepts) which is created for the Percona Server for MySQL when you install its Helm chart (use any name you like).

## Installing Percona Server for MySQL with customized parameters

The command above installs Percona Server for MySQL with [default parameters](operator.md). Custom options can be passed to a `helm install` command as a `--set key=value[,key=value]` argument. The options passed with a chart can be any of the [Custom Resource options :octicons-link-external-16:](https://github.com/percona/percona-helm-charts/tree/main/charts/ps-db#installing-the-chart).

The following example will deploy a Percona Server for MySQL in the `my-namespace` namespace, with disabled backups and 20 Gi storage:

```{.bash data-prompt="$"}
$ helm install my-db percona/ps-db \
  --set mysql.volumeSpec.pvc.resources.requests.storage=20Gi \
  --set backup.enabled=false
```

## Next steps

[Connect to Percona Server for MySQL :material-arrow-right:](connect.md){.md-button}

