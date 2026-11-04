import Link from "next/link";
import type { CityRank } from "@/lib/api";
import { fill } from "@/lib/aqi";

export default function RankList({ rows }: { rows: CityRank[] }) {
  if (!rows.length) return <p className="muted">nothing yet, waiting for the first sync</p>;

  return (
    <ol className="rank">
      {rows.map((r, i) => (
        <li key={r.city}>
          <span className="n">{i + 1}.</span>
          <i className="dot" style={{ background: fill(r.index) }} />
          <Link href={`/city/${encodeURIComponent(r.city)}`}>{r.city}</Link>
          <span>{r.value}</span>
        </li>
      ))}
    </ol>
  );
}
