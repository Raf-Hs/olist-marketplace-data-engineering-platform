# Azure Architecture (design only)

No paid Azure resources were created. This document describes the intended
cloud mapping.

| Local component | Azure service |
|---|---|
| Raw/bronze/silver/gold files | Azure Data Lake Storage Gen2 |
| PySpark processing | Azure Databricks |
| Orchestration | Azure Data Factory |
| Secrets | Azure Key Vault |
| Monitoring | Azure Monitor |

## Migration notes

- Replace local filesystem paths with ADLS Gen2 abfss:// URIs.
- Move Spark code to Databricks notebooks/jobs.
- Use ADF pipelines to orchestrate ingestion -> Databricks -> SQL Warehouse.
- Store DB credentials in Key Vault; reference via linked services.
- Enable Azure Monitor diagnostics on all resources.
