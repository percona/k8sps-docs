# Install Percona Server for MySQL using Helm

[Helm](https://github.com/helm/helm) is the package manager for Kubernetes. Percona Helm charts can be found in [percona/percona-helm-charts](https://github.com/percona/percona-helm-charts) repository on Github.

## Pre-requisites

Install Helm following its [official installation instructions](https://docs.helm.sh/using_helm/#installing-helm).

!!! note

    Helm v3 is needed to run the following steps.

## Installation

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

   The `my-op` parameter in the above example is the name of [a new release object](https://helm.sh/docs/intro/using_helm/#three-big-concepts)
   which is created for the Operator when you install its Helm chart (use any
   name you like).

   !!! note

       If nothing explicitly specified, `helm install` command will work
       with `default` namespace. To use different namespace, provide it with
       the following additional parameter: `--namespace my-namespace`.


3. Install Percona Server for MySQL:

   ```{.bash data-prompt="$"}
   $ helm install my-db percona/ps-db
   ```

   The `my-db` parameter in the above example is the name of [a new release object](https://helm.sh/docs/intro/using_helm/#three-big-concepts)
   which is created for the Percona Server for MySQL when you install its Helm
   chart (use any name you like).

The command above installs Percona Server for MySQL with default parameters.

You can find in the documentation for the charts which [Operator](https://github.com/percona/percona-helm-charts/tree/main/charts/ps-operator#installing-the-chart) and [database](https://github.com/percona/percona-helm-charts/tree/main/charts/ps-db#installing-the-chart) parameters can be customized during installation.
