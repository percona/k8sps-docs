#!/usr/bin/env python3
"""Generate the cross-site replication ClusterSet architecture diagram.

Requires: pip install diagrams
Run from repo root:
    python docs/assets/diagrams/cross-site-replication-clusterset.py

Output: docs/assets/images/cross-site-replication-clusterset-diagrams.png
"""

from pathlib import Path

from diagrams import Cluster, Diagram, Edge
from diagrams.k8s.compute import Pod
from diagrams.k8s.others import CRD
from diagrams.onprem.client import Client
from diagrams.onprem.compute import Server
from diagrams.onprem.database import MySQL
from diagrams.onprem.network import HAProxy

OUTPUT = Path(__file__).resolve().parents[1] / "images" / "cross-site-replication-clusterset-diagrams.png"

graph_attr = {
    "fontsize": "13",
    "bgcolor": "white",
    "pad": "0.4",
    "splines": "spline",
    "nodesep": "0.8",
    "ranksep": "1.2",
}

with Diagram(
    "Cross-site replication ClusterSet",
    filename=str(OUTPUT.with_suffix("")),
    outformat="png",
    show=False,
    direction="TB",
    graph_attr=graph_attr,
):
    app = Client("Application")

    
    grouprepl = Edge(label="Group Replication", style="dashed", color="gray")
    asyncrepl = Edge(label="async replication", style="solid", color="green")

    with Cluster("ClusterSet", direction="LR"):
        with Cluster("ClusterSet management", direction="LR"):
            clusterset_cr = CRD("PerconaServerMySQL\nClusterSet CR")
            controller = Pod("ClusterSet\ncontroller")
            runner = Pod("mysqlshell-\nrunner Pod")
            clusterset_cr << controller >> runner
       

        with Cluster(""):
            with Cluster("Kubernetes cluster — primary"):
                op_primary = Pod("PS Operator")
                with Cluster("MySQL Cluster primary"):
                    mysql_primary1 = MySQL("Primary")
                    mysql_primary2 = MySQL("Secondary")
                    mysql_primary3 = MySQL("MySQL Pod")
                    mysql_primary1 - mysql_primary2 - mysql_primary3 - mysql_primary1 << grouprepl
                haproxy_primary = HAProxy("HAProxy")
                op_primary >> mysql_primary1 >> haproxy_primary

            with Cluster("Kubernetes cluster — replica"):
                op_replica = Pod("PS Operator")
                with Cluster("MySQL Cluster primary"):
                    mysql_replica1 = MySQL("Primary")
                    mysql_replica2 = MySQL("Secondary")
                    mysql_replica3 = MySQL("Secondary")
                    mysql_replica1 - mysql_replica2 - mysql_replica3 - mysql_replica1 << grouprepl
                haproxy_replica = HAProxy("HAProxy")
                op_replica >> mysql_replica1 >> haproxy_replica

            with Cluster("On-premises MySQL"):
                mysql_nodes = Server("MySQL nodes")
                haproxy_onprem = HAProxy("HAProxy")
                mysql_nodes >> haproxy_onprem

        runner >> Edge(label="mysqlsh AdminAPI") >> [op_primary, op_replica, mysql_nodes]
        mysql_primary1 >> Edge(label="Async replication", color="darkgreen") >> mysql_replica1
        mysql_primary1 >> Edge(label="Async replication", color="darkgreen") >> mysql_nodes
        op_primary >> Edge(label="Async replication", style="dashed", color="gray") >> op_replica

    app >> Edge(label="Writes and reads") >> mysql_primary1
    app >> Edge(label="Reads") >> mysql_replica1
    app >> Edge(label="Reads") >> mysql_nodes

print(f"Wrote {OUTPUT}")
