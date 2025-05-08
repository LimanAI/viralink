"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import PageTransition from "@/components/PageTransition";
import { motion } from "framer-motion";
import {
  FiArrowLeft,
  FiSettings,
  FiUserPlus,
  FiRefreshCw,
  FiLoader,
  FiCheck,
  FiAlertCircle,
} from "react-icons/fi";
import { BackButton } from "@/components/BackButton";
import { useQuery } from "@tanstack/react-query";
import { useApi } from "@/hooks/useApi";
import { tgAgentsCheckBotPermissions } from "@viralink-ai/sdk";

export default function GrantAccess() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [channel, setChannel] = useState(null);
  const [bot, setBot] = useState(null);
  const [isChecking, setIsChecking] = useState(false);
  const [checkCount, setCheckCount] = useState(0);
  const [accessGranted, setAccessGranted] = useState(false);
  const [error, setError] = useState(null);

  const api = useApi();

  const { data } = useQuery({
    queryKey: ["agents/link-bot", id],
    queryFn: async () => {
      const { data } = await tgAgentsCheckBotPermissions({
        path: {
          agent_id: id,
        },
        throwOnError: true,
      });
      return data;
    },
    retry: 0,
    enabled: !!api,
  });
  console.log("link-bot", data);

  // Load channel and bot data from localStorage
  useEffect(() => {
    if (typeof window !== "undefined") {
      const channelData = localStorage.getItem("selectedChannel");
      const botData = localStorage.getItem("selectedBot");

      if (channelData) {
        setChannel(JSON.parse(channelData));
      } else {
        //router.push("/add-channel");
        return;
      }

      if (botData) {
        setBot(JSON.parse(botData));
      } else {
        //router.push("/add-channel/select-bot");
        return;
      }
    }
  }, [router]);

  // Function to check if bot has been granted access
  const checkBotAccess = async () => {
    setIsChecking(true);
    setError(null);

    try {
      // Simulate API call to check if bot has admin access to the channel
      await new Promise((resolve) => setTimeout(resolve, 2000));

      // Simulate success after a few checks or with 30% probability
      if (checkCount > 2 || Math.random() < 0.3) {
        setAccessGranted(true);
        // Wait a moment before redirecting
      } else {
        setCheckCount((prev) => prev + 1);
        setIsChecking(false);
      }
    } catch (err) {
      console.error("Error checking bot access:", err);
      setError("Failed to verify bot access. Please try again.");
      setIsChecking(false);
    }
  };

  // Start checking access automatically on page load
  useEffect(() => {
    if (channel && bot && !isChecking && !accessGranted && !error) {
      const timer = setTimeout(() => {
        checkBotAccess();
      }, 1000);

      return () => clearTimeout(timer);
    }
  }, [channel, bot, isChecking, accessGranted, error, checkCount]);

  const handleBack = () => {
    //router.push("/add-channel/select-bot");
  };

  // Animation variants
  const stepVariants = {
    hidden: { opacity: 0, x: -20 },
    visible: (index) => ({
      opacity: 1,
      x: 0,
      transition: {
        delay: index * 0.2,
        duration: 0.5,
      },
    }),
  };

  return (
    <PageTransition>
      <BackButton />
      <div className="container mx-auto max-w-md p-4 pb-20">
        <div className="flex items-center mb-4">
          <h1 className="text-2xl font-bold">Grant Bot Access</h1>
        </div>

        <p className="text-sm opacity-70 mb-6">
          {accessGranted
            ? `Great! @${bot?.name} now has access to ${channel?.name}`
            : `@${bot?.name} needs admin access to manage content in ${channel?.name}`}
        </p>

        {/* Instructions card */}
        {!accessGranted && <Instructions botUsername="yaz" />}

        {/* Status card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6, duration: 0.5 }}
          className={`card ${accessGranted ? "bg-success text-success-content" : "bg-base-300"} p-5 text-center`}
        >
          {accessGranted ? (
            <div className="py-3">
              <div className="w-16 h-16 bg-success-content bg-opacity-30 rounded-full flex items-center justify-center text-3xl mx-auto mb-4">
                <FiCheck />
              </div>
              <h3 className="text-xl font-bold mb-2">Access Granted!</h3>
              <p className="opacity-80 mb-3">
                Bot successfully connected to your channel
              </p>
              <div className="flex justify-center">
                <div className="loading loading-dots loading-md"></div>
              </div>
              <p className="text-sm mt-2">Redirecting to next step...</p>
            </div>
          ) : error ? (
            <div className="py-3">
              <div className="w-16 h-16 bg-error text-error-content rounded-full flex items-center justify-center text-3xl mx-auto mb-4">
                <FiAlertCircle />
              </div>
              <h3 className="text-xl font-bold mb-2">Verification Failed</h3>
              <p className="opacity-80 mb-4">{error}</p>
              <button
                onClick={checkBotAccess}
                className="btn btn-primary"
                disabled={isChecking}
              >
                <FiRefreshCw
                  className={`mr-2 ${isChecking ? "animate-spin" : ""}`}
                />
                Try Again
              </button>
            </div>
          ) : (
            <div className="py-4">
              <h3 className="text-lg font-bold mb-3">
                Waiting for admin access...
              </h3>

              <div className="flex items-center justify-center mb-4">
                <div
                  className={`w-12 h-12 rounded-full border-4 ${isChecking ? "border-primary border-t-transparent animate-spin" : "border-base-content border-opacity-20"} mx-auto`}
                ></div>
              </div>

              <p className="text-sm opacity-70 mb-4">
                We're checking if the bot has been added as an admin to your
                channel
              </p>

              <button
                onClick={checkBotAccess}
                className="btn btn-sm btn-outline"
                disabled={isChecking}
              >
                <FiRefreshCw
                  className={`mr-2 ${isChecking ? "animate-spin" : ""}`}
                />
                {isChecking ? "Checking..." : "Check Again"}
              </button>
            </div>
          )}
        </motion.div>

        {/* Hints and tips */}
        {!accessGranted && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8, duration: 0.5 }}
            className="mt-6 card bg-base-100 border border-base-300 p-4"
          >
            <h4 className="font-medium mb-2 flex items-center">
              <FiAlertCircle className="mr-2 text-primary" />
              Tips
            </h4>
            <ul className="space-y-2 text-sm opacity-80">
              <li>• Make sure to grant all posting permissions to the bot</li>
              <li>
                • The bot needs permission to post, edit, and delete messages
              </li>
              <li>• This step is required to automate content management</li>
            </ul>
          </motion.div>
        )}
      </div>
    </PageTransition>
  );
}

