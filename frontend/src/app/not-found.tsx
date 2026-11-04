import Link from "next/link";

export default function NotFound() {
  return (
    <div className="box" style={{ maxWidth: 520, margin: "40px auto", textAlign: "center" }}>
      <h1>nothing here</h1>
      <p>no stations in that city, or the page doesn&apos;t exist</p>
      <Link className="btn" href="/">
        back to the map
      </Link>
    </div>
  );
}
