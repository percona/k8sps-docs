# Labels and annotations

[Labels :octicons-link-external-16:](https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/)
and [annotations :octicons-link-external-16:](https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations/)
are used to attach additional metadata information to Kubernetes resources.

Labels and annotations are rather similar but differ in purpose. 

**Labels** are used by Kubernetes to identify and select objects. They enable filtering and grouping, allowing users to apply selectors for operations like deployments or scaling. 

**Annotations** are assigning additional *non-identifying* information that doesn't affect how Kubernetes processes resources. They store descriptive information like deployment history, monitoring configurations or external integrations. 

The following diagram illustrates this difference:

```mermaid
graph TD
    A[Custom Resource] --> B[Operator]
    B --> C[Kubernetes resources]
    C --> D[Labels]
    C --> E[Annotations]
    D --> F[Selection]
    D --> G[Grouping]
    E --> H[External tools]
    E --> I[Documentation]
```

Both Labels and Annotations are assigned to the following objects managed by Percona Operator for MySQL:

* Custom Resource Definitions
* Custom Resources
* Deployments
* Services
* StatefulSets
* PVCs
* Pods
* ConfigMaps and Secrets

## When to use labels and annotations

Use **Labels** when:

* The information is used for object selection
* The data is used for grouping or filtering
* The information is used by Kubernetes controllers
* The data is used for operational purposes

Use **Annotations** when:

* The information is for external tools
* The information is used for debugging
* The data is used for monitoring configuration

## Labels and annotations used by Percona Operator for MySQL

### Labels

| Name                        | Objects                          | Description                                      | Example values                          |
|-----------------------------|-----------------------------------|------------------------------------------------|-----------------------------------------|
| `app.kubernetes.io/name`      | Services, StatefulSets, Deployments, etc. | Specifies the name of the application          | percona-server  |
| `app.kubernetes.io/instance`  | Services, StatefulSets, Deployments | Identifies a specific instance of the application | ps-cluster1 |
| `app.kubernetes.io/managed-by`| Services, StatefulSets           | Indicates the controller managing the object    | percona-server-mysql-operator |
| `app.kubernetes.io/component`| Services, StatefulSets           | Specifies the component within the application  | mysql, haproxy, router    | database            |
| `app.kubernetes.io/part-of`   | Services, StatefulSets           | Indicates the higher-level application the object belongs to | percona-server                          |
| `app.kubernetes.io/version`  | CustomResourceDefinition          | Specifies the version of the Percona MySQL Operator. | {{release}} |
|`percona.com/exposed` | Services | Indicates if the service is exposed externally | true, false |
| `percona.com/cluster` | Custom Resource | Identifies the MySQL cluster instance | ps-cluster1 |
| `percona.com/backup-type`| Custom Resource | Specifies the type of backup being performed (e.g. cron for scheduled backups) | cron, manual |
| `percona.com/backup-ancestor`| Custom Resource | Specifies the name of the backup that was used as a base for the current backup | ps-cluster1-backup-{{year}}-05-23 |
| `mysql.percona.com/primary`| Pods | Marks the primary node in the MySQL cluster | true |

### Annotations

| Name                                              | Objects  | Description                                   | Example Values              |
|---------------------------------------------------|----------|-----------------------------------------------|-----------------------------|
| `service.beta.kubernetes.io/aws-load-balancer-backend-protocol` | Services | Specifies the protocol for AWS load balancers | http, http-test             |
| `service.beta.kubernetes.io/aws-load-balancer-backend`         | Services | Specifies the backend type for AWS load balancers | test-type                  |
| `controller-gen.kubebuilder.io/version`     | CustomResourceDefinition          | Indicates the version of the Kubebuilder controller-gen tool used.             |
| `percona.com/last-applied-tls` | Services   | Stores the hash of the last applied TLS configuration for the service |
| `percona.com/last-applied-secret` | Secrets | Stores the hash of the last applied user Secret configuration |
| `percona.com/configuration-hash` | Services | Used to track and validate configuration changes in the MySQL cluster components |
| `percona.com/last-config-hash` | Services | Stores the hash of the most recent configuration |
| `percona.com/passwords-updated`| Secrets | Indicates when passwords were last updated in the Secret |

## Setting labels and annotations in the Custom Resource

You can define both Labels and Annotations as `key-value` pairs in the metadata section of a YAML manifest for a specific resource.

### Set labels and annotations for Pods

You can set labels and annotations for Percona XtraBackup Pods, specific to the backup storage you use. To do this, use the `.spec.backup.storages.<STORAGE_NAME>.annotations`/`.spec.backup.storages.<STORAGE_NAME>.labels` keys in the Custom Resource manifest.

```yaml
spec:
  backup:
    storages:
      s3-us-west:
        annotations:
          testName: scheduled-backup
        labels:
          backupWorker: 'True'
```

