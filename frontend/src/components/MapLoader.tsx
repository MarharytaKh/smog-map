"use client";

import dynamic from "next/dynamic";

const MapLoader = dynamic(() => import("./StationMap"), {
  ssr: false,
  loading: () => <p style={{ padding: 20 }}>drawing the map...</p>,
});

export default MapLoader;
