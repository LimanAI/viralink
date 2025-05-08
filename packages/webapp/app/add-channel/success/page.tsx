"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { showMainButton } from "@/lib/telegram";
import PageTransition from "@/components/PageTransition";
import { motion } from "framer-motion";
import { FiCheckCircle, FiAlertCircle } from "react-icons/fi";
import confetti from "canvas-confetti";

const connectBotToChannel = (channelId, botId, contentDescription, persona) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const updatedChannel = channels.find(
        (channel) => channel.id === channelId
      );
      if (updatedChannel) {
        updatedChannel.isConnected = true;
        updatedChannel.botId = botId;

        resolve({
          success: true,
          channel: updatedChannel,
          message: `Bot ${botId} successfully connected to channel ${channelId} with persona: ${persona}`,
        });
      } else {
        resolve({
          success: false,
          message: "Channel not found",
        });
      }
    }, 1200);
  });
};
export default function Success() {
  const router = useRouter();
  const [channel, setChannel] = useState(null);
  const [bot, setBot] = useState(null);
  const [isConnecting, setIsConnecting] = useState(true);
  const [isSuccess, setIsSuccess] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    // Get data from localStorage
    if (typeof window !== "undefined") {
      const channelData = localStorage.getItem("selectedChannel");
      const botData = localStorage.getItem("selectedBot");
      const personaData = localStorage.getItem("channelPersona");
      const contentData = localStorage.getItem("channelContent");

      if (channelData) {
        setChannel(JSON.parse(channelData));
      }

      if (botData) {
        setBot(JSON.parse(botData));
      }

      // Connect the bot to the channel using the mock API
      const connectBot = async () => {
        try {
          setIsConnecting(true);
          const channelObj = JSON.parse(channelData);
          const botObj = JSON.parse(botData);
          const personaObj = JSON.parse(personaData);
          const contentObj = JSON.parse(contentData);

          const result = await connectBotToChannel(
            channelObj.id,
            botObj.id,
            contentObj,
            personaObj
          );

          if (result.success) {
            setIsSuccess(true);
            // Trigger confetti animation
            if (typeof window !== "undefined") {
              setTimeout(() => {
                confetti({
                  particleCount: 100,
                  spread: 70,
                  origin: { y: 0.6 },
                });
              }, 500);
            }
          } else {
            setError(
              result.message || "Something went wrong. Please try again."
            );
          }
        } catch (err) {
          console.error("Failed to connect bot:", err);
          setError("Connection failed. Please try again.");
        } finally {
          setIsConnecting(false);
        }
      };

      connectBot();
    }

    return () => {
      // Cleanup
    };
  }, [router]);

  return (
    <PageTransition>
      <div className="container mx-auto max-w-md p-4 text-center">
        {isConnecting ? (
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
        ) : isSuccess ? (
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
              {channel?.name} is now connected with {bot?.name}
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
                  <div className="w-5 h-5 bg-primary rounded-full flex items-center justify-center text-primary-content text-xs mt-0.5 mr-2">
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
                  className="flex items-start"
                >
                  <div className="w-5 h-5 bg-primary rounded-full flex items-center justify-center text-primary-content text-xs mt-0.5 mr-2">
                    3
                  </div>
                  <div>
                    You'll receive notifications when content is ready for
                    review
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
              {error || "Something went wrong. Please try again."}
            </p>

            <button
              className="btn btn-primary"
              onClick={() => router.push("/add-channel")}
            >
              Try Again
            </button>
          </motion.div>
        )}
        <button className="btn btn-ghost" onClick={() => router.push("/")}>
          Return
        </button>
      </div>
    </PageTransition>
  );
}
