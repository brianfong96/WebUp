export type JobConfig = {
  job_id: string;
  ingestor_plugin: string;
  analyzer_plugin: {
    provider: "ollama" | "openai";
    model: "llama3" | "mistral" | "phi3" | string;
    temperature: number;
    prompt_template_id: string;
  };
  pipeline_settings: {
    max_parallelism: number;
    max_retries: number;
    cron: string;
  };
  storage_policy: {
    raw_retention_days: number;
    analyzed_retention_days: number;
    persist_artifacts: boolean;
  };
};
