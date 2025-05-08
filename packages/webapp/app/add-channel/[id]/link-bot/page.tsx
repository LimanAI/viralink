"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import PageTransition from "@/components/PageTransition";
import { motion } from "framer-motion";
import cn from "clsx";

import {
  FiSettings,
  FiUserPlus,
  FiRefreshCw,
  FiCheck,
  FiAlertCircle,
} from "react-icons/fi";
import { BackButton } from "@/components/BackButton";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useApi } from "@/hooks/useApi";
import {
  TgAgent,
  tgAgentsCheckBotPermissions,
  tgAgentsGet,
} from "@viralink-ai/sdk";
import Link from "next/link";
import ProgressBar from "@/components/ProgressBar";

export default function GrantAccess() {
  const { id } = useParams<{ id: string }>();
  const [accessGranted, setAccessGranted] = useState(false);

  const api = useApi();

  const { data: agent } = useQuery({
    queryKey: ["/agents", id],
    queryFn: async () => {
      const { data } = await tgAgentsGet({
        path: {
          agent_id: id,
        },
        throwOnError: true,
      });
      return data;
    },
    enabled: !!api,
  });

  useEffect(() => {
    if (!agent) return;
    setAccessGranted(
      agent.status === "waiting_channel_profile" || agent.status === "active"
    );
  }, [agent]);

  return (
    <>
      <ProgressBar currentStep={3} totalSteps={5} />
      <PageTransition>
        <BackButton />
        <div className="container mx-auto max-w-md p-4 pb-20">
          <div className="flex items-center mb-4">
            <h1 className="text-2xl font-bold">Grant Bot Access</h1>
          </div>

          <p className="text-sm opacity-70 mb-6">
            <Header
              accessGranted={accessGranted}
              channelUsername={agent?.channel_username}
              botUsername={agent?.user_bot?.metadata_?.username}
            />
          </p>

          {!accessGranted && (
            <Instructions
              channelUsername={agent?.channel_username}
              botUsername={agent?.user_bot?.metadata_?.username}
            />
          )}

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6, duration: 0.5 }}
          >
            {accessGranted ? (
              <AccessGranted agent={agent} />
            ) : (
              <AccessChecker agentId={id} />
            )}
          </motion.div>

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
                <li>• Bot only needs basic access to generate content</li>
                <li>• To auto-publish, add the bot as an admin</li>
              </ul>
            </motion.div>
          )}
        </div>
      </PageTransition>
    </>
  );
}

