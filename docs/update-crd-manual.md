# Upgrade the Operator and CRD manually

Before you start, export your namespace as an environment variable to simplify the configuration:

```bash
export NAMESPACE=<my-namespace>
```

The upgrade includes the following steps.

1. Update the Custom Resource Definition for the Operator and the Role-based access control. Take the latest versions from the official repository on GitHub with the following commands:

    ```bash
    kubectl apply --server-side -f https://raw.githubusercontent.com/percona/percona-server-mysql-operator/v{{ release }}/deploy/crd.yaml
    kubectl apply --server-side -f https://raw.githubusercontent.com/percona/percona-server-mysql-operator/v{{ release }}/deploy/rbac.yaml
    ```

2. Next, update the Percona Server for MySQL Operator Deployment in Kubernetes by changing the container image of the Operator Pod to the latest version. Find the image name for the current Operator release [in the list of certified images](images.md). Use the following command to update the Operator to the `{{ release }}` version:

    === "For single-namespace deployment"

        Use the following command if you deploy both the Operator and the database cluster in the same namespace:

        ```bash
        kubectl apply --server-side -f https://raw.githubusercontent.com/percona/percona-server-mysql-operator/v{{ release }}/deploy/operator.yaml -n $NAMESPACE
        ```

    === "For cluster-wide deployment"

        If you deployed the Operator to manage several clusters in different namespaces (the so-called [cluster-wide mode](cluster-wide.md)), use the following command:

        ```bash
        kubectl apply --server-side -f https://raw.githubusercontent.com/percona/percona-server-mysql-operator/v{{ release }}/deploy/cw-operator.yaml -n $NAMESPACE
        ```

    For previous releases, please refer to the [old releases documentation archive :octicons-link-external-16:](https://docs.percona.com/legacy-documentation/)

3. The deployment rollout will be automatically triggered.
    You can track the rollout process in real time with the
    `kubectl rollout status` command with the name of your cluster:

    ```bash
    kubectl rollout status deployments percona-server-mysql-operator -n $NAMESPACE
    ```

    !!! note

        Labels set on the Operator Pod will not be updated during upgrade.

4. Update the Custom Resource, the database and components. This step ensures all new features and improvements of the latest release work well within your environment.

## Update the Custom Resource, the database and components 

{% include 'assets/fragments/update-db-commands.txt' %}
