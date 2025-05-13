"use client";

import { motion } from "framer-motion";
import { FiPlus } from "react-icons/fi";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { useApi } from "@/hooks/useApi";

import { tgAgentsList } from "@viralink-ai/sdk";

import AgentItem from "./AgentItem";

export function AgentsList() {
  const api = useApi();

  const {
    data: agents,
    isPending,
    error,
  } = useQuery({
    queryKey: ["/agents"],
    queryFn: async () => {
      const { data } = await tgAgentsList({ throwOnError: true });
      return data;
    },
    enabled: !!api,
  });

  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  if (isPending) {
    return <Skeleton />;
  }

  return (
    <div className="mt-4 w-full">
      {error ? (
        <div className="alert alert-error alert-outline mt-4">
          <span>{error.message}</span>
        </div>
      ) : (
        <motion.div
          variants={container}
          initial="hidden"
          animate="show"
          className="space-y-4"
        >
          {agents?.map((agent) => <AgentItem key={agent.id} agent={agent} />)}
        </motion.div>
      )}

      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.4 }}
        className="mt-6"
      >
        <Link href="/add-channel" className="btn btn-primary btn-block gap-2">
          <FiPlus /> Add New Channel
        </Link>
      </motion.div>
    </div>
  );
}

export function Skeleton() {
  return (
    <div className="space-y-4 mt-4 w-full">
      {[1, 2, 3].map((item) => (
        <div
          key={item}
          className="card bg-base-200 shadow-sm w-full animate-pulse"
        >
          <div className="card-body p-4">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-base-300 rounded-full"></div>
              <div className="ml-3 space-y-2">
                <div className="h-4 w-24 bg-base-300 rounded"></div>
                <div className="h-3 w-16 bg-base-300 rounded"></div>
              </div>
              <div className="ml-auto h-8 w-20 bg-base-300 rounded-full"></div>
            </div>
            <div className="h-3 w-full bg-base-300 rounded mt-3"></div>
          </div>
        </div>
      ))}
    </div>
  );
}