### Set labels and annotations for Services

You can set labels and annotations for Services. For example, to control placement based on physical infrastructure or to improve your CI automation. 

Use the following options in the Custom Resource manifest:

* `.spec.mysql.exposePrimary.annotations`/`.spec.mysql.exposePrimary.labels` - for MySQL primary service
* `.spec.mysql.expose.annotations`/`.spec.mysql.expose.labels` - for MySQL service for every Pod
* `.spec.proxy.haproxy.expose.annotations`/`.spec.proxy.haproxy.expose.labels` - for HAProxy Service,
* `.spec.proxy.router.expose.annotations`/`.spec.proxy.router.expose.labels` - for MySQL Router Service
* `.spec.orchestrator.expose.annotations`/`.spec.orchestrator.expose.labels` -  for the Orchestrator Service

The following example shows how to set labels and annotations for a `<CLUSTER-NAME>-mysql-primary` service:

```yaml
spec:
  mysql:
    exposePrimary:
      enabled: true
      type: ClusterIP
      annotations:
        my-annotation: annotation-value
     ...
      labels:
        my-label: label-value
     ...
```


### Set global labels and annotations

You can also use the top-level spec `metadata.annotations` and `metadata.labels`
options to set annotations and labels at a global level, for all resources
created by the Operator:

```yaml
apiVersion: ps.percona.com/v1alpha1
kind: PerconaServerMySQL
metadata:
  name: ps-cluster1
  annotations:
    percona.com/issue-vault-token: "true"
  labels:
    ...
```

## Querying labels and annotations

To check which **labels** are attached to a specific object, use the additional `--show-labels` option of the `kubectl get` command.

For example, to see the Operator version associated with a Custom Resource Definition, use the following command:

```{.bash data-prompt="$"}
$ kubectl get crd perconaservermysqls.ps.percona.com --show-labels
```

??? example "Sample output"

    ```{.text .no-copy}
    NAME                                 CREATED AT             LABELS
    perconaservermysqls.ps.percona.com   2025-05-23T10:40:54Z   mysql.percona.com/version=v{{release}}
    ```

To check **annotations** associated with an object, use the following command: 

``` {.bash data-prompt="$" }
$ kubectl get <resource> <resource-name> -o jsonpath='{.metadata.annotations}'
```

For example, this command lists annotations assigned to a `ps-cluster1-mysql-0` Pod:

``` {.bash data-prompt="$" }
$ kubectl get pod ps-cluster1-mysql-0 -o jsonpath='{.metadata.annotations}'
```

??? example "Sample output"

    ```{.json .no-copy}
    {"percona.com/last-applied-tls":"c8dfc846cb62b75ba8eab61b7e86a46c"}
    ```

## Specifying labels and annotations ignored by the Operator

Sometimes various Kubernetes flavors can add their own annotations to the
objects managed by the Operator.

The Operator keeps track of all changes to its objects and can remove
annotations that it didn't create. 

Here's how the Operator manages labels and annotations:

* If there are no annotations or labels in the `expose*.*` subsections of the Custom Resource, the Operator does
nothing if a new label or an annotation is added to the Service object.

* The Operator doesn't remove any [global labels or annotations](#set-global-labels-and-annotations) that you defined in the `spec.metadata` section of the Custom Resource.

* The Operator keeps custom annotations and labels a Service if the `expose.labels` and `expose.annotations` fields in the Custom Resource are empty for this Service. If they are not empty, the Operator overrides custom labels and annotations with the `expose.annotations` and `expose.labels` values.

* If you [exposed individual Pods](expose.md#expose-individual-pods), the Operator removes unknown annotations and labels from Services that the Operator created for Pods.

You can still specify which annotations and labels the Operator should keep. It is useful if a cloud provider adds own labels and annotations to Services. Or you may have custom automation tools that add own labels or annotations and you need to keep them.

List these labels and annotations in the `spec.ignoreAnnotations` or `spec.ignoreLabels` fields of the `deploy/cr.yaml`, as follows:

```yaml
spec:
  ignoreAnnotations:
    - some.custom.cloud.annotation/smth
  ignoreLabels:
    - some.custom.cloud.label/smth
...
```

The label and annotation values must exactly match the ones defined for the Service to be kept.

## Delete labels and annotations

The Operator can only add custom labels and annotations to objects and it cannot delete them. This means you mst manually delete custom annotations and labels when they are no longer needed.

To delete a label or an annotation, run the following commands:

* For labels:

   ```
   kubectl label <resource> <name> <label-key>-
   ```

   where `<label-key>` is the label you want to delete.

* For annotations:

   ```
   kubectl annotate <resource> <name> <annotation-key>-
   ```

   where `<annotation-key>` is the annotation you want to delete.
