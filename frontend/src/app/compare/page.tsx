import HistoryChart from "@/components/HistoryChart";
import { api, PARAMS, type Compare, type Param } from "@/lib/api";
import { fmt } from "@/lib/aqi";

type Props = { searchParams: Promise<{ a?: string; b?: string; param?: string }> };

export const metadata = { title: "Compare · Smog Map" };

function mean(xs: number[]) {
  return xs.length ? xs.reduce((a, b) => a + b, 0) / xs.length : null;
}

export default async function ComparePage({ searchParams }: Props) {
  const sp = await searchParams;
  const cities = await api.cities().catch(() => [] as string[]);

  const a = sp.a ?? "Warszawa";
  const b = sp.b ?? "Kraków";
  const param: Param = PARAMS.includes(sp.param as Param) ? (sp.param as Param) : "PM2.5";

  let data: Compare | null = null;
  let error = "";
  if (a && b) {
    try {
      data = await api.compare(a, b, param);
    } catch {
      error = `could not load ${a} or ${b}`;
    }
  }

  const pa = data?.a.history[param] ?? [];
  const pb = data?.b.history[param] ?? [];
  const ma = mean(pa.map((p) => p.value));
  const mb = mean(pb.map((p) => p.value));

  return (
    <div className="stack">
      <h1>city vs city</h1>

      <form className="row box" method="get">
        <label>
          first
          <select name="a" defaultValue={a}>
            {cities.map((c) => (
              <option key={c}>{c}</option>
            ))}
          </select>
        </label>
        <label>
          second
          <select name="b" defaultValue={b}>
            {cities.map((c) => (
              <option key={c}>{c}</option>
            ))}
          </select>
        </label>
        <label>
          what
          <select name="param" defaultValue={param}>
            {PARAMS.map((p) => (
              <option key={p}>{p}</option>
            ))}
          </select>
        </label>
        <button type="submit">compare</button>
      </form>

      {error && <p className="box error">{error}</p>}

      {data && (
        <>
          <div className="stats" style={{ gridTemplateColumns: "1fr 1fr" }}>
            <div className="box stat">
              <b>{fmt(ma, 1)}</b>
              {data.a.city} <span className="muted">— solid line</span>
            </div>
            <div className="box alt stat">
              <b>{fmt(mb, 1)}</b>
              {data.b.city} <span className="muted">- - dashed</span>
            </div>
          </div>
          {ma != null && mb != null && ma !== mb && (
            <p style={{ fontSize: 24 }}>
              over the week {ma > mb ? data.a.city : data.b.city} had{" "}
              <b>{Math.round((Math.max(ma, mb) / Math.max(Math.min(ma, mb), 0.1) - 1) * 100)}%</b> more {param} on
              average
            </p>
          )}
          <section className="box">
            <HistoryChart
              byParam={{
                [param]: [
                  { name: data.a.city, points: pa },
                  { name: data.b.city, points: pb, dashed: true },
                ],
              }}
            />
          </section>
        </>
      )}
    </div>
  );
}
