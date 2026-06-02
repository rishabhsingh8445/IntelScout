"use client";

import { useRef, useState, ReactNode } from "react";
import { motion } from "framer-motion";

interface AnimatedCardProps {
  children: ReactNode;
  className?: string;
  glowColor?: string;
  delay?: number;
}

export default function AnimatedCard({ 
  children, 
  className = "", 
  glowColor = "99, 102, 241",
  delay = 0 
}: AnimatedCardProps) {
  const cardRef = useRef<HTMLDivElement>(null);
  const [rotateX, setRotateX] = useState(0);
  const [rotateY, setRotateY] = useState(0);
  const [glowPos, setGlowPos] = useState({ x: 50, y: 50 });

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    const card = cardRef.current;
    if (!card) return;
    
    const rect = card.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;

    const rotX = ((y - centerY) / centerY) * -10;
    const rotY = ((x - centerX) / centerX) * 10;

    setRotateX(rotX);
    setRotateY(rotY);
    setGlowPos({ 
      x: (x / rect.width) * 100, 
      y: (y / rect.height) * 100 
    });
  };

  const handleMouseLeave = () => {
    setRotateX(0);
    setRotateY(0);
    setGlowPos({ x: 50, y: 50 });
  };

  return (
    <motion.div
      ref={cardRef}
      initial={{ opacity: 0, y: 40, rotateX: 15 }}
      whileInView={{ opacity: 1, y: 0, rotateX: 0 }}
      viewport={{ once: true, margin: "-50px" }}
      transition={{ 
        duration: 0.7, 
        delay, 
        ease: [0.23, 1, 0.32, 1] 
      }}
      whileHover={{ scale: 1.02 }}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      className={`relative rounded-2xl overflow-hidden card-3d ${className}`}
      style={{
        transform: `perspective(1200px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`,
        transformStyle: "preserve-3d",
      }}
    >
      {/* Glow follow */}
      <div
        className="absolute inset-0 opacity-0 hover:opacity-100 transition-opacity duration-300 pointer-events-none z-10"
        style={{
          background: `radial-gradient(circle at ${glowPos.x}% ${glowPos.y}%, rgba(${glowColor}, 0.15) 0%, transparent 60%)`,
        }}
      />
      
      {/* Border glow */}
      <div 
        className="absolute inset-0 rounded-2xl pointer-events-none z-10 opacity-0 hover:opacity-100 transition-opacity duration-500"
        style={{
          boxShadow: `inset 0 0 0 1px rgba(${glowColor}, 0.2), 0 0 30px rgba(${glowColor}, 0.1)`,
        }}
      />

      {/* Shimmer */}
      <div className="absolute inset-0 rounded-2xl pointer-events-none z-10 shimmer-effect" />

      {/* Content */}
      <div className="relative z-20">{children}</div>
    </motion.div>
  );
}
