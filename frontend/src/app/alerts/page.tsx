"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Suspense } from "react";
import MapLoader from "@/components/MapLoader";
import { api, type Station, type SubscriptionOut } from "@/lib/api";
import { fmt } from "@/lib/aqi";

function AlertsInner() {
  const search = useSearchParams();
  const unsubToken = search.get("unsubscribe");

  const [stations, setStations] = useState<Station[]>([]);
  const [picked, setPicked] = useState<[number, number] | null>(null);
  const [email, setEmail] = useState("");
  const [radius, setRadius] = useState(5);
  const [threshold, setThreshold] = useState(35);
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<SubscriptionOut | null>(null);
  const [msg, setMsg] = useState("");

  useEffect(() => {
    api.stations().then(setStations).catch(() => setMsg("map data is not available right now"));
  }, []);

  useEffect(() => {
    if (!unsubToken) return;
    api
      .unsubscribe(unsubToken)
      .then((ok) => setMsg(ok ? "done, you won't get any more emails" : "this link was already used"))
      .catch(() => setMsg("something went wrong, try again later"));
  }, [unsubToken]);

  function locate() {
    if (!navigator.geolocation) {
      setMsg("your browser can't share location, click on the map instead");
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => setPicked([pos.coords.latitude, pos.coords.longitude]),
      () => setMsg("couldn't get your location, click on the map instead"),
    );
  }

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!picked) {
      setMsg("pick a spot on the map first");
      return;
    }
    setBusy(true);
    setMsg("");
    try {
      const out = await api.subscribe({ email, lat: picked[0], lon: picked[1], radius_km: radius, threshold });
      console.log("subscribed", out);
      setResult(out);
    } catch {
      setMsg("couldn't save that, check the email and try again");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="stack">
      <div>
        <h1>tell me when it gets bad</h1>
        <p className="muted">
          pick your area and we&apos;ll email you when PM2.5 nearby goes over your limit. max one email every 6 hours.
        </p>
      </div>

      {msg && <p className="box error">{msg}</p>}

      <div className="grid">
        <div className="box map" style={{ height: 460 }}>
          <MapLoader
            stations={stations}
            picked={picked}
            onPick={(lat, lon) => setPicked([lat, lon])}
          />
        </div>

        {result ? (
          <section className="box alt">
            <h2>you&apos;re in ✓</h2>
            <p>we&apos;ll watch these stations for you:</p>
            <ul>
              {(result.nearest_stations ?? []).map((s) => (
                <li key={s.id}>
                  {s.name} <span className="muted">({s.distance_km} km, now {fmt(s.values["PM2.5"])})</span>
                </li>
              ))}
            </ul>
            {(result.nearest_stations ?? []).length === 0 && (
              <p className="muted">no stations within {result.radius_km} km, try a bigger radius</p>
            )}
            <button className="ghost" onClick={() => setResult(null)}>
              add another
            </button>
          </section>
        ) : (
          <form className="box stack" onSubmit={submit}>
            <p style={{ margin: 0 }}>
              {picked ? `spot: ${picked[0].toFixed(3)}, ${picked[1].toFixed(3)}` : "click on the map to pick a spot"}
            </p>
            <button type="button" className="ghost" onClick={locate}>
              use my location
            </button>
            <label>
              email
              <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
            </label>
            <label>
              radius: {radius} km
              <input type="range" min={1} max={30} value={radius} onChange={(e) => setRadius(+e.target.value)} />
            </label>
            <label>
              alert above {threshold} µg/m³
              <input
                type="range"
                min={10}
                max={150}
                step={5}
                value={threshold}
                onChange={(e) => setThreshold(+e.target.value)}
              />
            </label>
            <button type="submit" disabled={busy}>
              {busy ? "saving..." : "subscribe"}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}

export default function AlertsPage() {
  return (
    <Suspense>
      <AlertsInner />
    </Suspense>
  );
}
