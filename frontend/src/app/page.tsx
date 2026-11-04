import Legend from "@/components/Legend";
import MapLoader from "@/components/MapLoader";
import RankList from "@/components/RankList";
import { api, type Station, type CityRank } from "@/lib/api";
import { ago } from "@/lib/aqi";

export const revalidate = 600;

async function load() {
  try {
    const [stations, worst, best] = await Promise.all([
      api.stations(),
      api.ranking("worst"),
      api.ranking("best"),
    ]);
    return { stations, worst, best, error: null };
  } catch (e) {
    console.error(e);
    return { stations: [] as Station[], worst: [] as CityRank[], best: [] as CityRank[], error: "API is not responding" };
  }
}

export default async function Home() {
  const { stations, worst, best, error } = await load();
  const withData = stations.filter((s) => s.index != null);
  const latest = withData.map((s) => s.updated_at).filter(Boolean).sort().at(-1) ?? null;

  return (
    <div className="stack">
      <div>
        <h1>
          how&apos;s the air in <span className="scribble">Poland</span>?
        </h1>
        <p className="muted">
          {error
            ? error
            : `${withData.length} of ${stations.length} stations reporting · last reading ${ago(latest)}`}
        </p>
      </div>

      <div className="grid">
        <div className="stack">
          <div className="box map">
            <MapLoader stations={stations} />
          </div>
          <Legend />
        </div>

        <div className="stack">
          <section className="box">
            <h2>worst right now</h2>
            <RankList rows={worst} />
          </section>
          <section className="box alt">
            <h2>cleanest</h2>
            <RankList rows={best} />
          </section>
          <p className="muted" style={{ fontSize: 16 }}>
            numbers are PM2.5 in µg/m³, averaged over the city&apos;s stations
          </p>
        </div>
      </div>
    </div>
  );
}
