import { NextRequest, NextResponse } from "next/server";
import { validateJobConfig } from "@/lib/schema";
import { getRedisClient } from "@/lib/redis";

export async function POST(request: NextRequest) {
  const payload = (await request.json()) as Record<string, unknown>;
  const valid = validateJobConfig(payload);

  if (!valid) {
    return NextResponse.json(
      { status: "validation_failed", errors: validateJobConfig.errors },
      { status: 400 }
    );
  }

  const jobId = String(payload.job_id ?? "");

  const redis = getRedisClient();
  await redis.xadd(
    "pipeline:events",
    "*",
    "type",
    "job.trigger",
    "job_id",
    jobId,
    "job_config",
    JSON.stringify(payload)
  );

  return NextResponse.json({ status: "queued", job_id: jobId });
}
