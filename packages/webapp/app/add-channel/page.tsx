"use client";

import { useCallback, useState } from "react";
import { useRouter } from "next/navigation";
import { FiEdit, FiLink, FiMessageSquare, FiPlay } from "react-icons/fi";
import { useMutation } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { motion } from "framer-motion";
import { z } from "zod";
import cn from "clsx";

import { TgAgent, tgAgentsCreate } from "@viralink-ai/sdk";

import PageTransition from "@/components/PageTransition";
import { useApi } from "@/hooks/useApi";
import { BackButton } from "@/components/BackButton";
import ProgressBar from "@/components/ProgressBar";

const isValidInviteLink = (url: string) => {
  return /^(https?:\/\/)?(t\.me\/joinchat\/|t\.me\/\+)[a-zA-Z0-9_-]+$/.test(
    url
  );
};

const isValidChannelHandle = (handle: string) => {
  return /^(@)?[a-zA-Z][a-zA-Z0-9_]{3,}$/.test(handle);
};

const formSchema = z.object({
  channelUsername: z
    .string({ required_error: "Channel name is required" })
    .refine((val) => isValidChannelHandle(val), "Invalid channe name format"),
});
type formData = z.infer<typeof formSchema>;

export default function AddChannel() {
  const router = useRouter();

  const api = useApi();
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<formData>({
    resolver: zodResolver(formSchema),
  });

  const { mutate, isPending: isSubmitting } = useMutation({
    mutationFn: async (data: formData) => {
      if (!api) throw new Error("API not initialized");
      const { data: agent } = await tgAgentsCreate({
        body: { channel_username: data.channelUsername },
      });
      return agent;
    },
    onSuccess: useCallback(
      (agent?: TgAgent) => {
        if (!agent) return;
        router.push(`/add-channel/${agent.id}/select-bot`);
      },
      [router]
    ),
  });

  const onSubmit = useCallback(
    async (data: formData) => {
      mutate(data);
    },
    [mutate]
  );

  return (
    <>
      <ProgressBar currentStep={1} totalSteps={5} />
      <PageTransition>
        <BackButton href="/" />
        <div className="container mx-auto max-w-md p-4">
          <h1 className="text-2xl font-bold mb-2">Add a Channel</h1>
          <p className="text-sm opacity-70 mb-6">
            Connect your Telegram channel with BoostIQ
          </p>

          <form onSubmit={handleSubmit(onSubmit)}>
            <motion.div
              initial={{ y: 10, opacity: 0 }}
              animate={{ y: 1, opacity: 1 }}
              transition={{ duration: 0.3 }}
              className="form-control"
            >
              <div className="relative">
                <span className="absolute left-3 top-3.5 text-base-content/50">
                  <FiLink />
                </span>

                <input
                  type="text"
                  placeholder="Channel name"
                  className={cn("input input-lg w-full", {
                    "input-error": errors.channelUsername,
                  })}
                  {...register("channelUsername")}
                />
                {errors.channelUsername && (
                  <label className="label pt-2">
                    <span className="label-text-alt text-error">
                      {errors.channelUsername.message}
                    </span>
                  </label>
                )}
              </div>
            </motion.div>

            <InfoBlock />

            <button
              type="submit"
              className="btn btn-primary mt-6 w-full"
              disabled={isSubmitting}
            >
              Continue
            </button>
          </form>
        </div>
      </PageTransition>
    </>
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
      <h3 className="font-semibold">What can BoostIQ do for your channel?</h3>

      <motion.div
        className="card bg-base-200 p-3"
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.3, duration: 0.5 }}
      >
        <div className="flex items-center">
          <div className="w-8 h-8 bg-primary/20 rounded-full flex items-center justify-center text-primary">
            <FiEdit />
          </div>
          <div className="ml-3">
            <p className="font-medium">Generate engaging content</p>
            <p className="text-xs opacity-70">
              Never run out of quality content
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
          <div className="w-8 h-8 bg-primary/20 rounded-full flex items-center justify-center text-primary">
            <FiMessageSquare />
          </div>
          <div className="ml-3">
            <p className="font-medium">Engage with audience</p>
            <p className="text-xs opacity-70">
              Respond and interact with your subscribers
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
          <div className="w-8 h-8 bg-primary/20 rounded-full flex items-center justify-center text-primary">
            <FiPlay />
          </div>
          <div className="ml-3">
            <p className="font-medium">Schedule posts</p>
            <p className="text-xs opacity-70">Post content at optimal times</p>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
}
