"use client";

import { LuCheck } from "react-icons/lu";
import { PiTelegramLogo } from "react-icons/pi";
import { useQuery } from "@tanstack/react-query";
import TGAccount from "./tg/_components/TGAccount";

import { tgAccountsList } from "@/api";

export default function Admin() {
  const { isError, data, error } = useQuery({
    queryKey: ["/admin/tg/accounts"],
    retry: false,
    queryFn: async () => {
      const { data } = await tgAccountsList({
        throwOnError: true,
      });
      return data;
    },
  });

  if (isError) {
    return (
      <div>
        <div className="bg-base-100 p-6 rounded-lg shadow">
          <h2 className="font-bold text-lg">Telegram Accounts</h2>
          <p className="text-base-content/50">
            These Telegram accounts are used for connecting to telgram channels and fetching posts
          </p>

          <div className="mt-6 flex gap-6 flex-wrap">
            <div className="alert alert-error alert-soft">Failed to load telegram accounts {error.message}</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="bg-base-100 p-6 rounded-lg shadow">
        <h2 className="font-bold text-lg">Telegram Accounts</h2>
        <p className="text-base-content/50">
          These Telegram accounts are used for connecting to telgram channels and fetching posts
        </p>

        <div className="my-6 flex gap-6 flex-wrap">
          {data?.map((account) => <TGAccount key={account.id} {...account} />)}
        </div>
        <div className="card w-96 bg-base-200 shadow-sm">
          <div className="card-body">
            <div className="flex justify-between">
              <h2 className="text-2xl font-bold">New Account</h2>
              <span className="text-xl">
                <PiTelegramLogo className="size-6" />
              </span>
            </div>
            <ul className="mt-6 flex flex-col gap-2 text-xs">
              <li>
                <LuCheck className="size-4 mr-2 inline-block text-success" />
                <span>Regular telegram user</span>
              </li>
              <li>
                <LuCheck className="size-4 mr-2 inline-block text-success" />
                <span>Allows to join to any channel</span>
              </li>
              <li>
                <LuCheck className="size-4 mr-2 inline-block text-success" />
                <span>Retrieves new posts</span>
              </li>
              <li>
                <LuCheck className="size-4 mr-2 inline-block text-success" />
                <span>Requires full access</span>
              </li>
              <li className="opacity-50">
                <LuCheck className="size-4 mr-2 inline-block text-base-content/50" />
                <span className="line-through">Publish posts or messages</span>
              </li>
            </ul>
            <div className="mt-6">
              <a href="/admin/tg/add-account" className="btn btn-primary btn-block">
                Add new account
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
