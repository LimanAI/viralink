"use client";

import { useTranslation } from "@/i18n/client";
import { Language } from "@/i18n/conf";
import { TgAgent } from "@viralink-ai/sdk";
import { useParams, useRouter } from "next/navigation";

export default function ContentBlock({
  agent,
  className,
}: {
  agent: TgAgent;
  className?: string;
}) {
  const { lang } = useParams<{ lang: Language }>();
  const { t } = useTranslation(lang, "app", {
    keyPrefix: "agents._components.ContentBlock",
  });
  const router = useRouter();
  const content_description = agent.channel_profile?.content_description;

  return (
    <div className={className}>
      <h3 className="font-medium mb-2">{t("title")}</h3>
      <p className="whitespace-pre-wrap text-sm opacity-80">
        {content_description
          ? content_description
          : t("empty_content_description")}
      </p>
      <button
        onClick={() => router.push(`/add-channel/${agent.id}/describe-content`)}
        className="btn btn-sm btn-outline my-2 w-full"
      >
        {t("button.edit_content_description")}
      </button>
    </div>
  );
}
