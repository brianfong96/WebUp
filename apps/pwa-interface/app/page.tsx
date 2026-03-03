"use client";

import { useMemo, useState } from "react";
import defaultJob from "../../../config/job-templates/default.job_config.json";
import { Play, ShieldCheck } from "lucide-react";

export default function CommandCenterPage() {
  const [jobText, setJobText] = useState(JSON.stringify(defaultJob, null, 2));
  const [validation, setValidation] = useState<string[]>([]);
  const [triggerStatus, setTriggerStatus] = useState<string>("");

  const parsed = useMemo(() => {
    try {
      return JSON.parse(jobText);
    } catch {
      return null;
    }
  }, [jobText]);

  async function validate() {
    const response = await fetch("/api/jobs/validate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: jobText
    });
    const data = await response.json();
    setValidation(data.errors || []);
  }

  async function trigger() {
    setTriggerStatus("dispatching...");
    const response = await fetch("/api/jobs/trigger", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: jobText
    });
    const data = await response.json();
    setTriggerStatus(data.status || "failed");
  }

  return (
    <section className="grid gap-4">
      <div className="rounded-xl border border-slate-300 bg-white p-4">
        <h2 className="mb-2 text-lg font-semibold">JSON Job Config</h2>
        <textarea
          className="h-[420px] w-full rounded-lg border border-slate-300 p-3 font-mono text-sm"
          value={jobText}
          onChange={(e) => setJobText(e.target.value)}
          spellCheck={false}
        />
        <div className="mt-3 flex gap-2">
          <button
            type="button"
            onClick={validate}
            className="inline-flex items-center gap-2 rounded-lg bg-slate-800 px-3 py-2 text-sm text-white"
          >
            <ShieldCheck size={16} /> Validate Schema
          </button>
          <button
            type="button"
            onClick={trigger}
            className="inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-3 py-2 text-sm text-white"
          >
            <Play size={16} /> Trigger Pipeline
          </button>
        </div>
      </div>

      <div className="rounded-xl border border-slate-300 bg-white p-4">
        <h3 className="font-medium">Validation</h3>
        {validation.length === 0 ? (
          <p className="text-sm text-slate-600">No validation errors.</p>
        ) : (
          <ul className="list-disc pl-5 text-sm text-red-700">
            {validation.map((err) => (
              <li key={err}>{err}</li>
            ))}
          </ul>
        )}
        <p className="mt-3 text-sm text-slate-700">Pipeline trigger status: {triggerStatus || "idle"}</p>
        <p className="text-xs text-slate-500">Current job: {parsed?.job_id || "invalid JSON"}</p>
      </div>
    </section>
  );
}
