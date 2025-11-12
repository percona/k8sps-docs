# Upgrading Percona Server for MySQL

You can decide how to run the database upgrades:

* [Automatically](update-db.md#automated-upgrade) - the Operator periodically checks for new versions of the database images and for valid image paths and automatically updates your deployment with the latest, recommended or a specific version of the database and other components included. To do so, the Operator queries a special
*Version Service* server at scheduled times. If the current version should be upgraded, the Operator updates the Custom
Resource to reflect the new image paths and sequentially deletes Pods,
allowing StatefulSet to redeploy the cluster Pods with the new image.

* [Manually](update-db.md#minor-upgrade-to-a-specific-version) - you manually update the Custom Resource and specify the desired version of the database. Then, depending on the configured [update strategy](update.md#update-strategies), either the Operator automatically updates the deployment to this version. Or you manually trigger the upgrade by deleting Pods.

The way to instruct the Operator how it should run the database upgrades is to set the `upgradeOptions.apply` Custom Resource option to one of the following:

* `Never` - the Operator never makes automatic upgrades. You must upgrade the Custom Resource and images manually.
* `Disabled` - the Operator doesn't not carry on upgrades automatically. You must upgrade the Custom Resource and images manually.
* `Recommended` - the Operator automatically updates the database and components to the version flagged as Recommended.
* `Latest` - the Operator automatically updates the database and components to the most recent available version
* `version` - specify the specific database version that you want to update to in the format `{{ ps84recommended }}`, `{{ ps80recommended }}`, etc. The Operator updates the database to it automatically. Find available versions [in the list of certified images](images.md).

For previous versions, refer to the [old releases documentation archive :octicons-link-external-16:](https://docs.percona.com/legacy-documentation/).

## Minor upgrade to a specific version

### Assumptions

For the procedures in this tutorial, we assume that you have set up the `Smart Update` strategy to update the objects in your database cluster.

### Before you start

Before updating the database, complete the following preparation steps:

1. Check the version of the Operator you have in your Kubernetes environment. If you need to update it, refer to the [Operator upgrade guide](update-operator.md).

2. Check the [Custom Resource](operator.md) manifest configuration to ensure the following:

    * `spec.updateStrategy` option is set to `SmartUpdate`
    * `spec.upgradeOptions.apply` option is set to `Never` or `Disabled` (this means that the Operator will not carry on upgrades automatically)

    ```yaml
    ...
    spec:
      updateStrategy: SmartUpdate
      upgradeOptions:
        apply: Disabled
        ...
    ```

3. Before selecting the update command, identify your current setup:

    * **MySQL version**: Check your current `mysql.image` value in your Custom Resource
    * **Replication type**: Check the `mysql.clusterType` option in your Custom Resource (`async` or `group`)
    * **Proxy type**: For async replication, you use HAProxy. For group replication, check if `proxy.haproxy.enabled` or `proxy.router.enabled` is set to `true` in your Custom Resource

4. We recommend to [update PMM Server :octicons-link-external-16:](https://docs.percona.com/percona-monitoring-and-management/3/pmm-upgrade/index.html) before upgrading PMM Client.

### Update commands

{% include 'assets/fragments/update-db-commands.txt' %}

### Track the upgrade progress

After applying the patch, the deployment rollout will be automatically triggered. You can track the rollout process in real time with the `kubectl rollout status` command with the name of your cluster:

```bash
kubectl rollout status sts ps-cluster1-ps
```

## Automated upgrade

### Assumptions

For the procedures in this tutorial, we assume that you have set up the `Smart Update` strategy to update the objects in your database cluster.

### Before you start

We recommend to [update PMM Server :octicons-link-external-16:](https://docs.percona.com/percona-monitoring-and-management/3/pmm-upgrade/index.html)  before upgrading PMM Client.

### Procedure

1. Check the version of the Operator you have in your Kubernetes environment. If you need to update it, refer to the [Operator upgrade guide](update-operator.md)

2. Change `spec.crVersion` option to match the version of the Custom Resource
    Definition upgrade while upgrading
    the Operator:

    ```yaml
    ...
    spec:
      crVersion: {{ release }}
      ...
    ```
    
    !!! note

        If you don't update crVersion, minor version upgrade is the only one to
        occur. For example, the image `percona-server:8.0.30-22` can
        be upgraded to `percona-server:8.0.32-24`.

3. Make sure that `spec.updateStrategy` option is set to `SmartUpdate`.

4. Change the `upgradeOptions.apply`  option from `Disabled` to one of the
    following values:

    * `Recommended` - the Operator will choose the most recent version of
        software flagged as "Recommended"

    * `Latest` - automatic upgrades will choose the most recent version of
        the software available,

    * *version number* - specify the desired version explicitly
        (version numbers are specified as `{{ ps80recommended }}`, etc.).
        Actual versions can be found [in the list of certified images](images.md)
        (for older releases, please refer to the [old releases documentation archive :octicons-link-external-16:](https://docs.percona.com/legacy-documentation)).

5. Make sure to set the valid Version Server URL for the `upgradeOptions.versionServiceEndpoint` key. The Operator checks the new software versions in the Version Server. If the Operator can’t reach the Version Server, the upgrades won’t happen.

    === "Percona’s Version Service (default)"

        You can use the URL of the official Percona’s Version Service (default).
        Set `upgradeOptions.versionServiceEndpoint` to `https://check.percona.com`.

    === "Version Service inside your cluster"
    
        Alternatively, you can run Version Service inside your cluster. This
        can be done with the `kubectl` command as follows:

        ```bash
        kubectl run version-service --image=perconalab/version-service --env="SERVE_HTTP=true" --port 11000 --expose
        ```

5. Specify the schedule to check for the new versions in in CRON format for the `upgradeOptions.schedule` option.

    The following example sets the midnight update checks with the official
    Percona's Version Service:

    ```yaml
    spec:
      updateStrategy: SmartUpdate
      upgradeOptions:
        apply: Recommended
        versionServiceEndpoint: https://check.percona.com
        schedule: "0 0 * * *"
    ...
    ```

    !!! note

        You can force an immediate upgrade by changing the schedule to
        `* * * * *` (continuously check and upgrade) and changing it back to
        another more conservative schedule when the upgrade is complete.

6. Apply your changes to the Custom Resource in the usual way:

    ```bash
    kubectl apply -f deploy/cr.yaml
    ```
