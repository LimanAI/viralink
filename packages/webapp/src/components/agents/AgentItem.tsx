"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { FiUsers, FiFileText, FiCheck, FiLink } from "react-icons/fi";

import type { TgAgent } from "@viralink-ai/sdk";

const ChannelItem = ({ agent }: { agent: TgAgent }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="card bg-base-200 shadow-sm w-full"
    >
      <div className="card-body p-4">
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
};

function AgentStatus({ agent }: { agent: TgAgent }) {
  if (agent.status === "active") {
    return (
      <div className="ml-auto badge badge-success gap-1">
        <FiCheck /> Connected
      </div>
    );
  }

  if (agent.status === "waiting_bot_attach") {
    return (
      <Link
        href={`/add-channel/${agent.id}/select-bot`}
        className="ml-auto btn btn-primary btn-sm gap-1"
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
      >
        <FiLink /> Connect
      </Link>
    );
  }
}

export default ChannelItem;
