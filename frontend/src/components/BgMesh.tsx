"use client";

export function BgMesh() {
  return (
    <div
      className="animate-mesh pointer-events-none fixed inset-0 z-0"
      style={{
        background:
          "radial-gradient(ellipse 80% 50% at 20% -10%, rgba(0,107,182,0.25) 0%, transparent 55%), " +
          "radial-gradient(ellipse 60% 40% at 85% 110%, rgba(245,132,38,0.12) 0%, transparent 50%), " +
          "radial-gradient(ellipse 50% 30% at 50% 50%, rgba(212,175,55,0.06) 0%, transparent 60%)",
      }}
    >
      <div
        className="absolute inset-0"
        style={{
          background:
            "repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(255,255,255,0.015) 2px, rgba(255,255,255,0.015) 4px)",
        }}
      />
    </div>
  );
}
