import Redis from "ioredis";

let client: Redis | null = null;

export function getRedisClient(): Redis {
  if (!client) {
    client = new Redis(process.env.VALKEY_URL || "redis://valkey:6379/0");
  }
  return client;
}