function Header({
  accessGranted,
  channelUsername,
  botUsername,
}: {
  accessGranted: boolean;
  channelUsername?: string | null;
  botUsername?: string | null;
}) {
  if (accessGranted) {
    return (
      <span>
        Great! {botUsername ? `@${botUsername}` : "The bot"} now has access to{" "}
        {channelUsername ? `@${channelUsername}` : "the channel"}`
      </span>
    );
  }
  return (
    <span>
      {botUsername ? `@${botUsername}` : "The bot"} needs to be added to{" "}
      {channelUsername ? `@${channelUsername}` : "the channel"}
    </span>
  );
}

const getNextLink = (agent?: TgAgent) => {
  if (!agent) return "/";

  switch (agent.status) {
    case "waiting_channel_profile":
      if (!agent.channel_profile?.content_description) {
        return `/add-channel/${agent.id}/describe-content`;
      }
      if (!agent.channel_profile?.persona_description) {
        return `/add-channel/${agent.id}/describe-persona`;
      }
      return "/";
    default:
      return "/";
  }
};

function AccessGranted({ agent }: { agent?: TgAgent }) {
  const router = useRouter();

  return (
    <>
      <div className="card bg-success text-success-content p-5 text-center">
        <div className="py-3">
          <div className="w-16 h-16 bg-success-content/30 rounded-full flex items-center justify-center text-3xl mx-auto mb-4">
            <FiCheck />
          </div>
          <h3 className="text-xl font-bold mb-2">Access Granted!</h3>
          <p className="opacity-80 mb-3">
            Bot successfully connected to your channel
          </p>
          {/*
          <div className="flex justify-center">
            <div className="loading loading-dots loading-md"></div>
          </div>
          */}
        </div>
      </div>

      <button
        className="btn btn-primary mt-6 w-full"
        onClick={() => router.push(getNextLink(agent))}
      >
        Continue
      </button>
    </>
  );
}

function AccessChecker({ agentId }: { agentId: string }) {
  const queryClient = useQueryClient();

  const { mutate, isPending: isChecking } = useMutation({
    mutationFn: async (agentId: string) => {
      const { data } = await tgAgentsCheckBotPermissions({
        path: {
          agent_id: agentId,
        },
        throwOnError: true,
      });
      return data;
    },
    onSuccess: (agent) => {
      queryClient.setQueryData(["/agents", agentId], (prev: TgAgent) => ({
        ...prev,
        status: agent.status,
      }));
    },

    retry: 0,
  });

  useEffect(() => {
    mutate(agentId);

    const interval = setInterval(() => {
      mutate(agentId);
    }, 5000);

    return () => {
      clearInterval(interval);
    };
  }, [agentId]);

  return (
    <div className="card bg-base-300 p-5 text-center">
      <div className="py-4">
        <h3 className="text-lg font-bold mb-3">Waiting for an access...</h3>

        <div className="flex items-center justify-center mb-4">
          <div
            className={cn(
              "w-12 h-12 rounded-full border-4 mx-auto",
              isChecking
                ? "border-primary border-t-transparent animate-spin"
                : "border-base-content border-opacity-20"
            )}
          ></div>
        </div>

        <p className="text-sm opacity-70 mb-4">
          We're checking if the bot has been added to your channel
        </p>

        <button
          onClick={() => mutate(agentId)}
          className="btn btn-sm btn-outline"
          disabled={isChecking}
        >
          <FiRefreshCw className={`mr-2 ${isChecking ? "animate-spin" : ""}`} />
          {isChecking ? "Checking..." : "Check Again"}
        </button>
      </div>
    </div>
  );
}

function LegacyInstructions({ channelUsername }: { channelUsername?: string }) {
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
            {channelUsername && (
              <div className="mt-2 flex items-center text-primary font-medium">
                <span className="text-sm">Search for @{channelUsername}</span>
              </div>
            )}
          </div>
        </motion.div>
      </div>
    </div>
  );
}

function Instructions({
  channelUsername,
  botUsername,
}: {
  channelUsername?: string | null;
  botUsername?: string | null;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2, duration: 0.5 }}
      className="mt-4 mb-6 space-y-2"
    >
      <h3 className="font-semibold">Follow these steps</h3>

      <motion.div
        className="card bg-base-200 p-3"
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.3, duration: 0.5 }}
      >
        <div className="flex items-center">
          <div className="w-8 h-8 bg-primary/20 rounded-full flex items-center justify-center">
            1
          </div>
          <div className="ml-3">
            <p className="font-medium">
              Open your channel{" "}
              {channelUsername && (
                <Link
                  href={`https://t.me/${channelUsername}`}
                  className="link font-semibold"
                >
                  @{channelUsername}
                </Link>
              )}
            </p>
            <p className="text-xs opacity-70">And go to settings</p>
          </div>
        </div>
      </motion.div>

      <motion.div
        className="card bg-base-200 p-3"
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.4, duration: 0.5 }}
      >
        <div className="flex items-center">
          <div className="w-8 h-8 bg-primary/20 rounded-full flex items-center justify-center">
            2
          </div>
          <div className="ml-3">
            <p className="font-medium">
              Tap on
              <span className="ml-2">
                <FiUserPlus className="h-5 w-5 mx-1 inline-block" />
                <span className="font-bold">Add Members</span>
              </span>
            </p>
            <p className="text-xs opacity-70">Find the bot in the list</p>
          </div>
        </div>
      </motion.div>

      <motion.div
        className="card bg-base-200 p-3"
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.5, duration: 0.5 }}
      >
        <div className="flex items-center">
          <div className="w-8 h-8 bg-primary/20 rounded-full flex items-center justify-center">
            3
          </div>
          <div className="ml-3">
            <p className="font-medium">
              Add{" "}
              {botUsername ? (
                <span className="font-bold">@{botUsername}</span>
              ) : (
                "the bot"
              )}{" "}
              to the members
            </p>
            <p className="text-xs opacity-70">
              It allows to get info about the channel
            </p>
          </div>
        </div>
      </motion.div>

      <motion.div
        className="card bg-base-200 p-3"
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.6, duration: 0.5 }}
      >
        <div className="flex items-center">
          <div className="w-8 h-8 bg-primary/20 rounded-full flex items-center justify-center">
            4
          </div>
          <div className="ml-3">
            <p className="font-medium">
              (Optional) Grant{" "}
              {botUsername ? (
                <span className="font-bold">@{botUsername}</span>
              ) : (
                "the bot"
              )}{" "}
              admin permissions
            </p>
            <p className="text-xs opacity-70">
              It allows to publish posts automatically.
            </p>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
}
