import type { components } from "./schema";

type S = components["schemas"];

export type Station = S["StationOut"];
export type NearStation = S["NearStation"];
export type Point = S["Point"];
export type CityRank = S["CityRank"];
export type CityDetail = S["CityDetail"];
export type Compare = S["Compare"];
export type SubscriptionIn = S["SubscriptionIn"];
export type SubscriptionOut = S["SubscriptionOut"];

export type Param = "PM2.5" | "PM10" | "NO2";
export const PARAMS: Param[] = ["PM2.5", "PM10", "NO2"];

export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

async function get<T>(path: string, params?: Record<string, string | number | undefined>, revalidate = 600): Promise<T> {
  const url = new URL(path, API_URL);
  if (params) {
    for (const [k, v] of Object.entries(params)) {
      if (v !== undefined) url.searchParams.set(k, String(v));
    }
  }
  const res = await fetch(url, { next: { revalidate } });
  if (!res.ok) throw new ApiError(res.status, `${res.status} ${url.pathname}`);
  return res.json() as Promise<T>;
}

export const api = {
  stations: () => get<Station[]>("/stations"),
  near: (lat: number, lon: number, limit = 5) => get<NearStation[]>("/stations/near", { lat, lon, limit }, 0),
  cities: () => get<string[]>("/cities", undefined, 3600),
  ranking: (order: "worst" | "best", param: Param = "PM2.5", limit = 8) =>
    get<CityRank[]>("/cities/ranking", { order, param, limit }),
  city: (name: string, days = 7) => get<CityDetail>(`/cities/${encodeURIComponent(name)}`, { days }),
  compare: (a: string, b: string, param: Param, days = 7) => get<Compare>("/compare", { a, b, param, days }),

  async subscribe(body: SubscriptionIn): Promise<SubscriptionOut> {
    const res = await fetch(`${API_URL}/subscriptions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new ApiError(res.status, "could not subscribe");
    return res.json();
  },

  async unsubscribe(token: string) {
    const res = await fetch(`${API_URL}/subscriptions/${encodeURIComponent(token)}`, { method: "DELETE" });
    if (!res.ok && res.status !== 404) throw new ApiError(res.status, "could not unsubscribe");
    return res.status === 204;
  },
};
