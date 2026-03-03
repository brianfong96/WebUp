import { NextRequest, NextResponse } from "next/server";
import { getRedisClient } from "@/lib/redis";

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const jobId = searchParams.get("job_id") || "";
  const redis = getRedisClient();

  const stream = await redis.xrevrange("logs:stream", "+", "-", "COUNT", 50);
  const logs = stream
    .map(([, entries]) => {
      const mapped = Object.fromEntries(
        entries.reduce((acc: string[][], value: string, idx: number, arr: string[]) => {
          if (idx % 2 === 0 && arr[idx + 1] !== undefined) {
            acc.push([value, arr[idx + 1]]);
          }
          return acc;
        }, [])
      ) as Record<string, string>;
      return {
        timestamp: mapped.timestamp,
        severity: mapped.severity,
        service_name: mapped.service_name,
        trace_id: mapped.trace_id,
        job_id: mapped.job_id,
        message: mapped.message
      };
    })
    .filter((item) => !jobId || item.job_id === jobId);

  return NextResponse.json({ logs });
}
