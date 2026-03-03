import { NextRequest, NextResponse } from "next/server";
import { validateJobConfig } from "@/lib/schema";

export async function POST(request: NextRequest) {
  const payload = await request.json();
  const ok = validateJobConfig(payload);

  return NextResponse.json({
    valid: ok,
    errors: validateJobConfig.errors?.map((e) => `${e.instancePath || "/"} ${e.message}`) || []
  });
}
