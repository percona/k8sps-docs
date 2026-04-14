# Configure Operator environment variables

You can configure the Percona Operator for MySQL by setting environment variables on the Operator Deployment. This lets you tune Operator behavior without rebuilding images.

You can set environment variables in the following ways:

* For installations with `kubectl`, edit the Operator Deployment manifest (`deploy/bundle.yaml` / `deploy/operator.yaml` or `deploy/bundle-cw.yaml` / `deploy/operator-cw.yaml` in the [percona-server-mysql-operator :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator) repository) before you apply it. You can also change the existing Deployment with `kubectl patch` or `kubectl edit`.
* For Helm installations, you can set environment variables through Helm values. Use the [ps-operator chart values :octicons-link-external-16:](https://github.com/percona/percona-helm-charts/tree/main/charts/ps-operator).
* For OpenShift installations that use OLM, configure environment variables in the Subscription.

## Available environment variables

### `LOG_STRUCTURED`

Controls whether Operator logs are structured (JSON) or plain text.

| Value type | Default | Example |
| ---------- | ------- | ------- |
| string     | `"false"` | `"true"` |

**Example configuration:**

```yaml
env:
  - name: LOG_STRUCTURED
    value: "true"
```

Structured logs work well with tools such as [jq :octicons-link-external-16:](https://stedolan.github.io/jq/). See also [Check the logs](debug-logs.md).

### `LOG_LEVEL`

Sets the verbosity of Operator logs.

| Value type | Default | Example |
| ---------- | ------- | ------- |
| string     | `INFO`  | `DEBUG` |

Valid values are:

* `VERBOSE` or `DEBUG` — Most verbose; `VERBOSE` also enables additional diagnostic output in some code paths.
* `ERROR` — Error messages only.
* `INFO` — Standard informational messages (default).
  
Any other value falls back to `INFO` with a message in the log.

**Example configuration:**

```yaml
env:
  - name: LOG_LEVEL
    value: DEBUG
```

### `WATCH_NAMESPACE`

Specifies which namespaces the Operator watches for `PerconaServerMySQL` and related custom resources.

By default, the value is set to the Operator’s own namespace from the metadata.namespace option via a downward API `fieldRef`:

```yaml
- name: WATCH_NAMESPACE
  valueFrom:
    fieldRef:
      apiVersion: v1
      fieldPath: metadata.namespace
```

| Value type | Default | Example |
| ---------- | ------- | ------- |
| string     | See below | `ns-one,ns-two` or `""` |

Accepted values:

* If set to a comma-separated list, the Operator watches those specific namespaces. The namespace list must include the namespace where the Operator itself is deployed. Use this approach for the [multi-namespace deployment](cluster-wide.md).
* If set to an empty string (`""`), the Operator watches all namespaces. 
  
When you deploy the Operator in cluster-wide mode, it should be associated with the appropriate ClusterRole.

**Example configuration:**

```yaml
env:
 - name: WATCH_NAMESPACE
   value: "mysql,mysql-dev,mysql-prod"
```

### `DISABLE_TELEMETRY`

Disables anonymous telemetry data collection by the Operator. For what is collected when telemetry is enabled, see [Telemetry](telemetry.md).

| Value type | Default | Example |
| ---------- | ------- | ------- |
| string     | `"false"` | `"true"` |

**Example configuration:**

```yaml
env:
  - name: DISABLE_TELEMETRY
    value: "true"
```

## Update environment variables

### Using `kubectl patch`

You can update environment variables in an existing Operator Deployment by applying a patch. To keep existing environment variables, you must specify the full list of them.

Here’s how to do it:

1. Get the current environment variables:
    
    ```bash
    kubectl get deployment percona-server-mysql-operator -n <operator-namespace> -o jsonpath='{.spec.template.spec.containers[0].env}' | jq
    ```

2. Update the deployment. This example command keeps downward API for `WATCH_NAMESPACE` and sets `LOG_LEVEL` to `DEBUG`:

    ```bash
    kubectl patch deployment percona-server-mysql-operator -n <operator-namespace> \
      --type='json' \
      -p='[{"op": "replace", "path": "/spec/template/spec/containers/0/env", "value": [
        {"name": "LOG_STRUCTURED", "value": "false"},
        {"name": "LOG_LEVEL", "value": "DEBUG"},
        {"name": "WATCH_NAMESPACE", "valueFrom": {"fieldRef": {"apiVersion": "v1",     "fieldPath": "metadata.namespace"}}},
        {"name": "DISABLE_TELEMETRY", "value": "false"}
      ]}]'
    ```

Adjust the list to match your current Deployment (for example cluster-wide `WATCH_NAMESPACE` with a string `value` instead of `valueFrom`).

### Using `kubectl edit`

You can also edit the Deployment directly:

```bash
kubectl edit deployment percona-server-mysql-operator -n <operator-namespace>
```

Then modify the env section in the container specification, save, and exit. Kubernetes rolls out a new ReplicaSet for the Operator Pod.

After you change environment variables, the Operator Pod restarts with the new settings.
