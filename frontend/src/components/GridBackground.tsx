"use client";

export default function GridBackground() {
  return (
    <div className="fixed inset-0 z-0 pointer-events-none overflow-hidden opacity-[0.07]">
      {/* Perspective grid */}
      <div
        className="absolute inset-0"
        style={{
          perspective: "500px",
          perspectiveOrigin: "50% 30%",
        }}
      >
        <div
          className="absolute left-[-20%] right-[-20%] bottom-[-20%] h-[80vh]"
          style={{
            transform: "rotateX(55deg)",
            transformOrigin: "center bottom",
            backgroundImage: `
              linear-gradient(rgba(99, 102, 241, 0.5) 1px, transparent 1px),
              linear-gradient(90deg, rgba(99, 102, 241, 0.5) 1px, transparent 1px)
            `,
            backgroundSize: "60px 60px",
            maskImage: "linear-gradient(to top, white 30%, transparent 90%)",
            WebkitMaskImage: "linear-gradient(to top, white 30%, transparent 90%)",
          }}
        >
          {/* Scan line */}
          <div className="scan-line" />
        </div>
      </div>
    </div>
  );
}
