"use client";

import { useParams } from "next/navigation";
import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import {
  FiSettings,
  FiUsers,
  FiFileText,
  FiEye,
  FiTrendingUp,
  FiCheckCircle,
  FiAlertCircle,
  FiSave,
} from "react-icons/fi";
import { RiDeleteBin6Line } from "react-icons/ri";
import { useMutation, useQuery } from "@tanstack/react-query";

import {
  TgAgent,
  tgAgentsDelete,
  tgAgentsGet,
  TgAgentsGetError,
} from "@viralink-ai/sdk";

import PageTransition from "@/components/PageTransition";
import { BackButton } from "@/components/BackButton";
import { strError } from "@/utils/errors";
import { getChannelUsername } from "@/components/agents/utils";
import { useApi } from "@/hooks/useApi";

import BotBlock from "./_components/BotBlock";
import PersonaBlock from "./_components/PersonaBlock";
import ContentBlock from "./_components/ContentBlock";
import RecommendationsBlock from "./_components/RecommendationsBlock";
import { useCallback } from "react";

export default function AgentPage() {
  const { id: agentId } = useParams<{ id: string }>();
  const router = useRouter();

  const api = useApi();

  const {
    data: agent,
    isPending,
    refetch,
    error,
  } = useQuery<TgAgent, TgAgentsGetError>({
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

  const { mutate: deleteAgent } = useMutation({
    mutationFn: async () => {
      await tgAgentsDelete({
        path: {
          agent_id: agentId,
        },
        throwOnError: true,
      });
    },
    onSuccess: useCallback(() => {
      router.push("/");
    }, [router]),
  });

  const onShowDeleteModal = useCallback(() => {
    const modal = document.getElementById("delete-channel-modal");
    if (!modal) return;
    // @ts-ignore
    modal.showModal();
  }, []);

  if (isPending) {
    return (
      <PageTransition>
        <BackButton href="/" />
        <Skeleton />;
      </PageTransition>
    );
  }

  if (error) {
    return (
      <PageTransition>
        <BackButton href="/" />
        <div className="container mx-auto max-w-md p-4">
          <div className="card bg-error text-error-content p-6 text-center">
            <FiAlertCircle className="text-4xl mx-auto mb-3" />
            <h2 className="text-xl font-bold mb-2">Error Loading Channel</h2>
            <p>{strError(error)}</p>
            <button
              className="btn btn-outline mt-4 mx-auto"
              onClick={() => refetch()}
            >
              Try Again
            </button>
          </div>
        </div>
      </PageTransition>
    );
  }

  return (
    <PageTransition>
      <BackButton href="/" />

      <div className="container mx-auto max-w-md p-4">
        <div className="card bg-base-200 p-5 mb-6">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
            {/* Left side - Channel info */}
            <div className="flex items-center">
              <div className="w-16 h-16 bg-primary text-primary-content rounded-md flex items-center justify-center text-2xl font-semibold">
                {agent.channel_username?.charAt(0)}
              </div>

              <div className="ml-4">
                <h1 className="text-2xl font-bold">
                  {agent.channel_metadata?.title}
                </h1>
                <p className="text-sm opacity-70">
                  {getChannelUsername(agent)}
                </p>
                <div className="flex flex-wrap gap-x-4 mt-1">
                  <span className="text-xs opacity-70 flex items-center">
                    <FiUsers className="mr-1" /> 10 members
                  </span>
                  <span className="text-xs opacity-70 flex items-center">
                    <FiFileText className="mr-1" /> 11 posts
                  </span>
                  <span className="text-xs opacity-70 flex items-center">
                    <FiEye className="mr-1" /> 111 views
                  </span>
                  <span className="text-xs opacity-70 flex items-center">
                    <FiTrendingUp className="mr-1" /> 72% growth
                  </span>
                </div>
              </div>
            </div>

            <div>
              {agent.status === "active" ? (
                <div className="badge badge-success gap-1 py-3">
                  <FiCheckCircle />
                  <span>Active</span>
                </div>
              ) : (
                <div className="badge badge-warning gap-1 py-3">
                  <FiAlertCircle />
                  <span>Not Connected</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {agent.channel_metadata?.description && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="card bg-base-100 border border-base-300 p-5 mb-6"
          >
            <h2 className="text-lg font-semibold mb-2 flex items-center">
              <FiFileText className="mr-2 text-primary" /> About This Channel
            </h2>
            <p className="opacity-80">{agent.channel_metadata?.description}</p>
          </motion.div>
        )}

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="card bg-base-100 border border-base-300 p-5 mb-6"
        >
          <BotBlock agent={agent} />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="card bg-base-100 border border-base-300 p-5 mb-6"
        >
          <h2 className="text-lg font-semibold mb-4 flex items-center">
            <FiSettings className="mr-2 text-primary" /> Content Settings
          </h2>

          <ContentBlock agent={agent} className="my-3" />
          <PersonaBlock agent={agent} className="my-3" />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="card bg-base-100 border border-base-300 p-5 mb-6"
        >
          <RecommendationsBlock />
        </motion.div>

        <button onClick={() => {}} className="btn btn-primary w-full">
          <>
            <FiSave />
            Save Changes
          </>
        </button>
        <button
          onClick={onShowDeleteModal}
          className="btn btn-error btn-outline w-full my-2"
        >
          <>
            <RiDeleteBin6Line />
            Delete Channel
          </>
        </button>
      </div>
      <dialog
        id="delete-channel-modal"
        className="modal modal-bottom sm:modal-middle"
      >
        <div className="modal-box">
          <h3 className="font-bold text-lg">
            Delete {getChannelUsername(agent)} channel?
          </h3>
          <p className="py-4">
            Would you like to delete this channel? This action cannot be undone.
          </p>
          <div className="modal-action">
            <form method="dialog">
              <button className="btn mx-2">No</button>
              <button
                className="btn btn-error btn-outline"
                onClick={() => deleteAgent()}
              >
                Yes
              </button>
            </form>
          </div>
        </div>
      </dialog>
    </PageTransition>
  );
}

function Skeleton() {
  return (
    <div className="container mx-auto max-w-md p-4">
      {/* Channel Header skeleton */}
      <div className="card bg-base-200 p-5 mb-6">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          {/* Left side - Channel info skeleton */}
          <div className="flex items-center">
            <div className="skeleton w-16 h-16 rounded-md"></div>
            <div className="ml-4">
              <div className="skeleton h-8 w-48 mb-2"></div>
              <div className="skeleton h-4 w-32"></div>
              <div className="flex flex-wrap gap-x-4 mt-3">
                <div className="skeleton h-3 w-24"></div>
                <div className="skeleton h-3 w-20"></div>
                <div className="skeleton h-3 w-28"></div>
              </div>
            </div>
          </div>
          {/* Right side - Status badge skeleton */}
          <div className="skeleton h-8 w-24 rounded-full"></div>
        </div>
      </div>

      {/* Description skeleton */}
      <div className="card bg-base-100 border border-base-300 p-5 mb-6">
        <div className="skeleton h-6 w-40 mb-4"></div>
        <div className="skeleton h-4 w-full mb-2"></div>
        <div className="skeleton h-4 w-5/6 mb-2"></div>
        <div className="skeleton h-4 w-4/6"></div>
      </div>

      {/* Bot Connection skeleton */}
      <div className="card bg-base-100 border border-base-300 p-5 mb-6">
        <div className="skeleton h-6 w-48 mb-4"></div>
        <div className="flex items-center mb-4">
          <div className="skeleton w-12 h-12 rounded-md mr-3"></div>
          <div>
            <div className="skeleton h-5 w-32 mb-2"></div>
            <div className="skeleton h-3 w-24"></div>
          </div>
          <div className="skeleton h-8 w-28 ml-auto"></div>
        </div>
        <div className="flex flex-wrap gap-2 mb-4">
          <div className="skeleton h-6 w-28 rounded-full"></div>
          <div className="skeleton h-6 w-24 rounded-full"></div>
          <div className="skeleton h-6 w-32 rounded-full"></div>
        </div>
        <div className="skeleton h-8 w-64"></div>
      </div>

      {/* Content Settings skeleton */}
      <div className="card bg-base-100 border border-base-300 p-5 mb-6">
        <div className="skeleton h-6 w-36 mb-4"></div>
        <div className="flex flex-wrap gap-2 mb-4">
          <div className="skeleton h-6 w-16 rounded-full"></div>
          <div className="skeleton h-6 w-20 rounded-full"></div>
          <div className="skeleton h-6 w-14 rounded-full"></div>
        </div>
        <div className="skeleton h-32 w-full rounded-lg mb-3"></div>
        <div className="skeleton h-8 w-40"></div>
      </div>
    </div>
  );
}
