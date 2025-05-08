"use client";

import { useCallback, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useMutation, useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import cn from "clsx";
import { twMerge } from "tailwind-merge";

import { BackButton } from "@/components/BackButton";
import PageTransition from "@/components/PageTransition";
import {
  TgAgent,
  tgAgentsLinkBot,
  TgAgentsLinkBotData,
  TgAgentsLinkBotError,
  tgAgentsListBots,
  TgAgentsListBotsError,
  TgUserBot,
} from "@viralink-ai/sdk";
import BotSelection from "@/components/agents/BotSelection";
import { useApi } from "@/hooks/useApi";
import { FiAlertCircle } from "react-icons/fi";
import { strError } from "@/utils/errors";

export default function SelectBot() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [selectedBot, setSelectedBot] = useState<
    TgUserBot | null | "create_new_bot"
  >(null);

  const api = useApi();

  const { data: bots } = useQuery<TgUserBot[], TgAgentsListBotsError>({
    queryKey: ["bots"],
    queryFn: async () => {
      const { data } = await tgAgentsListBots();
      return data ?? [];
    },
    throwOnError: true,
    enabled: !!api,
  });

  const {
    mutate: attachBot,
    isPending: isAttaching,
    error,
  } = useMutation<TgAgent, TgAgentsLinkBotError, TgUserBot>({
    mutationFn: async (bot: TgUserBot) => {
      if (!api) throw new Error("API not initialized");
      const { data } = await tgAgentsLinkBot({
        path: {
          agent_id: id,
        },
        body: {
          bot_id: bot.id,
        },
        throwOnError: true,
      });
      return data;
    },
    onSuccess: useCallback(() => {
      router.push(`/add-channel/${id}/link-bot`);
    }, [router, id]),
  });

  const handleSelectBot = (bot: TgUserBot | null) => {
    setSelectedBot((prev) => (prev === bot ? null : bot));
  };

  const onClick = useCallback(async () => {
    if (!selectedBot) return;
    if (selectedBot === "create_new_bot") {
      router.push(`/add-channel/${id}/create-bot`);
      return;
    }
    attachBot(selectedBot);
  }, [router, selectedBot, id]);

  return (
    <PageTransition>
      <BackButton />
      <div className="container mx-auto max-w-md p-4">
        {bots?.length !== 0 ? (
          <>
            <h1 className="text-2xl font-bold mb-2">Select a Bot</h1>
            <p className="text-sm opacity-70 mb-6">
              Choose a bot that will manage content for your channel
            </p>
            {error && (
              <motion.div
                initial={{ y: 10, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.3 }}
              >
                <div className="alert alert-error mb-4 flex items-center">
                  <FiAlertCircle />
                  <span className="ml-2">{strError(error)}</span>
                </div>
              </motion.div>
            )}

            <BotSelection
              onSelect={handleSelectBot}
              selectedBotId={
                selectedBot instanceof Object ? selectedBot.id : undefined
              }
            />
          </>
        ) : null}
        <motion.div
          initial={{ y: 10, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.3 }}
          className={twMerge(
            cn(
              "card bg-base-300 cursor-pointer hover:shadow-md transition-all border border-transparent",
              selectedBot === "create_new_bot"
                ? "bg-primary/10 border-primary"
                : "bg-base-200"
            )
          )}
          onClick={() =>
            setSelectedBot((prev) =>
              prev === "create_new_bot" ? null : "create_new_bot"
            )
          }
        >
          <div className="card-body p-4 text-center">
            <h3 className="font-semibold">Add a new bot</h3>
            <p className="text-sm opacity-80">
              Add a new bot to manage content for your channel
            </p>
          </div>
        </motion.div>
        <button
          className="btn btn-primary mt-6 w-full"
          disabled={!selectedBot || isAttaching}
          onClick={onClick}
        >
          Continue
        </button>
      </div>
    </PageTransition>
  );
}
