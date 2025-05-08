"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import {
  FiUsers,
  FiFileText,
  FiCheck,
  FiLink,
  FiLayout,
  FiPlus,
  FiType,
  FiBook,
} from "react-icons/fi";

import type { TgAgent } from "@viralink-ai/sdk";
import { useRouter } from "next/navigation";

export default function AgentItem({ agent }: { agent: TgAgent }) {
  const router = useRouter();
  const onCardClick = () => {
    router.push(`/agents/${agent.id}`);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="card bg-base-200 shadow-sm w-full"
    >
      <div className="card-body p-4 cursor-pointer" onClick={onCardClick}>
        <div className="flex items-center">
          <div className="w-12 h-12 bg-primary text-primary-content rounded-md flex items-center justify-center text-lg font-semibold">
            {agent.channel_metadata?.title?.charAt(0)}
          </div>

          <div className="ml-3">
            <h3 className="font-semibold">
              @{agent.channel_metadata?.username || agent.channel_username}
            </h3>

            <div className="flex items-center text-xs opacity-80 space-x-3 mt-1">
              <span className="flex items-center">
                <FiUsers className="mr-1" /> 0
              </span>
              <span className="flex items-center">
                <FiFileText className="mr-1" /> 0
              </span>
            </div>
          </div>
          <AgentStatus agent={agent} />
        </div>

        {agent.channel_metadata?.description && (
          <p className="text-sm opacity-80 mt-2">
            {agent.channel_metadata?.description}
          </p>
        )}
      </div>
    </motion.div>
  );
}

function AgentStatus({ agent }: { agent: TgAgent }) {
  if (agent.status === "active") {
    return (
      <div className="ml-auto badge badge-success gap-1">
        <FiCheck /> Active
      </div>
    );
  }

  if (agent.status === "waiting_bot_attach") {
    return (
      <Link
        href={`/add-channel/${agent.id}/select-bot`}
        className="ml-auto btn btn-primary btn-sm gap-1"
        onClick={(e) => {
          e.stopPropagation();
        }}
      >
        <FiLink /> Connect
      </Link>
    );
  }

  if (agent.status === "waiting_bot_access") {
    return (
      <Link
        href={`/add-channel/${agent.id}/link-bot`}
        className="ml-auto btn btn-primary btn-sm gap-1"
        onClick={(e) => {
          e.stopPropagation();
        }}
      >
        <FiLink /> Connect
      </Link>
    );
  }

  if (
    agent.status === "waiting_channel_profile" &&
    !agent.channel_profile?.content_description
  ) {
    return (
      <Link
        href={`/add-channel/${agent.id}/describe-content`}
        className="ml-auto btn btn-accent btn-sm gap-1"
        onClick={(e) => {
          e.stopPropagation();
        }}
      >
        <FiBook className="h-3 w-3" /> Prompts
      </Link>
    );
  }

  if (agent.status === "waiting_channel_profile") {
    return (
      <Link
        href={`/add-channel/${agent.id}/describe-persona`}
        className="ml-auto btn btn-secondary btn-sm gap-1"
        onClick={(e) => {
          e.stopPropagation();
        }}
      >
        <FiBook className="h-3 w-3" /> Prompts
      </Link>
    );
  }
}
