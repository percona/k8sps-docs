> For the complete documentation index, see [llms.txt](https://docs.percona.com/percona-operator-for-mysql/1.3.0/llms.txt).

# Upgrading Percona Server for MySQL

You can decide how to run the database upgrades:

- [Automatically](https://docs.percona.com/percona-operator-for-mysql/1.3.0/update-db.md#automated-upgrade) - the Operator periodically checks for new versions of the database images and for valid image paths and automatically updates your deployment with the latest, recommended or a specific version of the database and other components included. To do so, the Operator queries a special *Version Service* server at scheduled times. If the current version should be upgraded, the Operator updates the Custom Resource to reflect the new image paths and sequentially deletes Pods, allowing StatefulSet to redeploy the cluster Pods with the new image.
- [Manually](https://docs.percona.com/percona-operator-for-mysql/1.3.0/update-db.md#minor-upgrade-to-a-specific-version) - you manually update the Custom Resource and specify the desired version of the database. Then, depending on the configured [update strategy](https://docs.percona.com/percona-operator-for-mysql/1.3.0/update.md#update-strategies), either the Operator automatically updates the deployment to this version. Or you manually trigger the upgrade by deleting Pods.

The way to instruct the Operator how it should run the database upgrades is to set the `upgradeOptions.apply` Custom Resource option to one of the following:

- `Never` - the Operator never makes automatic upgrades. You must upgrade the Custom Resource and images manually.
- `Disabled` - the Operator doesn’t not carry on upgrades automatically. You must upgrade the Custom Resource and images manually.
- `Recommended` - the Operator automatically updates the database and components to the version flagged as Recommended.
- `Latest` - the Operator automatically updates the database and components to the most recent available version
- `version` - specify the specific database version that you want to update to in the format `8.4.11-11.1`, `8.0.46-37.1`, etc. The Operator updates the database to it automatically. Find available versions [in the list of certified images](https://docs.percona.com/percona-operator-for-mysql/1.3.0/images.md).

For previous versions, refer to the [old releases documentation archive](https://docs.percona.com/legacy-documentation/) .

## Minor upgrade to a specific version

### Assumptions

For the procedures in this tutorial, we assume that you have set up the `SmartUpdate` strategy to update the objects in your database cluster.

### Pre-upgrade steps

Before updating the database, complete the following preparation steps:

1. Check the version of the Operator you have in your Kubernetes environment. If you need to update it, refer to the [Operator upgrade guide](https://docs.percona.com/percona-operator-for-mysql/1.3.0/update-operator.md).

1. Check the [Custom Resource](https://docs.percona.com/percona-operator-for-mysql/1.3.0/operator.md) manifest configuration to ensure the following:

   - `spec.updateStrategy` option is set to `SmartUpdate`
   - `spec.upgradeOptions.apply` option is set to `Never` or `Disabled` (this means that the Operator will not carry on upgrades automatically)

   ```yaml
   ...
   spec:
     updateStrategy: SmartUpdate
     upgradeOptions:
       apply: Disabled
       ...
   ```

1. Before selecting the update command, identify your current setup:

   - **MySQL version**: Check your current `mysql.image` value in your Custom Resource
   - **Replication type**: Check the `mysql.clusterType` option in your Custom Resource (`async` or `group-replication`)
   - **Proxy type**: For async replication, you use HAProxy. For group replication, check if `proxy.haproxy.enabled` or `proxy.router.enabled` is set to `true` in your Custom Resource

1. For `async` clusters, check that either `backups.enabled` is `true` or you set the `unsafeFlags.asyncFailoverWithPossibleDataLoss`. See [If you upgrade an asynchronous cluster](#if-you-upgrade-an-asynchronous-cluster) for more information.

1. We recommend to [update PMM Server](https://docs.percona.com/percona-monitoring-and-management/3/pmm-upgrade/index.html) before upgrading PMM Client.

#### If you upgrade an asynchronous cluster

Version 1.3.0 requires backups for the [failover on asynchronous clusters](https://docs.percona.com/percona-operator-for-mysql/1.3.0/failover-async.md). After the Operator upgrade, reconciliation stops because status updates fail validation:

```text
PerconaServerMySQL.ps.percona.com "ps-cluster1" is invalid: spec: Invalid value: "object": no such key: unsafeFlags evaluating rule: Invalid configuration: When 'mysql.clusterType' is set to 'async', 'backup.enabled' must be true unless 'unsafeFlags.asyncFailoverWithPossibleDataLoss' is enabled. Without backups a failover cannot recover the transactions stranded on the old primary
```

Before you upgrade, [enable and configure backups](https://docs.percona.com/percona-operator-for-mysql/1.3.0/backups-storage.md). To let reconciliation continue without backups, set [`unsafeFlags.asyncFailoverWithPossibleDataLoss`](https://docs.percona.com/percona-operator-for-mysql/1.3.0/operator.md#unsafeflagsasyncfailoverwithpossibledataloss) to `true`. Make sure you understand the tradeoffs.

Without backups, a failover cannot recover transactions that remain on the old primary.

### Update commands

Update the Custom Resource, the database, backup, proxy and PMM Client image names with a newer version tag. This step ensures all new features and improvements of the latest release work well within your environment.

Find the image names [in the list of certified images](https://docs.percona.com/percona-operator-for-mysql/1.3.0/images.md).

We recommend to update the PMM Server **before** the upgrade of PMM Client. If you haven’t updated your PMM Server yet, exclude PMM Client from the list of images to update.

Since this is a working cluster, the way to update the Custom Resource is to [apply a patch](https://kubernetes.io/docs/tasks/run-application/update-api-object-kubectl-patch/) with the `kubectl patch ps` command.

Select the command that matches your setup from the sections below.

**MySQL 8.4**

**Asynchronous replication (tech preview)**

Asynchronous replication uses HAProxy and Orchestrator. It does not use MySQL Router.

- **With PMM Client**

  ```bash
  kubectl patch ps ps-cluster1 --type=merge --patch '{
     "spec": {
         "crVersion":"1.3.0",
         "mysql":{ "image": "percona/percona-server:8.4.11-11.1" },
         "proxy":{
            "haproxy":{ "image": "percona/haproxy:2.8.29-1" }
         },
         "orchestrator":{ "image": "percona/percona-orchestrator:3.2.6-24" },
         "backup":{ "image": "percona/percona-xtrabackup:8.4.0-7.1" },
         "toolkit":{ "image": "percona/percona-toolkit:3.7.2-1" },
         "pmm": { "image": "percona/pmm-client:3.10.0" }
     }}'
  ```

- **Without PMM Client**

  ```bash
  kubectl patch ps ps-cluster1 --type=merge --patch '{
     "spec": {
         "crVersion":"1.3.0",
         "mysql":{ "image": "percona/percona-server:8.4.11-11.1" },
         "proxy":{
            "haproxy":{ "image": "percona/haproxy:2.8.29-1" }
         },
         "orchestrator":{ "image": "percona/percona-orchestrator:3.2.6-24" },
         "backup":{ "image": "percona/percona-xtrabackup:8.4.0-7.1" },
         "toolkit":{ "image": "percona/percona-toolkit:3.7.2-1" }
     }}'
  ```

- **With Binlog Server**

  ```bash
  kubectl patch ps ps-cluster1 --type=merge --patch '{
     "spec": {
         "crVersion":"1.3.0",
         "mysql":{ "image": "percona/percona-server:8.4.11-11.1" },
         "proxy":{
            "haproxy":{ "image": "percona/haproxy:2.8.29-1" }
         },
         "orchestrator":{ "image": "percona/percona-orchestrator:3.2.6-24" },
         "backup":{
            "image": "percona/percona-xtrabackup:8.4.0-7.1",
            "pitr": { "binlogServer": { "image": "percona/percona-server-mysql-operator:1.3.0-binlog-server-0.4.1" } }
         },
         "toolkit":{ "image": "percona/percona-toolkit:3.7.2-1" }
     }}'
  ```

  After the upgrade, [enable point-in-time binlog collection](https://docs.percona.com/percona-operator-for-mysql/1.3.0/backups-pitr.md#enable-binlog-collection).

**Group replication with HAProxy**

Group replication with HAProxy uses HAProxy only. It does not use MySQL Router or Orchestrator.

- **With PMM Client**

  ```bash
  kubectl patch ps ps-cluster1 --type=merge --patch '{
     "spec": {
         "crVersion":"1.3.0",
         "mysql":{ "image": "percona/percona-server:8.4.11-11.1" },
         "proxy":{
            "haproxy":{ "image": "percona/haproxy:2.8.29-1" }
         },
         "backup":{ "image": "percona/percona-xtrabackup:8.4.0-7.1" },
         "toolkit":{ "image": "percona/percona-toolkit:3.7.2-1" },
         "pmm": { "image": "percona/pmm-client:3.10.0" }
     }}'
  ```

- **Without PMM Client**

  ```bash
  kubectl patch ps ps-cluster1 --type=merge --patch '{
     "spec": {
         "crVersion":"1.3.0",
         "mysql":{ "image": "percona/percona-server:8.4.11-11.1" },
         "proxy":{
            "haproxy":{ "image": "percona/haproxy:2.8.29-1" }
         },
         "backup":{ "image": "percona/percona-xtrabackup:8.4.0-7.1" },
         "toolkit":{ "image": "percona/percona-toolkit:3.7.2-1" }
     }}'
  ```

- **With Binlog Server**

  ```bash
  kubectl patch ps ps-cluster1 --type=merge --patch '{
     "spec": {
         "crVersion":"1.3.0",
         "mysql":{ "image": "percona/percona-server:8.4.11-11.1" },
         "proxy":{
            "haproxy":{ "image": "percona/haproxy:2.8.29-1" }
         },
         "backup":{
            "image": "percona/percona-xtrabackup:8.4.0-7.1",
            "pitr": { "binlogServer": { "image": "percona/percona-server-mysql-operator:1.3.0-binlog-server-0.4.1" } }
         },
         "toolkit":{ "image": "percona/percona-toolkit:3.7.2-1" }
     }}'
  ```

  After the upgrade, [enable point-in-time binlog collection](https://docs.percona.com/percona-operator-for-mysql/1.3.0/backups-pitr.md#enable-binlog-collection).

**Group replication with MySQL Router**

Group replication with MySQL Router uses MySQL Router only. It does not use HAProxy or Orchestrator.

- **With PMM Client**

  ```bash
  kubectl patch ps ps-cluster1 --type=merge --patch '{
     "spec": {
         "crVersion":"1.3.0",
         "mysql":{ "image": "percona/percona-server:8.4.11-11.1" },
         "proxy":{
            "router":{ "image": "percona/percona-mysql-router:8.4.11" }
         },
         "backup":{ "image": "percona/percona-xtrabackup:8.4.0-7.1" },
         "toolkit":{ "image": "percona/percona-toolkit:3.7.2-1" },
         "pmm": { "image": "percona/pmm-client:3.10.0" }
     }}'
  ```

- **Without PMM Client**

  ```bash
  kubectl patch ps ps-cluster1 --type=merge --patch '{
     "spec": {
         "crVersion":"1.3.0",
         "mysql":{ "image": "percona/percona-server:8.4.11-11.1" },
         "proxy":{
            "router":{ "image": "percona/percona-mysql-router:8.4.11" }
         },
         "backup":{ "image": "percona/percona-xtrabackup:8.4.0-7.1" },
         "toolkit":{ "image": "percona/percona-toolkit:3.7.2-1" }
     }}'
  ```

- **With Binlog Server**

  ```bash
  kubectl patch ps ps-cluster1 --type=merge --patch '{
     "spec": {
         "crVersion":"1.3.0",
         "mysql":{ "image": "percona/percona-server:8.4.11-11.1" },
         "proxy":{
            "router":{ "image": "percona/percona-mysql-router:8.4.11" }
         },
         "backup":{
            "image": "percona/percona-xtrabackup:8.4.0-7.1",
            "pitr": { "binlogServer": { "image": "percona/percona-server-mysql-operator:1.3.0-binlog-server-0.4.1" } }
         },
         "toolkit":{ "image": "percona/percona-toolkit:3.7.2-1" }
     }}'
  ```

  After the upgrade, [enable point-in-time binlog collection](https://docs.percona.com/percona-operator-for-mysql/1.3.0/backups-pitr.md#enable-binlog-collection).

**MySQL 8.0**

**Asynchronous replication (tech preview)**

Asynchronous replication uses HAProxy and Orchestrator. It does not use MySQL Router.

- **With PMM Client**

  ```bash
  kubectl patch ps ps-cluster1 --type=merge --patch '{
     "spec": {
         "crVersion":"1.3.0",
         "mysql":{ "image": "percona/percona-server:8.0.46-37.1" },
         "proxy":{
            "haproxy":{ "image": "percona/haproxy:2.8.29-1" }
         },
         "orchestrator":{ "image": "percona/percona-orchestrator:3.2.6-24" },
         "backup":{ "image": "percona/percona-xtrabackup:8.0.35-36.1" },
         "toolkit":{ "image": "percona/percona-toolkit:3.7.2-1" },
         "pmm": { "image": "percona/pmm-client:3.10.0" }
     }}'
  ```

- **Without PMM Client**

  ```bash
  kubectl patch ps ps-cluster1 --type=merge --patch '{
     "spec": {
         "crVersion":"1.3.0",
         "mysql":{ "image": "percona/percona-server:8.0.46-37.1" },
         "proxy":{
            "haproxy":{ "image": "percona/haproxy:2.8.29-1" }
         },
         "orchestrator":{ "image": "percona/percona-orchestrator:3.2.6-24" },
         "backup":{ "image": "percona/percona-xtrabackup:8.0.35-36.1" },
         "toolkit":{ "image": "percona/percona-toolkit:3.7.2-1" }
     }}'
  ```

- **With Binlog Server**

  ```bash
  kubectl patch ps ps-cluster1 --type=merge --patch '{
     "spec": {
         "crVersion":"1.3.0",
         "mysql":{ "image": "percona/percona-server:8.0.46-37.1" },
         "proxy":{
            "haproxy":{ "image": "percona/haproxy:2.8.29-1" }
         },
         "orchestrator":{ "image": "percona/percona-orchestrator:3.2.6-24" },
         "backup":{
            "image": "percona/percona-xtrabackup:8.0.35-36.1",
            "pitr": { "binlogServer": { "image": "percona/percona-server-mysql-operator:1.3.0-binlog-server-0.4.1" } }
         },
         "toolkit":{ "image": "percona/percona-toolkit:3.7.2-1" }
     }}'
  ```

  After the upgrade, [enable point-in-time binlog collection](https://docs.percona.com/percona-operator-for-mysql/1.3.0/backups-pitr.md#enable-binlog-collection).

**Group replication with HAProxy**

Group replication with HAProxy uses HAProxy only. It does not use MySQL Router or Orchestrator.

- **With PMM Client**

  ```bash
  kubectl patch ps ps-cluster1 --type=merge --patch '{
     "spec": {
         "crVersion":"1.3.0",
         "mysql":{ "image": "percona/percona-server:8.0.46-37.1" },
         "proxy":{
            "haproxy":{ "image": "percona/haproxy:2.8.29-1" }
         },
         "backup":{ "image": "percona/percona-xtrabackup:8.0.35-36.1" },
         "toolkit":{ "image": "percona/percona-toolkit:3.7.2-1" },
         "pmm": { "image": "percona/pmm-client:3.10.0" }
     }}'
  ```

- **Without PMM Client**

  ```bash
  kubectl patch ps ps-cluster1 --type=merge --patch '{
     "spec": {
         "crVersion":"1.3.0",
         "mysql":{ "image": "percona/percona-server:8.0.46-37.1" },
         "proxy":{
            "haproxy":{ "image": "percona/haproxy:2.8.29-1" }
         },
         "backup":{ "image": "percona/percona-xtrabackup:8.0.35-36.1" },
         "toolkit":{ "image": "percona/percona-toolkit:3.7.2-1" }
     }}'
  ```

- **With Binlog Server**

  ```bash
  kubectl patch ps ps-cluster1 --type=merge --patch '{
     "spec": {
         "crVersion":"1.3.0",
         "mysql":{ "image": "percona/percona-server:8.0.46-37.1" },
         "proxy":{
            "haproxy":{ "image": "percona/haproxy:2.8.29-1" }
         },
         "backup":{
            "image": "percona/percona-xtrabackup:8.0.35-36.1",
            "pitr": { "binlogServer": { "image": "percona/percona-server-mysql-operator:1.3.0-binlog-server-0.4.1" } }
         },
         "toolkit":{ "image": "percona/percona-toolkit:3.7.2-1" }
     }}'
  ```

  After the upgrade, [enable point-in-time binlog collection](https://docs.percona.com/percona-operator-for-mysql/1.3.0/backups-pitr.md#enable-binlog-collection).

**Group replication with MySQL Router**

Group replication with MySQL Router uses MySQL Router only. It does not use HAProxy or Orchestrator.

- **With PMM Client**

  ```bash
  kubectl patch ps ps-cluster1 --type=merge --patch '{
     "spec": {
         "crVersion":"1.3.0",
         "mysql":{ "image": "percona/percona-server:8.0.46-37.1" },
         "proxy":{
            "router":{ "image": "percona/percona-mysql-router:8.0.46" }
         },
         "backup":{ "image": "percona/percona-xtrabackup:8.0.35-36.1" },
         "toolkit":{ "image": "percona/percona-toolkit:3.7.2-1" },
         "pmm": { "image": "percona/pmm-client:3.10.0" }
     }}'
  ```

- **Without PMM Client**

  ```bash
  kubectl patch ps ps-cluster1 --type=merge --patch '{
     "spec": {
         "crVersion":"1.3.0",
         "mysql":{ "image": "percona/percona-server:8.0.46-37.1" },
         "proxy":{
            "router":{ "image": "percona/percona-mysql-router:8.0.46" }
         },
         "backup":{ "image": "percona/percona-xtrabackup:8.0.35-36.1" },
         "toolkit":{ "image": "percona/percona-toolkit:3.7.2-1" }
     }}'
  ```

- **With Binlog Server**

  ```bash
  kubectl patch ps ps-cluster1 --type=merge --patch '{
     "spec": {
         "crVersion":"1.3.0",
         "mysql":{ "image": "percona/percona-server:8.0.46-37.1" },
         "proxy":{
            "router":{ "image": "percona/percona-mysql-router:8.0.46" }
         },
         "backup":{
            "image": "percona/percona-xtrabackup:8.0.35-36.1",
            "pitr": { "binlogServer": { "image": "percona/percona-server-mysql-operator:1.3.0-binlog-server-0.4.1" } }
         },
         "toolkit":{ "image": "percona/percona-toolkit:3.7.2-1" }
     }}'
  ```

### Track the upgrade progress

After applying the patch, the deployment rollout will be automatically triggered. You can track the rollout process in real time with the `kubectl rollout status` command with the name of your cluster:

```bash
kubectl rollout status sts ps-cluster1-ps
```

If the rollout stops because one MySQL Pod stays unready, see [Unblock a stuck rolling update](https://docs.percona.com/percona-operator-for-mysql/1.3.0/pause-mysql-pod.md#unblock-a-stuck-rolling-update).

### Post-upgrade steps

If point-in-time recovery is enabled, take a new base backup after the upgrade to make it a new starting point for subsequent point-in-time recovery.

## Automated upgrade

### Assumptions

For the procedures in this tutorial, we assume that you have set up the `Smart Update` strategy to update the objects in your database cluster.

### Before you start

We recommend to [update PMM Server](https://docs.percona.com/percona-monitoring-and-management/3/pmm-upgrade/index.html) before upgrading PMM Client.

### Procedure

1. Check the version of the Operator you have in your Kubernetes environment. If you need to update it, refer to the [Operator upgrade guide](https://docs.percona.com/percona-operator-for-mysql/1.3.0/update-operator.md)

1. Change `spec.crVersion` option to match the version of the Custom Resource Definition upgrade while upgrading the Operator:

   ```yaml
   ...
   spec:
     crVersion: 1.3.0
     ...
   ```

   Note

   If you don’t update `crVersion`, minor version upgrade is the only one to occur. For example, the image `percona-server:8.0.30-22` can be upgraded to `percona-server:8.0.32-24`.

1. Make sure that `spec.updateStrategy` option is set to `SmartUpdate`.

1. Change the `upgradeOptions.apply` option from `Disabled` to one of the following values:

   - `Recommended` - the Operator will choose the most recent version of software flagged as “Recommended”
   - `Latest` - automatic upgrades will choose the most recent version of the software available,
   - *version number* - specify the desired version explicitly (version numbers are specified as `8.0.46-37.1`, etc.). Actual versions can be found [in the list of certified images](https://docs.percona.com/percona-operator-for-mysql/1.3.0/images.md) (for older releases, please refer to the [old releases documentation archive](https://docs.percona.com/legacy-documentation/) ).

1. Make sure to set the valid Version Server URL for the `upgradeOptions.versionServiceEndpoint` key. The Operator checks the new software versions in the Version Server. If the Operator can’t reach the Version Server, the upgrades won’t happen.

   **Percona’s Version Service (default)**

   You can use the URL of the official Percona’s Version Service (default). Set `upgradeOptions.versionServiceEndpoint` to `https://check.percona.com`.

   **Version Service inside your cluster**

   Alternatively, you can run Version Service inside your cluster. This can be done with the `kubectl` command as follows:

   ```bash
   kubectl run version-service --image=perconalab/version-service --env="SERVE_HTTP=true" --port 11000 --expose
   ```

1. Specify the schedule to check for the new versions in in CRON format for the `upgradeOptions.schedule` option.

   The following example sets the midnight update checks with the official Percona’s Version Service:

   ```yaml
   spec:
     updateStrategy: SmartUpdate
     upgradeOptions:
       apply: Recommended
       versionServiceEndpoint: https://check.percona.com
       schedule: "0 0 * * *"
   ...
   ```

   Note

   You can force an immediate upgrade by changing the schedule to `* * * * *` (continuously check and upgrade) and changing it back to another more conservative schedule when the upgrade is complete.

1. Apply your changes to the Custom Resource in the usual way:

   ```bash
   kubectl apply -f deploy/cr.yaml
   ```
