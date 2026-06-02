"use client";

import { motion } from "framer-motion";

interface AnimatedTextProps {
  text: string;
  className?: string;
  delay?: number;
}

export default function AnimatedText({ text, className = "", delay = 0 }: AnimatedTextProps) {
  const letters = Array.from(text);

  const container = {
    hidden: { opacity: 0 },
    visible: (i = 1) => ({
      opacity: 1,
      transition: { staggerChildren: 0.03, delayChildren: delay * 0.1 },
    }),
  };

  const child = {
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        type: "spring" as any,
        damping: 12,
        stiffness: 100,
      },
    },
    hidden: {
      opacity: 0,
      y: 20,
    },
  };

  return (
    <motion.h1
      style={{ display: "flex", flexWrap: "wrap" }}
      className={className}
      variants={container}
      initial="hidden"
      animate="visible"
    >
      {letters.map((word, index) => (
        <motion.span variants={child} key={index}>
          {word === " " ? "\u00A0" : word}
        </motion.span>
      ))}
    </motion.h1>
  );
}
