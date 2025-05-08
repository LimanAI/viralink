"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";

type TUser = {
  first_name: string;
  last_name?: string;
  username?: string;
  premium?: boolean;
};

function getCurrentUser(): TUser {
  return {
    first_name: "John",
    last_name: "Doe",
    username: "johndoe",
    premium: true,
  };
}

const UserInfo = () => {
  const [user, setUser] = useState<TUser | null>(null);

  useEffect(() => {
    const userInfo = getCurrentUser();
    setUser(userInfo);
  }, []);

  if (!user) {
    return (
      <div className="flex items-center p-4 bg-base-200 rounded-lg animate-pulse">
        <div className="w-12 h-12 bg-base-300 rounded-full"></div>
        <div className="ml-3 space-y-2">
          <div className="h-4 w-24 bg-base-300 rounded"></div>
          <div className="h-3 w-16 bg-base-300 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 5 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex items-center p-4 bg-base-200 rounded-lg"
    >
      <div className="w-12 h-12 bg-primary text-primary-content rounded-full flex items-center justify-center text-lg font-semibold">
        {user.first_name ? user.first_name.charAt(0) : "U"}
      </div>

      <div className="ml-3">
        <h3 className="font-semibold">
          {user.first_name} {user.last_name || ""}
        </h3>
        {user.username && (
          <p className="text-sm opacity-80">@{user.username}</p>
        )}
      </div>

      {user.premium && (
        <div className="ml-auto">
          <span className="badge badge-primary badge-sm">Premium</span>
        </div>
      )}
    </motion.div>
  );
};

export default UserInfo;
