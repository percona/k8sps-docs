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

1. The Operator version has three digits separated by a dot (`.`) in the format `major.minor.patch`. Here's how you can understand the version `1.0.1`:

    * `1` is the major version 
    * `0` is the minor version
    * `1` is the patch version.

    You can only upgrade the Operator to the nearest `major.minor` version (for example, from `1.0.0` to `1.1.0`).

    If the current Operator version and the version you want to upgrade to differ by more than one minor version, you need to upgrade step by step. For example, if your current version is `1.0.0` and you want to move to `1.2.0`, first upgrade to `1.1.0`, then to `1.2.0`.

    Check the [Release notes index](ReleaseNotes/index.md) for the list of the Operator versions.

2. CRD supports the **last 3 minor versions of the Operator**. This means it is
compatible with the newest Operator version and the two older minor versions.

3. The API version in CRDs is changed from `v1alpha` to `v1`. To update to version 0.12.0, you must manually delete the CRDs, apply new ones and recreate the cluster. To keep the data, do the following:

    * check that the `percona.com/delete-mysql-pvc` finalizer is not enabled in `deploy/cr.yaml`
    * don't delete PVCs manually
    * Recreate the cluster with the same name. The Operator then automatically reuses the same PVCs.

## Upgrade guides

Choose the upgrade instructions below based on how you originally deployed the Operator:

[Manual upgrade](update-crd-manual.md){.md-button}
[Upgrade via Helm](update-crd-helm.md){.md-button}
[Upgrade on OpenShift](update-openshift.md){.md-button}


