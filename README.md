# siem-elt-pipeline

A zero cost ELT pipeline for log ingestion, storage, transformation, and queries.

## Getting started

**_ If planning to use this in a production environment, please update the users and passwords in docker! _**

To start the application locally run: `docker-compose up --build`

The services will being running at:

- MinIO UI: http://localhost:9001 (User: admin, Pass: password)
- FastAPI Docs: http://localhost:8000/docs
- Prometheus UI: http://localhost:9090
- Grafana UI: http://localhost:3000 (User: admin, Pass: password)

To test that everything works as expected ingest the data test file

```
curl -X 'POST' \
  'http://localhost:8000/upload/' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@/test_data/json_logs.json'
```

The expected result message: `{"message": "File uploaded and processed successfully"}`

## System design

In order to create a low cost solution for a MVP, I choose a stack that could be easy developed with and scale up. All the tech is open source products that offered big data scale solutions compareable to more commercialized offerings.

MinIO: https://min.io

A S3 like self hosted data storage solution. This is used as a datalake for raw unscturctured and semi-structured data. Ideal for Data exploration and ML/AI like operations.

FastAPI: https://fastapi.tiangolo.com/

A python based API server that will facililate data ingestion, loading data to the datalake, data transformation and validation, and loading data into a datawarehouse.

Duckdb: https://duckdb.org/

A bigdata querying platform and data warehouse solution. This wasn't my first choice as timescale was a MUCH better option, but it was the most cost effective as the low low price of free. Duckdb stored transformed data and allows for optimizing querying in an SQL like experience.

Prometheus/Grafana: https://prometheus.io/docs/visualization/grafana/

I wanted visibility into the ingestion pipeline with a solution that was free and selfhosted and Prometheus with grafana solves the log transperency as well as data visualization in one.
