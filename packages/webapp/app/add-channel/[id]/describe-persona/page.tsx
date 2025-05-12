"use client";

import { useCallback, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { FiUser, FiAlertCircle } from "react-icons/fi";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

import {
  TgAgent,
  tgAgentsGet,
  tgAgentsUpdateChannelProfile,
  TgAgentsUpdateChannelProfileError,
} from "@viralink-ai/sdk";

import PageTransition from "@/components/PageTransition";
import { BackButton } from "@/components/BackButton";
import { useApi } from "@/hooks/useApi";
import { getBotUsername, getChannelUsername } from "@/components/agents/utils";
import { strError } from "@/utils/errors";
import ProgressBar from "@/components/ProgressBar";

// Tone options
const toneOptions = [
  { id: "professional", label: "Professional" },
  { id: "friendly", label: "Friendly & Casual" },
  { id: "humorous", label: "Humorous" },
  { id: "inspirational", label: "Inspirational" },
  { id: "educational", label: "Educational" },
];

const formSchema = z.object({
  personaDescription: z
    .string()
    .min(5, "Description too short (min 5 characters)"),
});

type FormData = z.infer<typeof formSchema>;

export default function DescribePersona() {
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
          persona_description: data.personaDescription,
        },
        throwOnError: true,
      });
      return agent;
    },
    onSuccess: (agent) => {
      router.push(`/add-channel/${agent.id}/success`);
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
      personaDescription: agent?.channel_profile?.persona_description ?? "",
    },
  });

  useEffect(() => {
    if (agent?.channel_profile?.content_description) {
      reset({
        personaDescription: agent.channel_profile.persona_description || "",
      });
    }
  }, [agent]);

  const onSubmit = useCallback(
    async (data: FormData) => {
      mutate(data);
    },
    [mutate]
  );

  return (
    <>
      <ProgressBar currentStep={5} totalSteps={5} />
      <PageTransition>
        <BackButton />
        <div className="container mx-auto max-w-md p-4">
          <div className="flex items-center mb-6">
            <h1 className="text-2xl font-bold">Define Your Channel Persona</h1>
          </div>
          <p className="text-sm opacity-70 mb-6">
            Help {getBotUsername(agent) || "your bot"} understand the voice and
            style for {getChannelUsername(agent) || "your channel"}
          </p>

          <form onSubmit={handleSubmit(onSubmit)}>
            <div className="form-control mb-6">
              <label className="label">
                <span className="label-text font-medium flex items-center">
                  <FiUser className="mr-2" /> Publisher Persona
                </span>
              </label>
              <textarea
                placeholder="Describe the persona who will be publishing content on this channel..."
                className="textarea textarea-bordered w-full h-32"
                {...register("personaDescription")}
              ></textarea>

              <label className="label">
                {errors.personaDescription && (
                  <label className="label pt-2">
                    <span className="label-text-alt text-error">
                      {errors.personaDescription.message}
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
              <h3 className="font-semibold mb-2">Why this matters:</h3>
              <p className="text-sm opacity-80">
                Defining a clear persona ensures all content from your bot
                maintains a consistent voice that resonates with your audience
                and represents your brand effectively.
              </p>
            </motion.div>

            <button
              type="submit"
              disabled={isPending}
              className="btn btn-primary w-full"
            >
              Continue
            </button>
          </form>
        </div>
      </PageTransition>
    </>
  );
}
