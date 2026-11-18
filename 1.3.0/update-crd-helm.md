> For the complete documentation index, see [llms.txt](https://docs.percona.com/percona-operator-for-mysql/1.3.0/llms.txt).

# Upgrade the Operator and CRD via Helm

If you have [installed the Operator using Helm](https://docs.percona.com/percona-operator-for-mysql/1.3.0/helm.html), you can upgrade the Operator with the `helm upgrade` command.

The helm upgrade command updates only the Operator deployment. The [update flow for the database management system](https://docs.percona.com/percona-operator-for-mysql/1.3.0/update-db.html) is the same for all installation methods, whether it was installed via Helm or `kubectl`.

1. Update the [Custom Resource Definition](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/) for the Operator, taking it from the official repository on GitHub, and do the same for the Role-based access control:

   ```
   kubectl apply --server-side -f https://raw.githubusercontent.com/percona/percona-server-mysql-operator/v1.3.0/deploy/crd.yaml
   kubectl apply --server-side -f https://raw.githubusercontent.com/percona/percona-server-mysql-operator/v1.3.0/deploy/rbac.yaml
   ```

1. Next, update the Operator deployment.

   **With default parameters**

   If you installed the Operator with default parameters, the upgrade can be done as follows:

   ```
   helm upgrade my-op percona/ps-operator --version 1.3.0
   ```

   **With customized parameters**

   If you installed the Operator with some [customized parameters](https://github.com/percona/percona-helm-charts/tree/main/charts/ps-operator#installing-the-chart) , you should list these options in the upgrade command.

   You can get the list of the used options in YAML format with the `helm get values my-op -a > my-values.yaml` command. Then pass this file directly to the upgrade command as follows:

   ```
   helm upgrade my-op percona/ps-operator --version 1.3.0 -f my-values.yaml
   ```

1. Update the Custom Resource, the database and components. This step ensures all new features and improvements of the latest release work well within your environment.

[Update the Custom Resource, the database and components](#update-the-custom-resource-the-database-and-components)

## Update the Custom Resource, the database and components

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
