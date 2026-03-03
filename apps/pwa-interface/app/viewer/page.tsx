"use client";

import { useEffect, useMemo, useState } from "react";

type LogRow = {
  timestamp: string;
  severity: string;
  service_name: string;
  trace_id: string;
  message: string;
};

export default function ViewerPage() {
  const [jobId, setJobId] = useState("finance-hourly");
  const [logs, setLogs] = useState<LogRow[]>([]);

  useEffect(() => {
    const poll = setInterval(async () => {
      const res = await fetch(`/api/observability/logs?job_id=${encodeURIComponent(jobId)}`);
      const data = await res.json();
      setLogs(data.logs || []);
    }, 2500);
    return () => clearInterval(poll);
  }, [jobId]);

  const asJson = useMemo(() => JSON.stringify(logs.slice(0, 5), null, 2), [logs]);

  return (
    <section className="grid gap-4 lg:grid-cols-2">
      <div className="rounded-xl border border-slate-300 bg-white p-4">
        <h2 className="text-lg font-semibold">Log Explorer</h2>
        <input
          className="my-3 w-full rounded-lg border border-slate-300 px-3 py-2"
          value={jobId}
          onChange={(e) => setJobId(e.target.value)}
          placeholder="Filter by job_id"
        />
        <div className="max-h-[420px] overflow-auto rounded-lg border border-slate-200">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50">
              <tr>
                <th className="p-2">Time</th>
                <th className="p-2">Severity</th>
                <th className="p-2">Service</th>
                <th className="p-2">Message</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log, i) => (
                <tr key={`${log.timestamp}-${i}`} className="border-t border-slate-100">
                  <td className="p-2">{log.timestamp}</td>
                  <td className="p-2">{log.severity}</td>
                  <td className="p-2">{log.service_name}</td>
                  <td className="p-2">{log.message}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="grid gap-4">
        <div className="rounded-xl border border-slate-300 bg-white p-4">
          <h3 className="font-semibold">Data Inspector</h3>
          <p className="mb-2 text-sm text-slate-600">Tabular + JSON tree-ready payload preview</p>
          <pre className="overflow-auto rounded-lg bg-slate-900 p-3 text-xs text-slate-100">{asJson}</pre>
        </div>
        <div className="rounded-xl border border-slate-300 bg-white p-4">
          <h3 className="font-semibold">Database Browser</h3>
          <p className="text-sm text-slate-600">Use this panel for PostgreSQL/TimescaleDB query results (API hook scaffolded).</p>
        </div>
      </div>
    </section>
  );
}
