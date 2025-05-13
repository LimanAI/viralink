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
  const content_description = agent.channel_profile?.content_description;

  return (
    <div className={className}>
      <h3 className="font-medium mb-2">Content Description</h3>
      <p className="whitespace-pre-wrap text-sm opacity-80">
        {content_description
          ? content_description
          : "This agent does not have a content description."}
      </p>
      <button
        onClick={() => router.push(`/add-channel/${agent.id}/describe-content`)}
        className="btn btn-sm btn-outline my-2 w-full"
      >
        Edit Content Preferences
      </button>
    </div>
  );
}
