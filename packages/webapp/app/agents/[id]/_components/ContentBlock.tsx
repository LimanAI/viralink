import { TgAgent } from "@viralink-ai/sdk";
import { useRouter } from "next/navigation";

export default function ContentBlock({
  agent,
  className,
}: {
  agent: TgAgent;
  className?: string;
}) {
  const router = useRouter();

  if (!agent.channel_profile?.content_description) {
    return (
      <div className={className}>
        <h3 className="font-medium mb-2">Content Description</h3>
        <p className="text-sm opacity-80">
          This agent does not have a content description.
        </p>
      </div>
    );
  }

  return (
    <div className={className}>
      <h3 className="font-medium mb-2">Content Description:</h3>
      <div>{agent.channel_profile?.content_description}</div>
      <button
        onClick={() => router.push(`/add-channel/${agent.id}/describe-content`)}
        className="btn btn-sm btn-outline"
      >
        Edit Content Preferences
      </button>
    </div>
  );
}
