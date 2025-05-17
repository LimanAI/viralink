"use client";

import { useCallback, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { FiCalendar, FiAlertCircle } from "react-icons/fi";
import { useMutation, useQuery } from "@tanstack/react-query";

import {
  TgAgent,
  TgAgentsUpdateChannelProfileError,
  tgAgentsGet,
  tgAgentsUpdateChannelProfile,
} from "@viralink-ai/sdk";

import PageTransition from "@/components/PageTransition";
import { BackButton } from "@/components/BackButton";
import { useApi } from "@/hooks/useApi";
import { strError } from "@/utils/errors";
import { getBotUsername, getChannelUsername } from "@/components/agents/utils";
import ProgressBar from "@/components/ProgressBar";

const formSchema = z.object({
  contentDescription: z
    .string()
    .min(10, "Description too short (min 10 characters)"),
});

type FormData = z.infer<typeof formSchema>;

export default function DescribeContent() {
  const { id: agentId } = useParams<{ id: string }>();
  const router = useRouter();

  const api = useApi();

  const { data: agent } = useQuery({
    queryKey: ["/agents", agentId],
    queryFn: async () => {
      const { data } = await tgAgentsGet({
        path: {
          agent_id: agentId,
        },
      });
      return data;
    },
    enabled: !!api,
  });

  const { mutate, isPending, error } = useMutation<
    TgAgent,
    TgAgentsUpdateChannelProfileError,
    FormData
  >({
    mutationFn: async (data: FormData) => {
      const { data: agent } = await tgAgentsUpdateChannelProfile({
        path: {
          agent_id: agentId,
        },
        body: {
          content_description: data.contentDescription,
        },
        throwOnError: true,
      });
      return agent;
    },
    onSuccess: (agent) => {
      const nextUrl = agent?.channel_profile?.persona_description
        ? `/agents/${agent.id}`
        : `/add-channel/${agent.id}/describe-persona`;
      router.push(nextUrl);
    },
  });

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      contentDescription: agent?.channel_profile?.content_description ?? "",
    },
  });

  useEffect(() => {
    if (agent?.channel_profile?.content_description) {
      reset({
        contentDescription: agent.channel_profile.content_description,
      });
    }
  }, [agent, reset]);

  const onSubmit = useCallback(
    async (data: FormData) => {
      mutate(data);
    },
    [mutate]
  );

  return (
    <>
      <ProgressBar currentStep={4} totalSteps={5} />
      <PageTransition>
        <BackButton />
        <div className="container mx-auto max-w-md p-4">
          <div className="mb-6">
            <h1 className="text-2xl font-bold mb-2">Content Preferences</h1>
            <p className="text-sm opacity-70">
              Tell {getBotUsername(agent) || "your bot"} what kind of content to
              create for {getChannelUsername(agent) || "your channel"}
            </p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)}>
            <div className="form-control mb-6">
              <label className="label">
                <span className="label-text font-medium flex items-center">
                  <FiCalendar className="mr-2" /> Content Topics & Themes
                </span>
              </label>
              <textarea
                placeholder="Describe topics your content should cover..."
                className="textarea textarea-bordered w-full h-32"
                {...register("contentDescription")}
              ></textarea>

              <label className="label">
                {errors.contentDescription && (
                  <label className="label pt-2">
                    <span className="label-text-alt text-error">
                      {errors.contentDescription.message}
                    </span>
                  </label>
                )}
              </label>
            </div>
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

            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="card bg-base-200 p-4 mb-6"
            >
              <h3 className="font-semibold mb-2">What happens next:</h3>
              <p className="text-sm opacity-80">
                After connecting, your bot will prepare content based on your
                preferences. You&apos;ll be able to review and approve all posts
                before they&apos;re published.
              </p>
            </motion.div>

            <button
              className="btn btn-primary w-full"
              disabled={isPending}
              type="submit"
            >
              Continue
            </button>
          </form>
        </div>
      </PageTransition>
    </>
  );
}
