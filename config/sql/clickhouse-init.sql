CREATE DATABASE IF NOT EXISTS webup;

CREATE TABLE IF NOT EXISTS webup.logs_stream
(
  timestamp DateTime64(3),
  service_name LowCardinality(String),
  severity LowCardinality(String),
  trace_id String,
  job_id String,
  message String
)
ENGINE = MergeTree
PARTITION BY toDate(timestamp)
ORDER BY (timestamp, service_name, trace_id);
