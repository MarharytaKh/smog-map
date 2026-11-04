"use client";

import "leaflet/dist/leaflet.css";
import Link from "next/link";
import { CircleMarker, MapContainer, Popup, TileLayer, useMapEvents } from "react-leaflet";
import type { Station } from "@/lib/api";
import { fill, fmt } from "@/lib/aqi";

type Props = {
  stations: Station[];
  center?: [number, number];
  zoom?: number;
  picked?: [number, number] | null;
  onPick?: (lat: number, lon: number) => void;
};

function ClickCatcher({ onPick }: { onPick: (lat: number, lon: number) => void }) {
  useMapEvents({
    click(e) {
      onPick(e.latlng.lat, e.latlng.lng);
    },
  });
  return null;
}

export default function StationMap({ stations, center = [52.0, 19.2], zoom = 6, picked, onPick }: Props) {
  return (
    <MapContainer center={center} zoom={zoom} scrollWheelZoom={true} attributionControl={true}>
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {onPick && <ClickCatcher onPick={onPick} />}

      {stations.map((s) => (
        <CircleMarker
          key={s.id}
          center={[s.lat, s.lon]}
          radius={s.index == null ? 5 : 9}
          pathOptions={{
            color: "#111",
            weight: s.index == null ? 2 : 3,
            fillColor: s.index == null ? "#fff" : fill(s.index),
            fillOpacity: 1,
            dashArray: s.index == null ? "3 3" : undefined,
          }}
        >
          {!onPick && (
            <Popup>
              <div>
                <b>{s.name}</b>
                <div>
                  PM2.5 {fmt(s.values["PM2.5"])} · PM10 {fmt(s.values["PM10"])} · NO₂ {fmt(s.values["NO2"])}
                </div>
                <div>{s.index_label ?? "no fresh data"}</div>
                {s.city && <Link href={`/city/${encodeURIComponent(s.city)}`}>{s.city} →</Link>}
              </div>
            </Popup>
          )}
        </CircleMarker>
      ))}

      {picked && (
        <CircleMarker
          center={picked}
          radius={14}
          pathOptions={{ color: "#111", weight: 4, fillOpacity: 0, dashArray: "6 4" }}
        />
      )}
    </MapContainer>
  );
}
