#!/usr/bin/env python3
"""Generate the cross-site replication architecture diagram.

Based on the mockup in docs/assets/images/cross-site-replication-architecture.svg.

Requires:
    pip install diagrams

Run from repo root:
    python docs/assets/diagrams/cross-site-replication-architecture.py

Output:
    docs/assets/images/cross-site-replication-architecture-diagrams.png
"""

from pathlib import Path

from diagrams import Cluster, Diagram, Edge
from diagrams.k8s.compute import Pod
from diagrams.k8s.others import CRD
from diagrams.onprem.client import Client
from diagrams.onprem.database import MySQL

OUTPUT = Path(__file__).resolve().parents[1] / "images" / "cross-site-replication-architecture-diagrams.png"

# Edge styles used across the diagram
ASYNC_EDGE = Edge(label="Async replication", color="darkgreen")
ADMIN_API_EDGE = Edge(label="mysqlsh AdminAPI\n(MySQL protocol)")


def innodb_cluster_nodes():
    """Three linked MySQL instances inside an InnoDB Cluster (Group Replication)."""
    primary = MySQL("Primary\n+ PVC")
    secondary_1 = MySQL("Secondary\n+ PVC")
    secondary_2 = MySQL("Secondary\n+ PVC")
    primary - secondary_1 - secondary_2 - primary
    return primary, secondary_1, secondary_2


def member_site(cr_label: str):
    """Build one ClusterSet member site: Operator, CR, and InnoDB Cluster."""
    operator = Pod("PS Operator")
    ps_cr = CRD(cr_label)
    with Cluster("InnoDB Cluster"):
        primary, secondary_1, secondary_2 = innodb_cluster_nodes()
    operator >> ps_cr
    operator >> [primary, secondary_1, secondary_2]
    return operator, primary, secondary_1, secondary_2


graph_attr = {
    "fontsize": "13",
    "bgcolor": "white",
    "pad": "0.5",
    "splines": "spline",
    "nodesep": "0.9",
    "ranksep": "1.3",
}

with Diagram(
    "Cross-site replication architecture",
    filename=str(OUTPUT.with_suffix("")),
    outformat="png",
    show=False,
    direction="TB",
    graph_attr=graph_attr,
):
    app = Client("Application")

    with Cluster("InnoDB ClusterSet (PerconaServerMySQLClusterSet)"):
        # Orchestration site - pure controller; does not manage Pods in remote clusters
        with Cluster("Orchestration site (one Kubernetes namespace)"):
            clusterset_cr = CRD("PerconaServerMySQL\nClusterSet CR")
            controller = Pod("ClusterSet\ncontroller")
            runner = Pod("mysqlshell-\nrunner Pod")
            jobs = Pod("Jobs")
            clusterset_cr >> controller >> runner >> Edge(style="dashed") >> jobs

        # Member sites - independently managed PerconaServerMySQL clusters
        with Cluster("Member sites", direction="LR"):
            with Cluster("Primary site\nKubernetes cluster / region A"):
                op_primary, mysql_p_primary, _, _ = member_site(
                    "PerconaServerMySQL\nCR (group-replication)",
                )

            with Cluster("Replica site\nKubernetes cluster / region B"):
                op_replica, mysql_r_primary, _, _ = member_site(
                    "PerconaServerMySQL CR\nbootstrap: manual",
                )

            with Cluster("Replica site\nDifferent K8s / cloud / on-premises"):
                op_remote, mysql_o_primary, _, _ = member_site(
                    "PerconaServerMySQL\nCR (group-replication)",
                )

        # mysqlsh AdminAPI reaches MySQL endpoints at every site over the network
        runner >> ADMIN_API_EDGE >> [op_primary, op_replica, op_remote]

        # Async replication channels from the primary cluster PRIMARY member
        mysql_p_primary >> ASYNC_EDGE >> mysql_r_primary
        mysql_p_primary >> ASYNC_EDGE >> mysql_o_primary

    # Application traffic
    app >> Edge(label="Writes") >> mysql_p_primary
    app >> Edge(label="Reads") >> mysql_r_primary
    app >> Edge(label="Reads") >> mysql_o_primary

print(f"Wrote {OUTPUT}")
