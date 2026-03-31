# Define environment variables for cluster components

Tuning through environment variables helps when you need to:

* **Change timeouts and limits** for bootstrap, replication, or health checks without building a new image.
* **Match your platform** using standard names such as time zone or locale.
* **Feed flags or paths** into scripts and binaries that already read `getenv`-style configuration.
* **Keep secrets out of the CR** by loading keys from a Kubernetes Secret instead of plain YAML.

You declare this configuration in the Custom Resource. The Operator reconciles the cluster and updates Pod specs so containers receive the variables you specify.

## How to tune cluster components

You can tune cluster components in the following ways:

* Using existing environment variables
* Passing custom environment variables

You use the same Custom Resource fields for either way: `env` for explicit name/value pairs, and `envFrom` to load many variables from a ConfigMap or Secret. All values must be strings. Note that default values or behaviors may change between Operator versions. Check the sample [`deploy/cr.yaml`](https://github.com/percona/percona-server-mysql-operator/blob/main/deploy/cr.yaml) for reference.

You can combine both approaches for a single component: use existing environment variables where available, and add your own custom names as needed.

## Existing environment variables for cluster components

### Percona Server for MySQL environment variable

The following environment variables are available to tune Percona Server for MySQL

| Variable | Description |
| -------- | ----------- |
| `BOOTSTRAP_READ_TIMEOUT` | Non-negative integer (seconds). Read/write timeout for bootstrap and related MySQL client operations. |
| `BOOTSTRAP_CLONE_TIMEOUT` | Non-negative integer (seconds). Upper bound for clone operations during asynchronous bootstrap. |
| `ASYNC_SOURCE_RETRY_COUNT` | Non-negative integer. Used when configuring asynchronous replication. |
| `ASYNC_SOURCE_CONNECT_RETRY` | Non-negative integer. Used when configuring asynchronous replication. |

### HAProxy environment variables

The following environment variables are available for HAProxy

| Variable | Description |
| -------- | ----------- |
| `HA_CONNECTION_TIMEOUT` | Sets the timeout (in milliseconds) for HAProxy health checks on MySQL nodes. The default is 10000 milliseconds (10 seconds), but you can increase this value for unstable Kubernetes networking or if you experience soft lockups on nodes. |
| `HA_RLIMIT_NOFILE` | Sets the soft file descriptor limit in the entrypoint before HAProxy container starts. The default value is 1048576. If the set value is invalid, the Operator falls back to the default one. |
| `HA_SERVER_OPTIONS` | Extra server options passed into generated HAProxy server lines ([`haproxy_add_mysql_nodes.sh` :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/main/build/haproxy_add_mysql_nodes.sh)). |

## Custom environment variables

Apart from existing environment variables, you can also pass your custom configurations in these ways:

* [Set variables directly in the Custom Resource](#set-variables-directly-in-the-custom-resource) — Under `spec.<component>.env` as a list of `name` and `value` pairs.
* [Load variables from a ConfigMap](#load-variables-from-a-configmap) — Under `envFrom` with `configMapRef`; each key becomes an environment variable name.
* [Load variables from a Secret](#load-variables-from-a-secret) — Under `envFrom` with `secretRef`; use for sensitive values.

### Supported components

Custom env and envFrom are supported for these components:

| Component | Custom Resource options  |
| --------- | ------------------------ |
| MySQL | `spec.mysql.env`, `spec.mysql.envFrom` |
| HAProxy | `spec.proxy.haproxy.env`, `spec.proxy.haproxy.envFrom` |
| MySQL Router | `spec.proxy.router.env`, `spec.proxy.router.envFrom` |
| Orchestrator | `spec.orchestrator.env`, `spec.orchestrator.envFrom` |
| Backup storage (per entry) | `spec.backup.storages.<name>.containerOptions.env` |

Full field definitions are in [Custom Resource options](operator.md).

### Set variables directly in the Custom Resource

Use this method when you have a small number of non-sensitive values and you want everything in a single file.

For example, you want to set a time zone to keep logs aligned across MySQL containers and to override the soft file descriptor limit for HAProxy.

1. Edit the `deploy/cr.yaml` Custom Resource manifest:

    ```yaml
    spec:
      mysql:
        env:
          - name: TZ
            value: "UTC"
          - name: BOOTSTRAP_READ_TIMEOUT
            value: "600"
      proxy:
        haproxy:
          env:
            - name: HA_CONNECTION_TIMEOUT
              value: "30"
    ```

2. Apply the changes:

    ```
    kubectl apply -f deploy/cr.yaml -n <namespace>
    ```

### Load variables from a ConfigMap

Use this when you want to share the same variables across multiple clusters or update them without editing the Custom Resource.

1. Export the namespace where your cluster is running as an environment variable. Replace my-namespace with your value:
    
    ```bash
    export NAMESPACE=my-namespace
    ```

2. Create a ConfigMap file. For example, `mysql-configmap.yaml`. Specify the variables within:

    ```yaml title="mysql-configmap.yaml"
    apiVersion: v1
    kind: ConfigMap
    metadata:
      name: ps-mysql-env
    data:
      TZ: "UTC"
      BOOTSTRAP_READ_TIMEOUT: "600"
    ```

3. Create a ConfigMap object:
     
    ```bash
    kubectl apply -f mysql-configmap.yaml -n $NAMESPACE

4. Reference the ConfigMap in the Custom Resource:

    ```yaml
    spec:
      mysql:
        envFrom:
          - configMapRef:
              name: ps-mysql-env
    ```

5. Apply the changes:

    ```bash
    kubectl apply -f deploy/cr.yaml -n $NAMESPACE
    ```

### Load variables from a Secret

Use Secrets when you need to supply sensitive values (tokens, passwords, keys).

For example, you need to provide a token used by a custom sidecar container.

1. Encode your sensitive values before adding them to a Secret, as Kubernetes stores Secret data in base64-encoded form. This helps prevent accidental exposure of sensitive information in plaintext, even though it is not a secure encryption method.

    To encode an API token, run:

    ```bash
    echo -n "your-token" | base64
    ```

    Copy the encoded string for use in your Secret manifest

2. Export the namespace where your cluster is running as an environment variable. Replace my-namespace with your value:

    ```bash
    export NAMESPACE=my-namespace
    ```

3. Create a Secret configuration file, for example, `integration-token.yaml`. Specify your encoded value within:

    ```yaml title="integration-token.yaml"
    apiVersion: v1
    kind: Secret
    metadata:
      name: ps-app-env
    type: Opaque
    data:
      MY_INTEGRATION_TOKEN: "your-base64-encoded-token"
    ```

4. Create the Secret object:
    
    ```bash
    kubectl apply -f integration-token.yaml
    ```

5. Reference the Secret in your Custom Resource:

    ```yaml
    spec:
      mysql:
        envFrom:
          - secretRef:
              name: ps-app-env
    ```

6. Apply the changes:

    ```bash
    kubectl apply -f deploy/cr.yaml -n $NAMESPACE
    ```

### Combining `env` and `envFrom`

You can use both on one component. If a name appears in multiple sources, Kubernetes resolution rules apply: later explicit `env` entries override earlier values (see the [Kubernetes documentation :octicons-link-external-16:](https://kubernetes.io/docs/tasks/inject-data-application/define-environment-variable-container/)).

