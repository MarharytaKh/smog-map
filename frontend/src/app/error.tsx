"use client";

export default function Error({ reset }: { error: Error; reset: () => void }) {
  return (
    <div className="box error" style={{ maxWidth: 520, margin: "40px auto", textAlign: "center" }}>
      <h1>oops</h1>
      <p>couldn&apos;t reach the API. is the backend running?</p>
      <button onClick={reset}>try again</button>
    </div>
  );
}
