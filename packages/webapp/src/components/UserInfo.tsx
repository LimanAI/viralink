"use client";

import { motion } from "framer-motion";
import { FiUser } from "react-icons/fi";
import { useQuery } from "@tanstack/react-query";
import { tgbotAuthMe } from "@viralink-ai/sdk";
import CreditBlock from "./blocks/CreditBlock";

const UserInfo = () => {
  const { data: user, isPending } = useQuery({
    queryKey: ["me"],
    queryFn: async () => {
      const { data } = await tgbotAuthMe({
        throwOnError: true,
      });
      return data;
    },
  });

  if (isPending || !user) {
    return <Skeleton />;
  }

  const handleProfileClick = () => {};

  return (
    <div className="flex items-center justify-between mb-5">
      <CreditBlock credits={user.credits_balance} />

      <motion.div
        initial={{ opacity: 0, x: 10 }}
        animate={{ opacity: 1, x: 0 }}
        className="flex items-center"
      >
        <motion.div
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={handleProfileClick}
          className="w-10 h-10 bg-primary text-primary-content rounded-full flex items-center justify-center text-sm font-semibold cursor-pointer shadow-sm"
        >
          {user.first_name ? user.first_name.charAt(0) : <FiUser />}
        </motion.div>

        <div className="ml-2 text-right">
          <h3 className="font-semibold text-sm leading-tight">
            {user.first_name} {user.last_name || ""}
          </h3>
          {user.username && (
            <p className="text-xs opacity-70 leading-tight">@{user.username}</p>
          )}
        </div>
      </motion.div>
    </div>
  );
};

function Skeleton() {
  return (
    <div className="flex items-center justify-between mb-5">
      {/* Credit skeleton */}
      <div className="skeleton h-10 w-24 rounded-full"></div>

      {/* User info skeleton */}
      <div className="flex items-center">
        <div className="skeleton w-10 h-10 rounded-full"></div>
        <div className="ml-2">
          <div className="skeleton h-4 w-24"></div>
        </div>
      </div>
    </div>
  );
}

export default UserInfo;
