# Diagram Generation Scripts

This directory contains Python scripts for generating architecture diagrams using the [diagrams](https://diagrams.mingrammer.com/) library.

## Prerequisites

1. Install Python 3.7 or higher
2. Install Graphviz (required by the diagrams library):
   - **macOS**: `brew install graphviz`
   - **Ubuntu/Debian**: `sudo apt-get install graphviz`
   - **Windows**: Download from [Graphviz website](https://graphviz.org/download/)

3. Install the diagrams library:
   ```bash
   pip install diagrams
   ```

## Usage

### Generate Backup Workflow Diagram

To generate the backup workflow diagram:

```bash
python scripts/generate-backup-diagram.py
```

This will create `docs/assets/images/backup-workflow.svg`.

**Note**: The generated SVG may contain absolute paths to node images. If the diagram doesn't display correctly when viewed elsewhere, you may need to:
1. Ensure the diagrams library is installed in the same location
2. Or use a tool to convert embedded images to base64 data URIs
3. Or regenerate the diagram on the target system

## Scripts

- `generate-backup-diagram.py`: Generates a diagram showing the backup workflow in the Percona Operator for MySQL, including:
  - Operator (creates Backup Job)
  - Backup Pod (sends HTTP request)
  - MySQL Pod with Xtrabackup and MySQL containers
  - Cloud Storage (receives backup data)

