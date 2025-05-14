import { TgAgent } from "@viralink-ai/sdk";
import { useRouter } from "next/navigation";

export default function PersonaBlock({
  agent,
  className,
}: {
  agent: TgAgent;
  className?: string;
}) {
  const router = useRouter();
  const persona_description = agent.channel_profile?.persona_description;

  return (
    <div className={className}>
      <h3 className="font-medium mb-2">Content Persona:</h3>
      <p className="whitespace-pre-wrap text-sm opacity-80">
        {persona_description ||
          "This agent does not have a content persona set."}
      </p>
      <button
        onClick={() => router.push(`/add-channel/${agent.id}/describe-persona`)}
        className="btn btn-sm btn-outline my-2 w-full"
      >
        Edit Persona Settings
      </button>
      <div>
        {agent.channel_profile_generated && (
          <>
            <h3 className="font-medium mb-2 mt-4">Collected Info:</h3>
            <p className="whitespace-pre-wrap text-xs opacity-80">
              {agent.channel_profile_generated}
            </p>
          </>
        )}
      </div>
    </div>
  );
}
