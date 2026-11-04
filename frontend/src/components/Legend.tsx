import { FILLS, LEVELS } from "@/lib/aqi";

export default function Legend() {
  return (
    <div className="legend">
      {LEVELS.map((l, i) => (
        <span key={l}>
          <i className="dot" style={{ background: FILLS[i] }} />
          {l}
        </span>
      ))}
      <span>
        <i className="dot" style={{ borderStyle: "dashed" }} />
        no data
      </span>
    </div>
  );
}
