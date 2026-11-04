"use client";

import { useMemo, useState } from "react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  Legend,
} from "recharts";
import type { Param, Point } from "@/lib/api";
import { LEVELS, THRESHOLDS } from "@/lib/aqi";

type Series = { name: string; points: Point[]; dashed?: boolean };

type Props = {
  byParam: Partial<Record<Param, Series[]>>;
};

const tick = { fill: "#111", fontSize: 15, fontFamily: "var(--font-hand)" };

function merge(series: Series[]) {
  const rows = new Map<string, Record<string, number | string>>();
  for (const s of series) {
    for (const p of s.points) {
      const row = rows.get(p.ts) ?? { ts: p.ts };
      row[s.name] = p.value;
      rows.set(p.ts, row);
    }
  }
  return [...rows.values()].sort((a, b) => String(a.ts).localeCompare(String(b.ts)));
}

function label(ts: string) {
  const d = new Date(ts);
  return d.toLocaleDateString("en-GB", { weekday: "short" }) + " " + String(d.getHours()).padStart(2, "0") + ":00";
}

export default function HistoryChart({ byParam }: Props) {
  const params = Object.keys(byParam) as Param[];
  const [param, setParam] = useState<Param>(params[0] ?? "PM2.5");
  const series = byParam[param] ?? [];
  const data = useMemo(() => merge(series), [series]);
  const limits = THRESHOLDS[param];

  return (
    <div>
      {params.length > 1 && (
        <div className="tabs">
          {params.map((p) => (
            <button key={p} className={p === param ? "on" : ""} onClick={() => setParam(p)}>
              {p}
            </button>
          ))}
        </div>
      )}

      {data.length === 0 ? (
        <p className="muted">no {param} measurements here</p>
      ) : (
        <div className="chart">
          <ResponsiveContainer>
            <LineChart data={data} margin={{ top: 10, right: 16, bottom: 0, left: -10 }}>
              <CartesianGrid stroke="#ccc" strokeDasharray="4 6" vertical={false} />
              <XAxis dataKey="ts" tickFormatter={label} tick={tick} minTickGap={50} stroke="#111" strokeWidth={2} />
              <YAxis tick={tick} stroke="#111" strokeWidth={2} />
              {limits.slice(1, 3).map((v, i) => (
                <ReferenceLine
                  key={v}
                  y={v}
                  stroke="#111"
                  strokeDasharray="2 5"
                  label={{ value: LEVELS[i + 1] + " ends", position: "insideTopRight", fill: "#555", fontSize: 14 }}
                />
              ))}
              <Tooltip
                labelFormatter={(v) => label(String(v))}
                contentStyle={{ border: "3px solid #111", borderRadius: 6, fontFamily: "var(--font-hand)" }}
                formatter={(v) => `${v} µg/m³`}
              />
              {series.length > 1 && <Legend wrapperStyle={{ fontFamily: "var(--font-hand)" }} />}
              {series.map((s) => (
                <Line
                  key={s.name}
                  type="monotone"
                  dataKey={s.name}
                  stroke="#111"
                  strokeWidth={s.dashed ? 2.5 : 3.5}
                  strokeDasharray={s.dashed ? "8 5" : undefined}
                  dot={false}
                  connectNulls
                  isAnimationActive={false}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
