import { TgAgent } from "@viralink-ai/sdk";

export default function PersonaBlock({
  agent,
  className,
}: {
  agent: TgAgent;
  className?: string;
}) {
  if (!agent.channel_profile?.persona_description) {
    return (
      <div className={className}>
        <h3 className="font-medium mb-2">Content Persona</h3>
        <p className="text-sm opacity-80">
          This agent does not have a content persona set.
        </p>
      </div>
    );
  }

  return (
    <div className={className}>
      <h3 className="font-medium mb-2">Content Persona:</h3>
      <div>{agent.channel_profile?.persona_description}</div>
      <button onClick={() => {}} className="btn btn-sm btn-outline">
        Edit Persona Settings
      </button>
    </div>
  );
}
