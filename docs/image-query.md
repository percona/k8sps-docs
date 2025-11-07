# Retrieve Percona certified images

When preparing for the upgrade, you must have the list of compatible images for a specific Operator version and the database version you wish to update to. You can either manually find the images in the [list of certified images](images.md) or you can get this list by querying the **Version Service** server. 

### What is the Version Service?

The **Version Service** is a centralized repository that the Percona Operator for MySQL connects to at scheduled times to get the latest information on compatible versions and valid image paths. This service is a crucial part of the automatic upgrade process, and it is enabled by default. Its landing page, `check.percona.com`, provides more details about the service itself.

### How to query the Version Service

You can manually query the Version Service using the `curl` command. The basic syntax is:

```bash
curl https://check.percona.com/versions/v1/ps-operator/<operator-version>/<ps-version> | jq -r '.versions[].matrix'
```

where:

* **`<operator-version>`** is the version of the Percona Operator for MySQL you are using.
* **`<ps-version>`** is the version of Percona Server for MySQL you want to get images for. This part is optional and helps filter the results. It can be a specific Percona Server for MySQL version (e.g. 8.4), a recommended version (e.g. 8.4-recommended), or the latest available version (e.g. 8.4-latest).

For example, to retrieve the list of images for the Operator version `0.11.0` and the latest version of Percona Server for MySQL 8.4, use the following command:

```bash
curl https://check.percona.com/versions/v1/ps-operator/0.11.0/8.4-latest | jq -r '.versions[].matrix'
```

??? example "Sample output"

    ```{.text .no-copy}
    "pmm": {
        "3.3.1": {
          "imagePath": "percona/pmm-client:3.3.1",
          "imageHash": "29a9bb1c69fef8bedc4d4a9ed0ae8224a8623fd3eb8676ef40b13fd044188cb4",
          "imageHashArm64": "50bccba4cb2c33bd3f6c5e37553bb70345de3f328b23a64ecfa63893f9025c83",
          "status": "recommended",
          "critical": true
        }
      },
      "haproxy": {
        "2.8.15": {
          "imagePath": "percona/haproxy:2.8.15",
          "imageHash": "49e6987a1c8b27e9111ae1f1168dd51f2840eb6d939ffc157358f0f259819006",
          "imageHashArm64": "",
          "status": "recommended",
          "critical": false
        }
      },
      "backup": {
        "8.4.0-3": {
          "imagePath": "percona/percona-xtrabackup:8.4.0-3",
          "imageHash": "01071522753ad94e11a897859bba4713316d08e493e23555c0094d68da223730",
          "imageHashArm64": "",
          "status": "available",
          "critical": false
        }
      },
      "operator": {
        "0.11.0": {
          "imagePath": "percona/percona-server-mysql-operator:0.11.0",
          "imageHash": "3068b1a4d81b5da7676e071040d3b44ff9fec5532cbfabb17f9c7612e8c9d35d",
          "imageHashArm64": "b50f215869ca3d9f6a52561171851e8ffa033ca30d0276556e220ad448418b61",
          "status": "recommended",
          "critical": false
        }
      },
      "mysql": {
        "8.4.5-5": {
          "imagePath": "percona/percona-server:8.4.5-5",
          "imageHash": "9628b1e598c0ec13c2a6b834caa1642bf77f2b4a2d7620b1ba2d8aaf2b708133",
          "imageHashArm64": "",
          "status": "available",
          "critical": false
        }
      },
      "router": {
        "8.4.5": {
          "imagePath": "percona/percona-mysql-router:8.4.5",
          "imageHash": "e890ecc49c297cc8882b54ba457ff4d25da896cb11269989fa072aa338d620c1",
          "imageHashArm64": "",
          "status": "available",
          "critical": false
        }
      },
      "orchestrator": {
        "3.2.6-17": {
          "imagePath": "percona/percona-orchestrator:3.2.6-17",
          "imageHash": "c1871ddc6ff3eaca7bb03c3aa11db880ae02d623db1203d0858f8566f56ea5f7",
          "imageHashArm64": "",
          "status": "recommended",
          "critical": false
        }
      },
      "toolkit": {
        "3.7.0": {
          "imagePath": "percona/percona-toolkit:3.7.0",
          "imageHash": "17ef2b69a97fa546d1f925c74ca09587ac215085c392761bb4d51f188baa6c0e",
          "imageHashArm64": "",
          "status": "recommended",
          "critical": false
        }
      }
    ```

To narrow down the search and check the Percona Server for MySQL images available for a specific Operator version (`0.11.0` in the following example), use the following command:

```bash
curl -s https://check.percona.com/versions/v1/ps-operator/0.11.0 | jq -r '.versions[0].matrix.mysql | to_entries[] | "\(.key)\t\(.value.imagePath)\t\(.value.status)"'
```

??? example "Sample output"
 
    ```{.text .no-copy}
    8.0.32-24   percona/percona-server:8.0.32-24    available
    8.0.33-25   percona/percona-server:8.0.33-25    available
    8.0.36-28   percona/percona-server:8.0.36-28    available
    8.0.40-31   percona/percona-server:8.0.40-31    available
    8.0.42-33   percona/percona-server:8.0.42-33    recommended
    8.4.5-5     percona/percona-server:8.4.5-5      available
    ```
