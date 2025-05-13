"use client";

import { AnimatePresence, motion } from "framer-motion";
//import { useRouter } from "next/navigation";
import { useState } from "react";
import { FiZap } from "react-icons/fi";

export default function CreditBlock() {
  const [showCreditPulse] = useState(false);
  //const router = useRouter();
  const credits = 10;

  const coinAnimation = {
    pulse: {
      scale: [1, 1.15, 1],
      rotate: [0, 5, -5, 0],
      color: ["#FFD700", "#FFC107", "#FFEB3B", "#FFC107", "#FFD700"],
      filter: [
        "drop-shadow(0 0 0px #FFD700)",
        "drop-shadow(0 0 3px #FFC107)",
        "drop-shadow(0 0 5px #FFD700)",
        "drop-shadow(0 0 3px #FFC107)",
        "drop-shadow(0 0 0px #FFD700)",
      ],
      transition: { duration: 1.5, repeat: 0 },
    },
  };

  /*
  useEffect(() => {
    // Add pulsing effect to credits every 10 seconds
    const interval = setInterval(() => {
      setShowCreditPulse(true);
      setTimeout(() => setShowCreditPulse(false), 1500);
    }, 10000);

    return () => clearInterval(interval);
  }, []);

  // Initial pulse on mount
  useEffect(() => {
    const initialTimeout = setTimeout(() => {
      setShowCreditPulse(true);
      setTimeout(() => setShowCreditPulse(false), 1500);
    }, 1000);

    return () => clearTimeout(initialTimeout);
  }, []);
  */

  return (
    <motion.div
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      className="relative flex items-center bg-base-200 px-3 py-2 rounded-full cursor-pointer hover:bg-base-300 transition-colors overflow-hidden"
      animate={
        showCreditPulse
          ? {
              boxShadow: [
                "0 0 0 rgba(0,0,0,0)",
                "0 0 0 rgba(0,0,0,0)",
                "0 0 8px rgba(255, 215, 0, 0.4)",
                "0 0 0 rgba(0,0,0,0)",
              ],
            }
          : {}
      }
      transition={{ duration: 1.5 }}
    >
      {showCreditPulse && (
        <motion.div
          className="absolute inset-0 bg-gradient-to-r from-transparent via-amber-200 to-transparent opacity-20"
          initial={{ x: "-100%" }}
          animate={{ x: "100%" }}
          transition={{ duration: 1, ease: "easeInOut" }}
        />
      )}

      <AnimatePresence>
        <motion.div
          animate={showCreditPulse ? "pulse" : "idle"}
          variants={coinAnimation}
          className="mr-2 text-secondary-content relative z-10"
        >
          <FiZap />
        </motion.div>
      </AnimatePresence>
      <span className="font-semibold text-sm relative z-10">
        {credits.toLocaleString()} credits
      </span>
    </motion.div>
  );
}