function Instructions({ botUsername }: { botUsername: string }) {
  const stepVariants = {
    hidden: { opacity: 0, x: -20 },
    visible: (i: number) => ({
      opacity: 1,
      x: 0,
      transition: {
        delay: i * 0.2,
        duration: 0.5,
      },
    }),
  };

  return (
    <div className="card bg-base-200 p-5 mb-6">
      <h3 className="font-semibold mb-3 flex items-center">
        <span className="w-6 h-6 bg-primary rounded-full text-primary-content flex items-center justify-center text-xs mr-2">
          <FiCheck />
        </span>
        Follow these steps:
      </h3>

      <div className="space-y-5">
        <motion.div
          className="flex"
          custom={0}
          initial="hidden"
          animate="visible"
          variants={stepVariants}
        >
          <div className="w-8 h-8 bg-base-300 rounded-full flex items-center justify-center text-base-content mr-3">
            1
          </div>
          <div>
            <p className="font-medium">Open channel settings</p>
            <p className="text-sm opacity-70">
              Open Telegram and go to your channel
            </p>
            <div className="mt-2 flex items-center text-primary">
              <FiSettings className="mr-1" />
              <span className="text-sm">
                Tap the channel name, then "Manage Channel"
              </span>
            </div>
          </div>
        </motion.div>

        <motion.div
          className="flex"
          custom={1}
          initial="hidden"
          animate="visible"
          variants={stepVariants}
        >
          <div className="w-8 h-8 bg-base-300 rounded-full flex items-center justify-center text-base-content mr-3">
            2
          </div>
          <div>
            <p className="font-medium">Go to Administrators</p>
            <p className="text-sm opacity-70">
              Find the administrators section
            </p>
            <div className="mt-2 flex items-center text-primary">
              <FiUserPlus className="mr-1" />
              <span className="text-sm">
                Tap "Administrators" then "Add Admin"
              </span>
            </div>
          </div>
        </motion.div>

        <motion.div
          className="flex"
          custom={2}
          initial="hidden"
          animate="visible"
          variants={stepVariants}
        >
          <div className="w-8 h-8 bg-base-300 rounded-full flex items-center justify-center text-base-content mr-3">
            3
          </div>
          <div>
            <p className="font-medium">Add the bot as admin</p>
            <p className="text-sm opacity-70">Search for the bot and add it</p>
            <div className="mt-2 flex items-center text-primary font-medium">
              <span className="text-sm">Search for @{botUsername}</span>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
