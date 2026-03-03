import Ajv2020 from "ajv/dist/2020";
import schema from "../../../config/job-templates/job_config.schema.json";

const ajv = new Ajv2020({ allErrors: true });
export const validateJobConfig = ajv.compile(schema);
