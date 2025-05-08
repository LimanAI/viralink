"use client";

import { useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { useMutation } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { FiAlertCircle, FiLoader } from "react-icons/fi";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import cn from "clsx";

import PageTransition from "@/components/PageTransition";
import { BackButton } from "@/components/BackButton";
import { useApi } from "@/hooks/useApi";
import { useForm } from "react-hook-form";
import {
  TgAgent,
  tgAgentsCreateBot,
  TgAgentsCreateBotError,
} from "@viralink-ai/sdk";
import { strError } from "@/utils/errors";

const formSchema = z.object({
  apiToken: z.string().min(1, "Bot API Token is required"),
});

type FormData = z.infer<typeof formSchema>;

export default function CreateBot() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();

  const api = useApi();
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(formSchema),
  });

  const { mutate, isPending, error } = useMutation<
    TgAgent,
    TgAgentsCreateBotError,
    FormData
  >({
    mutationFn: async (data: FormData) => {
      if (!api) throw new Error("API not initialized");
      const { data: agent } = await tgAgentsCreateBot({
        path: {
          agent_id: id,
        },
        body: {
          bot_token: data.apiToken,
        },
        throwOnError: true,
      });
      return agent;
    },
    onSuccess: (agent?: TgAgent) => {
      if (!agent) throw new Error("Failed to create bot");
      router.push(`/add-channel/${agent.id}/describe-persona`);
    },
  });

  const onSubmit = useCallback(
    async (data: FormData) => {
      mutate(data);
    },
    [mutate]
  );

  return (
    <PageTransition>
      <BackButton />
      <div className="container mx-auto max-w-md p-4">
        <h1 className="text-2xl font-bold mb-2">
          Connect a personal Telegram Bot
        </h1>

        <motion.div
          initial={{ y: 10, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="card bg-base-300 my-4"
        >
          <div className="card-body p-4 text-center">
            <p className="text-sm opacity-80 text-left">
              To manage your channel, you’ll need to create a personal Telegram
              bot. This bot will allow our system to securely access and manage
              your channel on your behalf.
            </p>
          </div>
        </motion.div>

        <form onSubmit={handleSubmit(onSubmit)}>
          <motion.div
            initial={{ y: 10, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            <div className="form-control w-full mb-4">
              {isPending && (
                <div className="flex justify-center items-center pt-4">
                  <FiLoader className="animate-spin text-2xl text-primary mr-2" />
                  <span>Checking the bot credentials</span>
                </div>
              )}

              <input
                type="text"
                placeholder="Bot API Token"
                className={cn("input input-lg w-full", {
                  "input-error": errors.apiToken,
                  hidden: isPending,
                })}
                {...register("apiToken")}
              />
              <label className="label">
                {errors.apiToken && (
                  <label className="label pt-2">
                    <span className="label-text-alt text-error">
                      {errors.apiToken.message}
                    </span>
                  </label>
                )}
              </label>
            </div>
          </motion.div>
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
          <InfoBlock />

          <button
            type="submit"
            className="btn btn-primary w-full mt-4"
            disabled={isPending}
          >
            Continue
          </button>
        </form>
      </div>
    </PageTransition>
  );
}

function InfoBlock() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2, duration: 0.5 }}
      className="mt-8 space-y-2"
    >
      <h3 className="font-semibold">How to get Bot API Token?</h3>

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
              Open{" "}
              <Link
                href="https://t.me/botfather"
                className="link font-semibold"
              >
                @BotFather
              </Link>
            </p>
            <p className="text-xs opacity-70">
              This is official Telegram bot for creating and managing bots
            </p>
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
              Select existing bot or create a new one
            </p>
            <p className="text-xs opacity-70">
              Press start and select either /newbot or /mybots commands
            </p>
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
            <p className="font-medium">Copy the bot API token </p>
            <p className="text-xs opacity-70">And paste in the input above</p>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
}
