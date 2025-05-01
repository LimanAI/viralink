"use client";

import { LuCheck } from "react-icons/lu";
import { PiTelegramLogo } from "react-icons/pi";
import SystemAccount from "./tg/_components/SystemAccount";

const telegramAccounts = [
  {
    id: 1,
    handle: "@telegram_account_1",
    status: "active",
  },
  {
    id: 2,
    handle: "@telegram_account_2",
    status: "inactive",
  },
];

export default function Admin() {
  return (
    <div>
      <div className="bg-base-100 p-6 rounded-lg shadow">
        <h2 className="font-bold text-lg">Telegram Accounts</h2>
        <p className="text-base-content/50">
          These Telegram accounts are used for connecting to telgram channels and fetching posts
        </p>

        <div className="mt-6 flex gap-6 flex-wrap">
          {telegramAccounts.map((account) => (
            <SystemAccount key={account.id} {...account} />
          ))}

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
    </div>
  );
}
