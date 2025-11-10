# Upgrade the Operator and CRD

To update the Operator, you need to update the Custom Resource Definition (CRD) and the Operator deployment. Also we recommend to update the Kubernetes database cluster configuration by updating the Custom Resource and the database components to the latest version. This step ensures that all new features that come with the Operator release work in your environment.

## Considerations for Kubernetes Cluster versions and upgrades

1. Before upgrading the Kubernetes cluster, have a disaster recovery plan in place. Ensure that a backup is taken prior to the upgrade.

2. Plan your Kubernetes cluster or Operator upgrades with version compatibility in mind.

    The Operator is supported and tested on specific Kubernetes versions. Always refer to the Operator's [release notes](ReleaseNotes/index.md) to verify the supported Kubernetes platforms.

    Note that while the Operator might run on unsupported or untested Kubernetes versions, this is not recommended. Doing so can cause various issues, and in some cases, the Operator may fail if deprecated API versions have been removed.

3. During a Kubernetes cluster upgrade, you must also upgrade the `kubelet`. It is advisable to drain the nodes hosting the database Pods during the upgrade process.

4. During the `kubelet` upgrade, nodes transition between `Ready` and `NotReady` states. Also in some scenarios, older nodes may be replaced entirely with new nodes. Ensure that nodes hosting database or proxy pods are functioning correctly and remain in a stable state after the upgrade.

5. Regardless of the upgrade approach, pods will be rescheduled or recycled. Plan your Kubernetes cluster upgrade accordingly to minimize downtime and service disruption.

## Considerations for Operator upgrades

1. The Operator version has three digits separated by a dot (`.`) in the format `major.minor.patch`. Here's how you can understand the version `1.0.0`:

    * `1` is the major version 
    * `0` is the minor version
    * `1` is the patch version.

    You can only upgrade the Operator to the nearest `major.minor` version (for example, from `1.0.0` to `1.0.1`).

    If the current Operator version and the version you want to upgrade to differ by more than one minor version, you need to upgrade step by step. For example, if your current version is `1.0.0` and you want to move to `1.0.2`, first upgrade to `1.0.1`, then to `1.0.2`.

    Check the [Release notes index](ReleaseNotes/index.md) for the list of the Operator versions.

2. CRD supports the **last 3 minor versions of the Operator**. This means it is
compatible with the newest Operator version and the two older minor versions.

3. The API version in CRDs is changed from `v1alpha` to `v1`. To update to version 0.12.0, you must manually delete the CRDs, apply new ones and recreate the cluster. To keep the data, do the following:

    * check that the `percona.com/delete-mysql-pvc` finalizer is not enabled in `deploy/cr.yaml`
    * don't delete PVCs manually
    * Recreate the cluster with the same name. The Operator then automatically reuses the same PVCs.

### Manual upgrade

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
        kubectl apply --server-side -f https://raw.githubusercontent.com/percona/percona-server-mysql-operator/v{{ release }}/deploy/operator.yaml
        ```

    === "For cluster-wide deployment"

        If you deployed the Operator to manage several clusters in different namespaces (the so-called [cluster-wide mode](cluster-wide.md)), use the following command

        ```bash
        kubectl apply --server-side -f https://raw.githubusercontent.com/percona/percona-server-mysql-operator/v{{ release }}/deploy/cw-operator.yaml
        ```

   
    For previous releases, please refer to the [old releases documentation archive :octicons-link-external-16:](https://docs.percona.com/legacy-documentation/)

3. The deployment rollout will be automatically triggered.
    You can track the rollout process in real time with the
    `kubectl rollout status` command with the name of your cluster:

    ```bash
    kubectl rollout status deployments percona-server-mysql-operator
    ```

    !!! note

        Labels set on the Operator Pod will not be updated during upgrade.

4. Update the Custom Resource, the database and components. This step ensures all new features and improvements of the latest release work well within your environment. 

   [Update the Custom Resource, the database and components :material-arrow-down:](#update-the-custom-resource-the-database-and-components){.md-button}

### Upgrade via helm

If you have [installed the Operator using Helm](helm.md), you can upgrade the
Operator with the `helm upgrade` command.

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

### Update the Custom Resource, the database and components

{% include 'assets/fragments/update-db-commands.txt' %}
