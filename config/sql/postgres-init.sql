CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE IF NOT EXISTS jobs (
    id BIGSERIAL PRIMARY KEY,
    job_id TEXT NOT NULL,
    trace_id TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    config JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS ingested_records (
    id BIGSERIAL,
    job_id TEXT NOT NULL,
    trace_id TEXT NOT NULL,
    observed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    record JSONB NOT NULL,
    PRIMARY KEY (id, observed_at)
);

CREATE TABLE IF NOT EXISTS analysis_results (
    id BIGSERIAL,
    job_id TEXT NOT NULL,
    trace_id TEXT NOT NULL,
    analyzed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    model TEXT NOT NULL,
    result JSONB NOT NULL,
    PRIMARY KEY (id, analyzed_at)
);

SELECT create_hypertable('ingested_records', 'observed_at', if_not_exists => TRUE);
SELECT create_hypertable('analysis_results', 'analyzed_at', if_not_exists => TRUE);
