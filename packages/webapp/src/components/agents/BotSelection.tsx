"use client";

import { motion } from "framer-motion";
import { FiCheck, FiChevronRight } from "react-icons/fi";
import { useApi } from "@/hooks/useApi";
import { useQuery } from "@tanstack/react-query";
import cn from "clsx";
import { twMerge } from "tailwind-merge";

import {
  tgAgentsListBots,
  TgAgentsListBotsError,
  TgUserBot,
} from "@viralink-ai/sdk";

const BotSelection = ({
  selectedBotId,
  onSelect,
}: {
  selectedBotId?: string;
  onSelect: (bot: TgUserBot) => void;
}) => {
  const api = useApi();

  const { data: bots, isPending } = useQuery<
    TgUserBot[],
    TgAgentsListBotsError
  >({
    queryKey: ["bots"],
    queryFn: async () => {
      const { data } = await tgAgentsListBots();
      return data ?? [];
    },
    throwOnError: true,
    enabled: !!api,
  });

  if (isPending) {
    return (
      <div className="space-y-4 mt-4">
        {[1, 2, 3].map((item) => (
          <div key={item} className="card bg-base-200 shadow-sm animate-pulse">
            <div className="card-body p-4">
              <div className="flex items-center">
                <div className="w-16 h-16 bg-base-300 rounded-md"></div>
                <div className="ml-3 space-y-2 flex-1">
                  <div className="h-4 w-24 bg-base-300 rounded"></div>
                  <div className="h-3 w-40 bg-base-300 rounded"></div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-4 mt-4"
    >
      {bots?.map((bot) => (
        <motion.div
          key={bot.id}
          initial={{ y: 10, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          whileHover={{ scale: 1.01 }}
          whileTap={{ scale: 0.99 }}
          transition={{ duration: 0.2 }}
          className={twMerge(
            cn(
              "card cursor-pointer hover:shadow-md transition-all border border-transparent",
              selectedBotId === bot.id
                ? "bg-primary/10 border-primary"
                : "bg-base-200"
            )
          )}
          onClick={() => onSelect(bot)}
        >
          <div className="card-body p-4">
            <div className="flex items-center">
              <div className="w-16 h-16 bg-primary text-primary-content rounded-md flex items-center justify-center text-xl font-bold">
                {bot.metadata_?.first_name?.substring(0, 2).toUpperCase()}
              </div>

              <div className="ml-4 flex-1">
                <h3 className="font-semibold">{bot.metadata_?.first_name}</h3>
                <p className="text-sm opacity-80">@{bot.metadata_?.username}</p>
                {bot.metadata_?.description && (
                  <p className="text-sm mt-1">{bot.metadata_?.description}</p>
                )}

                {/*
                {bot.capabilities && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {bot.capabilities.map((capability) => (
                      <span
                        key={capability}
                        className="badge badge-sm badge-outline"
                      >
                        {capability}
                      </span>
                    ))}
                  </div>
                )}
                */}
              </div>

              <div className="ml-2">
                {selectedBotId === bot.id ? (
                  <span className="text-primary text-2xl">
                    <FiCheck />
                  </span>
                ) : (
                  <span className="text-base-content opacity-50">
                    <FiChevronRight />
                  </span>
                )}
              </div>
            </div>
          </div>
        </motion.div>
      ))}

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
        className="divider mt-8 mb-6"
      >
        OR
      </motion.div>
    </motion.div>
  );
};

export default BotSelection;
