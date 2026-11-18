> For the complete documentation index, see [llms.txt](https://docs.percona.com/percona-operator-for-mysql/1.3.0/llms.txt).

# Upgrade the Operator and CRD manually

## Before you start

Export your namespace as an environment variable to simplify the configuration:

```
export NAMESPACE=<my-namespace>
```

## Upgrade the CRD and Operator Deployment

The upgrade includes the following steps.

1. Update the Custom Resource Definition for the Operator and the Role-based access control. Take the latest versions from the official repository on GitHub with the following commands:

   ```
   kubectl apply --server-side -f https://raw.githubusercontent.com/percona/percona-server-mysql-operator/v1.3.0/deploy/crd.yaml
   kubectl apply --server-side -f https://raw.githubusercontent.com/percona/percona-server-mysql-operator/v1.3.0/deploy/rbac.yaml
   ```

1. Next, update the Percona Server for MySQL Operator Deployment in Kubernetes by changing the container image of the Operator Pod to the latest version. Find the image name for the current Operator release [in the list of certified images](https://docs.percona.com/percona-operator-for-mysql/1.3.0/images.html). Use the following command to update the Operator to the `1.3.0` version:

   **For single-namespace deployment**

   Use the following command if you deploy both the Operator and the database cluster in the same namespace:

   ```
   kubectl apply --server-side -f https://raw.githubusercontent.com/percona/percona-server-mysql-operator/v1.3.0/deploy/operator.yaml -n $NAMESPACE
   ```

   **For cluster-wide deployment**

   If you deployed the Operator to manage several clusters in different namespaces (the so-called [cluster-wide mode](https://docs.percona.com/percona-operator-for-mysql/1.3.0/cluster-wide.html)), use the following command:

   ```
   kubectl apply --server-side -f https://raw.githubusercontent.com/percona/percona-server-mysql-operator/v1.3.0/deploy/cw-operator.yaml -n $NAMESPACE
   ```

   For previous releases, please refer to the [old releases documentation archive](https://docs.percona.com/legacy-documentation/)

1. The deployment rollout will be automatically triggered. You can track the rollout process in real time with the `kubectl rollout status` command with the name of your cluster:

   ```
   kubectl rollout status deployments percona-server-mysql-operator -n $NAMESPACE
   ```

   Note

   Labels set on the Operator Pod will not be updated during upgrade.

1. Update the Custom Resource, the database and components. This step ensures all new features and improvements of the latest release work well within your environment.

## Update the Custom Resource, the database and components

### Pre-upgrade steps

Before updating the database, complete the following preparation steps:

1. Check the version of the Operator you have in your Kubernetes environment. If you need to update it, refer to the [Operator upgrade guide](https://docs.percona.com/percona-operator-for-mysql/1.3.0/update-operator.html).

1. Check the [Custom Resource](https://docs.percona.com/percona-operator-for-mysql/1.3.0/operator.html) manifest configuration to ensure the following:

   - `spec.updateStrategy` option is set to `SmartUpdate`
   - `spec.upgradeOptions.apply` option is set to `Never` or `Disabled` (this means that the Operator will not carry on upgrades automatically)

   ```
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

Version 1.3.0 requires backups for the [failover on asynchronous clusters](https://docs.percona.com/percona-operator-for-mysql/1.3.0/failover-async.html). After the Operator upgrade, reconciliation stops because status updates fail validation:

```
PerconaServerMySQL.ps.percona.com "ps-cluster1" is invalid: spec: Invalid value: "object": no such key: unsafeFlags evaluating rule: Invalid configuration: When 'mysql.clusterType' is set to 'async', 'backup.enabled' must be true unless 'unsafeFlags.asyncFailoverWithPossibleDataLoss' is enabled. Without backups a failover cannot recover the transactions stranded on the old primary
```

Before you upgrade, [enable and configure backups](https://docs.percona.com/percona-operator-for-mysql/1.3.0/backups-storage.html). To let reconciliation continue without backups, set [`unsafeFlags.asyncFailoverWithPossibleDataLoss`](https://docs.percona.com/percona-operator-for-mysql/1.3.0/operator.html#unsafeflagsasyncfailoverwithpossibledataloss) to `true`. Make sure you understand the tradeoffs.

Without backups, a failover cannot recover transactions that remain on the old primary.

### Update steps

Update the Custom Resource, the database, backup, proxy and PMM Client image names with a newer version tag. This step ensures all new features and improvements of the latest release work well within your environment.

Find the image names [in the list of certified images](https://docs.percona.com/percona-operator-for-mysql/1.3.0/images.html).

We recommend to update the PMM Server **before** the upgrade of PMM Client. If you haven’t updated your PMM Server yet, exclude PMM Client from the list of images to update.

Since this is a working cluster, the way to update the Custom Resource is to [apply a patch](https://kubernetes.io/docs/tasks/run-application/update-api-object-kubectl-patch/) with the `kubectl patch ps` command.

Select the command that matches your setup from the sections below.

**MySQL 8.4**

**Asynchronous replication (tech preview)**

Asynchronous replication uses HAProxy and Orchestrator. It does not use MySQL Router.

- **With PMM Client**

  ```
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

  ```
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

  ```
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

  After the upgrade, [enable point-in-time binlog collection](https://docs.percona.com/percona-operator-for-mysql/1.3.0/backups-pitr.html#enable-binlog-collection).

**Group replication with HAProxy**

Group replication with HAProxy uses HAProxy only. It does not use MySQL Router or Orchestrator.

- **With PMM Client**

  ```
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

  ```
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

  ```
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

  After the upgrade, [enable point-in-time binlog collection](https://docs.percona.com/percona-operator-for-mysql/1.3.0/backups-pitr.html#enable-binlog-collection).

**Group replication with MySQL Router**

Group replication with MySQL Router uses MySQL Router only. It does not use HAProxy or Orchestrator.

- **With PMM Client**

  ```
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

  ```
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

  ```
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

  After the upgrade, [enable point-in-time binlog collection](https://docs.percona.com/percona-operator-for-mysql/1.3.0/backups-pitr.html#enable-binlog-collection).

**MySQL 8.0**

**Asynchronous replication (tech preview)**

Asynchronous replication uses HAProxy and Orchestrator. It does not use MySQL Router.

- **With PMM Client**

  ```
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

  ```
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

  ```
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

  After the upgrade, [enable point-in-time binlog collection](https://docs.percona.com/percona-operator-for-mysql/1.3.0/backups-pitr.html#enable-binlog-collection).

**Group replication with HAProxy**

Group replication with HAProxy uses HAProxy only. It does not use MySQL Router or Orchestrator.

- **With PMM Client**

  ```
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

  ```
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

  ```
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

  After the upgrade, [enable point-in-time binlog collection](https://docs.percona.com/percona-operator-for-mysql/1.3.0/backups-pitr.html#enable-binlog-collection).

**Group replication with MySQL Router**

Group replication with MySQL Router uses MySQL Router only. It does not use HAProxy or Orchestrator.

- **With PMM Client**

  ```
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

  ```
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

  ```
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

## Post-upgrade steps

If point-in-time recovery is enabled, take a new base backup after the upgrade to make it a new starting point for subsequent point-in-time recovery.
