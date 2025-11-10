#!/usr/bin/env python3
"""
Generate a backup workflow diagram using the diagrams library.
This script creates a diagram showing how backups work in the Percona Operator for MySQL.

Based on the blueprint:
- Operator (top-left) creates a Backup Job
- Backup Pod (middle-left) sends HTTP request
- MySQL Pod (middle-right) contains Xtrabackup and MySQL containers
- Cloud Storage (top-right) receives backup data
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.k8s.compute import Pod, Job
from diagrams.k8s.others import CRD
from diagrams.generic.storage import Storage

def generate_backup_diagram():
    """Generate the backup workflow diagram."""
    
    with Diagram("Backup Workflow", 
                 filename="docs/assets/images/backup-workflow",
                 show=False,
                 outformat="svg",
                 graph_attr={"rankdir": "LR", "nodesep": "2.0", "ranksep": "2.5", "pad": "0.5", "dpi": "300"}):
        
        # Operator (top-left area)
        operator = CRD("Operator")
        
        # Backup Pod (middle-left)
        backup_pod = Job("Backup Pod")
        
        # MySQL Pod with containers (middle-right)
        # Cluster represents the Pod, containing two containers
        with Cluster("MySQL Pod"):
            # Containers within the Pod - Xtrabackup on top, MySQL below
            xtrabackup = Pod("Xtrabackup")
            mysql = Pod("MySQL")
            # Connect containers to show they're in the same pod (vertical stack)
            xtrabackup >> mysql
        
        # Cloud Storage (top-right area)  
        cloud_storage = Storage("Cloud Storage")
        
        # Main workflow connections with labels
        operator >> Edge(label="Backup Job", style="bold", color="black") >> backup_pod
        backup_pod >> Edge(label="HTTP", style="bold", color="black") >> xtrabackup
        xtrabackup >> Edge(label="Backup Data", style="bold", color="black") >> cloud_storage

if __name__ == "__main__":
    generate_backup_diagram()
    print("Diagram generated successfully at docs/assets/images/backup-workflow.svg")

