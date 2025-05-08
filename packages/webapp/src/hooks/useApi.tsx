"use client";

import { settings } from "@/conf";
import { WebAppContext } from "@/providers/WebAppProvider";
import { client } from "@viralink-ai/sdk";
import { useContext, useMemo } from "react";

export function useApi() {
  const webApp = useContext(WebAppContext);

  return useMemo(() => {
    if (!webApp?.initData) {
      return null;
    }

    client.setConfig({
      baseUrl: settings.API_URL,
      headers: {
        "X-Telegram-Auth": webApp.initData,
      },
    });
    console.log("API_URL", settings.API_URL);
    return client;
  }, [webApp]);
}
