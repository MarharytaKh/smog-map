import Link from "next/link";
import { notFound } from "next/navigation";
import HistoryChart from "@/components/HistoryChart";
import MapLoader from "@/components/MapLoader";
import { ApiError, api, PARAMS, type CityDetail, type Param } from "@/lib/api";
import { ago, fill, fmt, inkOn } from "@/lib/aqi";

export const revalidate = 600;

type Props = { params: Promise<{ name: string }> };

export async function generateMetadata({ params }: Props) {
  const { name } = await params;
  return { title: `${decodeURIComponent(name)} · Smog Map` };
}

export default async function CityPage({ params }: Props) {
  const { name } = await params;
  let city: CityDetail;
  try {
    city = await api.city(decodeURIComponent(name));
  } catch (e) {
    if (e instanceof ApiError && e.status === 404) notFound();
    throw e;
  }

  const avg = (p: Param) => {
    const vals = city.stations.map((s) => s.values[p]).filter((v): v is number => v != null);
    return vals.length ? vals.reduce((a, b) => a + b, 0) / vals.length : null;
  };

  const worstIndex = Math.max(-1, ...city.stations.map((s) => s.index ?? -1));
  const lat = city.stations.reduce((a, s) => a + s.lat, 0) / city.stations.length;
  const lon = city.stations.reduce((a, s) => a + s.lon, 0) / city.stations.length;

  const byParam = Object.fromEntries(
    PARAMS.map((p) => [p, [{ name: p, points: city.history[p] ?? [] }]]),
  );

  return (
    <div className="stack">
      <div>
        <Link href="/">← map</Link>
        <h1>{city.city}</h1>
        {worstIndex >= 0 && (
          <span className="pill" style={{ background: fill(worstIndex), color: inkOn(worstIndex) }}>
            air is {city.stations.find((s) => s.index === worstIndex)?.index_label} at the worst station
          </span>
        )}
      </div>

      <div className="stats">
        {PARAMS.map((p) => (
          <div key={p} className="box stat">
            <b>{fmt(avg(p))}</b>
            {p} <span className="muted">µg/m³</span>
          </div>
        ))}
      </div>

      <section className="box">
        <h2>last 7 days</h2>
        <HistoryChart byParam={byParam} />
      </section>

      <div className="grid">
        <section className="box">
          <h2>stations</h2>
          <table>
            <thead>
              <tr>
                <th>where</th>
                <th className="num">PM2.5</th>
                <th className="num">PM10</th>
                <th className="num">NO₂</th>
                <th>updated</th>
              </tr>
            </thead>
            <tbody>
              {city.stations.map((s) => (
                <tr key={s.id}>
                  <td>
                    <i className="dot" style={{ background: fill(s.index), verticalAlign: "middle", marginRight: 6 }} />
                    {s.name.replace(`${city.city}, `, "")}
                  </td>
                  <td className="num">{fmt(s.values["PM2.5"])}</td>
                  <td className="num">{fmt(s.values["PM10"])}</td>
                  <td className="num">{fmt(s.values["NO2"])}</td>
                  <td className="muted">{ago(s.updated_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
        <div className="box map" style={{ height: 320 }}>
          <MapLoader stations={city.stations} center={[lat, lon]} zoom={11} />
        </div>
      </div>

      <p>
        <Link className="btn" href={`/compare?a=${encodeURIComponent(city.city)}`}>
          compare with another city
        </Link>
      </p>
    </div>
  );
}
