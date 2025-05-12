"use client";

import { useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { FiCheckCircle, FiAlertCircle } from "react-icons/fi";
import confetti from "canvas-confetti";
import { useQuery } from "@tanstack/react-query";

import { tgAgentsGet } from "@viralink-ai/sdk";

import { BackButton } from "@/components/BackButton";
import PageTransition from "@/components/PageTransition";
import { useApi } from "@/hooks/useApi";
import { getBotUsername, getChannelUsername } from "@/components/agents/utils";

export default function Success() {
  const { id: agentId } = useParams<{ id: string }>();
  const router = useRouter();

  const api = useApi();

  const { data: agent, isPending } = useQuery({
    queryKey: ["/agents", agentId],
    queryFn: async () => {
      const { data } = await tgAgentsGet({
        path: {
          agent_id: agentId,
        },
        throwOnError: true,
      });
      return data;
    },
    enabled: !!api,
  });
  useEffect(() => {
    if (agent?.status != "active") return;
    setTimeout(() => {
      confetti({
        particleCount: 100,
        spread: 70,
        origin: { y: 0.6 },
      });
    }, 500);
  }, [agent]);

  return (
    <PageTransition>
      <BackButton />
      <div className="container mx-auto max-w-md p-4 text-center">
        {isPending ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="my-16"
          >
            <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-6"></div>
            <h2 className="text-xl font-bold mb-2">Connecting Your Bot</h2>
            <p className="opacity-70">
              Please wait while we set everything up...
            </p>
          </motion.div>
        ) : agent?.status == "active" ? (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="my-12"
          >
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{
                type: "spring",
                stiffness: 260,
                damping: 20,
                delay: 0.2,
              }}
              className="w-24 h-24 bg-success text-success-content rounded-full flex items-center justify-center text-4xl mx-auto mb-6"
            >
              <FiCheckCircle />
            </motion.div>

            <h1 className="text-2xl font-bold mb-2">Connection Successful!</h1>
            <p className="opacity-70 mb-8">
              {getChannelUsername(agent)} is now connected with{" "}
              {getBotUsername(agent)}
            </p>

            <div className="card bg-base-200 p-4 text-left mb-8">
              <h3 className="font-semibold mb-2">What happens next:</h3>
              <ul className="space-y-2">
                <motion.li
                  initial={{ opacity: 0, x: -5 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.4 }}
                  className="flex items-start"
                >
                  <div className="w-5 h-5 bg-primary rounded-full flex items-center justify-center text-primary-content text-xs mt-0.5 mr-2">
                    1
                  </div>
                  <div>
                    Your bot is now analyzing your channel to understand your
                    content
                  </div>
                </motion.li>
                <motion.li
                  initial={{ opacity: 0, x: -5 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.6 }}
                  className="flex items-start"
                >
                  <div className="w-5 h-5 bg-primary rounded-full flex items-center justify-center text-primary-content text-xs">
                    2
                  </div>
                  <div>
                    The bot will prepare draft content based on your preferences
                  </div>
                </motion.li>
                <motion.li
                  initial={{ opacity: 0, x: -5 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.8 }}
                  className="flex items-center bg-red-200"
                >
                  <div className="flex flex-row items-start">
                    <div className="bg-primary w-7 h-7 text-center"></div>
                    <div className="bg-blue-200">
                      You'll receive notifications when content is ready for
                      review
                    </div>
                  </div>
                </motion.li>
              </ul>
            </div>

            <motion.button
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.98 }}
              className="btn btn-primary btn-block"
              onClick={() => router.push("/")}
            >
              Return to Channels
            </motion.button>
          </motion.div>
        ) : (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="my-16"
          >
            <div className="w-20 h-20 bg-error text-error-content rounded-full flex items-center justify-center text-3xl mx-auto mb-6">
              <FiAlertCircle />
            </div>
            <h2 className="text-xl font-bold mb-2">Connection Failed</h2>
            <p className="opacity-70 mb-6">
              {"Something went wrong. Please try again."}
            </p>

            <button
              className="btn btn-primary"
              onClick={() => router.push("/add-channel")}
            >
              Try Again
            </button>
          </motion.div>
        )}
      </div>
    </PageTransition>
  );
}
