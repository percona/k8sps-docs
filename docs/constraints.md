# Binding Distribution for MySQL components to Specific Kubernetes Nodes

The Operator automatically assigns Pods to nodes with sufficient resources for balanced distribution across the cluster. You can configure Pods to be scheduled on specific nodes. For example, for improved performance on the SSD
equipped machine or for cost optimization by choosing the nodes in the same availability zone.

Using the [deploy/cr.yaml :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/v{{release}}/deploy/cr.yaml) Custom Resource manifest, you can configure the following:

* Affinity and anti-affinity rules to bind Pods to specific Kubernetes nodes
* Taints and tolerations to ensure that Pods are not scheduled onto inappropriate nodes

## Affinity and Anti-affinity

Affinity controls Pod placement based on nodes which already have Pods with specific labels. Use affinity to:

* Reduce costs by placing Pods in the same availability zone
* Improve high availability by distributing Pods across different nodes or zones

The Operator provides two approaches:

* Simple - set anti-affinity using built-in options
* Advanced - using Kubernetes constraints

### Simple Anti-affinity

This approach does not require the knowledge of how Kubernetes assigns Pods to specific nodes.

Use the `topologyKey` option with these values:

* `kubernetes.io/hostname` - Pods avoid the same host
* `topology.kubernetes.io/zone` - Pods avoid the same zone  
* `topology.kubernetes.io/region` - Pods avoid the same region
* `none` - No constraints applied

**Example** 

This configuration forces Percona XtraDB Cluster Pods to avoid reside on the same node:

```yaml
affinity:
  antiAffinityTopologyKey: "kubernetes.io/hostname"
```

### Advanced anti-affinity via Kubernetes constraints

For complex scheduling requirements, use the `advanced` option. This disables the `topologyKey` effect and allows the use of standard Kubernetes affinity constraints:

```yaml
affinity:
   advanced:
     podAffinity:
       requiredDuringSchedulingIgnoredDuringExecution:
       - labelSelector:
           matchExpressions:
           - key: security
             operator: In
             values:
             - S1
         topologyKey: topology.kubernetes.io/zone
     podAntiAffinity:
       preferredDuringSchedulingIgnoredDuringExecution:
       - weight: 100
         podAffinityTerm:
           labelSelector:
             matchExpressions:
             - key: security
               operator: In
               values:
               - S2
           topologyKey: kubernetes.io/hostname
     nodeAffinity:
       requiredDuringSchedulingIgnoredDuringExecution:
         nodeSelectorTerms:
         - matchExpressions:
           - key: kubernetes.io/e2e-az-name
             operator: In
             values:
             - e2e-az1
             - e2e-az2
       preferredDuringSchedulingIgnoredDuringExecution:
       - weight: 1
         preference:
           matchExpressions:
           - key: another-node-label-key
             operator: In
             values:
             - another-node-label-value
```

See [Kubernetes affinity documentation :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/assign-pod-node/#inter-pod-affinity-and-anti-affinity-beta-feature) for detailed explanations of these options.

## Tolerations

Tolerations allow Pods to run on nodes with matching taints. A taint is a key-value pair associated with a node that marks the node to repel certain Pods.

Taints and tolerations work together to ensure Pods are not scheduled onto inappropriate nodes.

A toleration includes these fields:

* `key` - The taint key to match
* `operator` - Either `exists` (matches any value) or `equal` (requires exact value match)
* `value` - Required when `operator` is `equal`
* `effect` - The taint effect to tolerate:

  * `NoSchedule` - Pods cannot be scheduled on the node
  * `PreferNoSchedule` - Pods are discouraged from scheduling on the node
  * `NoExecute` - Pods are evicted from the node (with optional `tolerationSeconds`)

This is the example configuration of a toleration:

```yaml
tolerations:
- key: "node.alpha.kubernetes.io/unreachable"
  operator: "Exists"
  effect: "NoExecute"
  tolerationSeconds: 6000
```

### Common use cases

* **Dedicated nodes**: Reserve nodes for specific workloads by tainting them and adding corresponding tolerations to authorized Pods.

* **Special hardware**: Keep Pods that don't need specialized hardware (like GPUs) off dedicated nodes by tainting those nodes.

* **Node problems**: Handle node failures gracefully with automatic taints and tolerations.

See [Kubernetes Taints and Tolerations :octicons-link-external-16:](https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/) for detailed examples and use cases.

## Priority classes

Pods may belong to some *priority classes*. Priority classes help the scheduler distinguish important Pods when eviction is needed. To use priority classes:

1. Create PriorityClasses in your Kubernetes cluster
2. Specify `PriorityClassName` in the [deploy/cr.yaml :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator/blob/v{{release}}/deploy/cr.yaml) file:

```yaml
priorityClassName: high-priority
```

See [Kubernetes Pod Priority documentation :octicons-link-external-16:](https://kubernetes.io/docs/concepts/configuration/pod-priority-preemption) for more information on how to define and use priority classes in your cluster.
