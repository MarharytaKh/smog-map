import type { Param } from "./api";

export const LEVELS = ["very good", "good", "moderate", "sufficient", "bad", "very bad"];

export const FILLS = ["#ffffff", "#e4e4e4", "#b8b8b8", "#808080", "#4a4a4a", "#111111"];

export const THRESHOLDS: Record<Param, number[]> = {
  "PM2.5": [13, 35, 55, 75, 110],
  PM10: [20, 50, 80, 110, 150],
  NO2: [40, 90, 120, 230, 400],
};

export function fill(index: number | null | undefined) {
  if (index == null) return "transparent";
  return FILLS[index];
}

export function inkOn(index: number | null | undefined) {
  return index != null && index >= 3 ? "#fff" : "#111";
}

export function fmt(v: number | null | undefined, digits = 0) {
  if (v == null) return "–";
  return v.toFixed(digits);
}

export function ago(iso: string | null) {
  if (!iso) return "no data";
  const mins = Math.round((Date.now() - new Date(iso).getTime()) / 60000);
  if (mins < 60) return `${mins} min ago`;
  const h = Math.round(mins / 60);
  return h === 1 ? "1 hour ago" : `${h} hours ago`;
}
