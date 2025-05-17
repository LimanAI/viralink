"use client";

import { useTranslation } from "@/i18n/client";
import { Language } from "@/i18n/conf";
import { TgAgent } from "@viralink-ai/sdk";
import { useParams, useRouter } from "next/navigation";

export default function PersonaBlock({
  agent,
  className,
}: {
  agent: TgAgent;
  className?: string;
}) {
  const { lang } = useParams<{ lang: Language }>();
  const { t } = useTranslation(lang, "app", {
    keyPrefix: "agents._components.PersonaBlock",
  });
  const router = useRouter();
  const persona_description = agent.channel_profile?.persona_description;

  return (
    <div className={className}>
      <h3 className="font-medium mb-2">{t("title")}</h3>
      <p className="whitespace-pre-wrap text-sm opacity-80">
        {persona_description || t("empty_persona_description")}
      </p>
      <button
        onClick={() => router.push(`/add-channel/${agent.id}/describe-persona`)}
        className="btn btn-sm btn-outline my-2 w-full"
      >
        {t("button.edit_persona_description")}
      </button>
      <div>
        {agent.channel_profile_generated && (
          <>
            <h3 className="font-medium mb-2 mt-4">
              {t("collected_info_title")}
            </h3>
            <p className="whitespace-pre-wrap text-xs opacity-80">
              {agent.channel_profile_generated}
            </p>
          </>
        )}
      </div>
    </div>
  );
}
