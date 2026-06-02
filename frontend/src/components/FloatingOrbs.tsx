"use client";

export default function FloatingOrbs() {
  return (
    <div className="fixed inset-0 z-0 pointer-events-none overflow-hidden">
      {/* Large indigo orb - top left */}
      <div
        className="absolute w-[500px] h-[500px] rounded-full"
        style={{
          top: "-5%",
          left: "-5%",
          background: "radial-gradient(circle, rgba(99, 102, 241, 0.15) 0%, transparent 70%)",
          animation: "float 8s ease-in-out infinite",
        }}
      />
      
      {/* Purple orb - right */}
      <div
        className="absolute w-[600px] h-[600px] rounded-full"
        style={{
          top: "15%",
          right: "-10%",
          background: "radial-gradient(circle, rgba(139, 92, 246, 0.12) 0%, transparent 70%)",
          animation: "float-slow 10s ease-in-out infinite",
          animationDelay: "-3s",
        }}
      />

      {/* Cyan orb - bottom left */}
      <div
        className="absolute w-[400px] h-[400px] rounded-full"
        style={{
          bottom: "-10%",
          left: "15%",
          background: "radial-gradient(circle, rgba(34, 211, 238, 0.1) 0%, transparent 70%)",
          animation: "float 12s ease-in-out infinite",
          animationDelay: "-5s",
        }}
      />

      {/* Pink orb - center */}
      <div
        className="absolute w-[350px] h-[350px] rounded-full"
        style={{
          top: "50%",
          left: "40%",
          background: "radial-gradient(circle, rgba(236, 72, 153, 0.08) 0%, transparent 70%)",
          animation: "float-slow 14s ease-in-out infinite",
          animationDelay: "-7s",
        }}
      />
    </div>
  );
}
