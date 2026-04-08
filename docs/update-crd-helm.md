
# Upgrade the Operator and CRD via Helm

If you have [installed the Operator using Helm](helm.md), you can upgrade the
Operator with the `helm upgrade` command.

The helm upgrade command updates only the Operator deployment. The [update flow for the database management system](update-db.md) is the same for all installation methods, whether it was installed via Helm or `kubectl`.

1. Update the [Custom Resource Definition  :octicons-link-external-16:](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/)
    for the Operator, taking it from the official repository on Github, and do
    the same for the Role-based access control:

    ```bash
    kubectl apply --server-side -f https://raw.githubusercontent.com/percona/percona-server-mysql-operator/v{{ release }}/deploy/crd.yaml
    kubectl apply --server-side -f https://raw.githubusercontent.com/percona/percona-server-mysql-operator/v{{ release }}/deploy/rbac.yaml
    ```

2. Next, update the Operator deployment. 

    === "With default parameters"

        If you installed the Operator with default parameters, the upgrade can be done as follows: 
        
        ```bash 
        helm upgrade my-op percona/ps-operator --version {{ release }}
        ```

    === "With customized parameters"

        If you installed the Operator with some [customized parameters :octicons-link-external-16:](https://github.com/percona/percona-helm-charts/tree/main/charts/pxc-operator#installing-the-chart), you should list these options in the upgrade command.

        You can get the list of the used options in YAML format with the `helm get values my-op -a > my-values.yaml` command. Then pass this file directly to the upgrade command as follows:

        ```bash
        helm upgrade my-op percona/ps-operator --version {{ release }} -f my-values.yaml
        ```

3. Update the Custom Resource, the database and components. This step ensures all new features and improvements of the latest release work well within your environment.

   [Update the Custom Resource, the database and components :material-arrow-down:](#update-the-custom-resource-the-database-and-components){.md-button}

## Update the Custom Resource, the database and components

{% include 'assets/fragments/update-db-commands.txt' %}