# Install Percona Operator for MySQL with customized parameters

You can customize the configuration of Percona Server for MySQL and install it with customized parameters.

To check available configuration options, see [deploy/cr.yaml :octicons-link-external-16:](https://raw.githubusercontent.com/percona/percona-server-mysql-operator/v{{ release }}/deploy/cr.yaml) and [Custom Resource Options](operator.md).

!!! note

    Deploy the Operator in your namespace before you apply a customized cluster manifest. If you have not installed it yet, follow [Install with kubectl](kubectl.md) or [Install with Helm](helm.md).

=== ":simple-kubernetes: kubectl"

    To customize the configuration when installing with `kubectl`, do the following:

    1. Clone the repository with all manifests and source code by executing the following command:

        ```bash
        git clone -b v{{ release }} https://github.com/percona/percona-server-mysql-operator
        ```    

    2. Edit the required options and apply your modified `deploy/cr.yaml` file as follows:

         ```bash
         kubectl apply -f deploy/cr.yaml -n <namespace>        
         ```

=== ":simple-helm: Helm"

    You can install the Operator deployment and the Percona Server for MySQL cluster with custom parameters using Helm. Find what options you can customize in the [Operator chart documentation :octicons-link-external-16:](https://github.com/percona/percona-helm-charts/tree/main/charts/ps-operator#installing-the-chart) and the [Percona Server for MySQL chart documentation :octicons-link-external-16:](https://github.com/percona/percona-helm-charts/tree/main/charts/ps-db#installing-the-chart).

    You can provide custom parameters to Helm using either the `--set` flag or a `values.yaml` file. The `--set` flag is convenient for overriding a small number of parameters directly in the command line, while a `values.yaml` file is preferable when you want to manage many custom settings in one place. Both methods are fully supported by Helm and can be used as needed for your deployment.

    **Using `--set` flags**

    To pass a custom parameter to Helm, use the `--set key=value` flag with the `helm install` command.

    For example, to enable [Percona Monitoring and Management (PMM) :octicons-link-external-16:](https://docs.percona.com/percona-monitoring-and-management/2/index.html) for the database cluster, run:

    ```bash
    helm install my-db percona/ps-db --version {{ release }} --namespace my-namespace \
      --set mysql.image.tag={{ ps84recommended }} \
      --set pmm.enabled=true
    ```

    **Using a `values.yaml` file**

    Create a `values.yaml` file with your custom parameters and pass it to `helm install` with the `-f` or `--values` flag:

    ```bash
    helm install my-db percona/ps-db --version {{ release }} --namespace my-namespace -f values.yaml
    ```

    Example `values.yaml`:

    ```yaml
    mysql:
      image:
        tag: {{ ps84recommended }}
    pmm:
      enabled: true
    ```

    ## Naming conventions for Helm resources

    When you install a chart, Helm creates a release and uses the release name and chart name to generate resource names. By default, resources are named `release-name-chart-name`.

    You can override the default naming with the `nameOverride` or `fullnameOverride` options. Pass them using the `--set` flag or in your `values.yaml` file.

    | Option | Effect | Example |
    | ------ | ------ | ------- |
    | `nameOverride` | Replaces the chart name but keeps the release name in the generated name | `release-name-name-override` |
    | `fullnameOverride` | Replaces the entire generated name with the specified value | `fullname-override` |

    *Using `nameOverride`* — replaces the chart name but keeps the release name:

    ```bash
    helm install my-operator percona/ps-operator --namespace my-namespace \
      --set nameOverride=mysql-operator
    ```

    Deployment name: `my-operator-mysql-operator`.

    ```bash
    helm install cluster1 percona/ps-db -n my-namespace \
      --set nameOverride=mysql
    ```

    Cluster name: `cluster1-mysql`.

    *Using `fullnameOverride`* — replaces the full resource name:

    ```bash
    helm install my-operator percona/ps-operator --namespace my-namespace \
      --set fullnameOverride=percona-server-mysql-operator
    ```

    Deployment name: `percona-server-mysql-operator`.

    ```bash
    helm install cluster1 percona/ps-db -n my-namespace \
      --set fullnameOverride=my-db
    ```

    Cluster name: `my-db`.

    !!! note "Cluster naming"

        Use names that satisfy [Kubernetes naming rules :octicons-link-external-16:](https://kubernetes.io/docs/concepts/overview/working-with-objects/names/#names) for resources and DNS labels. If you use long release names together with `nameOverride` or `fullnameOverride`, ensure the resulting names stay within length limits your environment allows.

    ## Common Helm values reference

    The following table lists commonly used values for the Operator and database charts. For the full list of options, see the chart values files.

    | Value | Charts | Description |
    | ----- | ------ | ----------- |
    | `nameOverride` | [ps-operator](https://github.com/percona/percona-helm-charts/blob/main/charts/ps-operator/values.yaml), [ps-db](https://github.com/percona/percona-helm-charts/blob/main/charts/ps-db/values.yaml) | Replaces the chart name in generated resource names |
    | `fullnameOverride` | [ps-operator](https://github.com/percona/percona-helm-charts/blob/main/charts/ps-operator/values.yaml), [ps-db](https://github.com/percona/percona-helm-charts/blob/main/charts/ps-db/values.yaml) | Replaces the entire generated resource name |
    | `watchAllNamespaces` | [ps-operator](https://github.com/percona/percona-helm-charts/blob/main/charts/ps-operator/values.yaml) | Deploy the Operator in cluster-wide mode to watch all namespaces |
    | `disableTelemetry` | [ps-operator](https://github.com/percona/percona-helm-charts/blob/main/charts/ps-operator/values.yaml) | Disable telemetry collection. See [Telemetry](telemetry.md) for details |
