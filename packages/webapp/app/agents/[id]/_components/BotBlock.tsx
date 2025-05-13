import { getBotUsername } from "@/components/agents/utils";
import { TgAgent } from "@viralink-ai/sdk";
import { useRouter } from "next/navigation";
import { FiCpu } from "react-icons/fi";

export default function BotBlock({ agent }: { agent: TgAgent }) {
  const router = useRouter();

  return (
    <>
      <h2 className="text-lg font-semibold mb-4 flex items-center">
        <FiCpu className="mr-2 text-primary" /> Bot Connection
      </h2>

      {agent.status === "waiting_bot_attach" && (
        <div className="text-center py-4">
          <p className="mb-4">This channel is not connected to a bot</p>
          <button
            onClick={() => router.push(`/add-channel/${agent.id}/select-bot`)}
            className="btn btn-primary"
          >
            Connect a Bot
          </button>
        </div>
      )}

      <BotInfo agent={agent} />
    </>
  );
}

function BotInfo({ agent }: { agent: TgAgent }) {
  const router = useRouter();

  if (["initial", "waiting_bot_attach"].includes(agent.status)) {
    return null;
  }

  return (
    <div>
      <div className="flex items-center mb-4">
        <div className="w-12 h-12 bg-base-300 rounded-md flex items-center justify-center text-lg mr-3">
          🤖
        </div>
        <div>
          <h3 className="font-medium">
            {agent.user_bot?.metadata_?.first_name}
          </h3>
          <p className="text-sm opacity-70">{getBotUsername(agent)}</p>
        </div>
        <button
          onClick={() => router.push(`/add-channel/${agent.id}/select-bot`)}
          className="btn btn-sm btn-outline ml-auto"
        >
          Change Bot
        </button>
      </div>
      {/*
      {agent.status !== "waiting_bot_access" && agent.bot_permissions && (
        <div className="mb-4">
          <h4 className="font-medium mb-2">Bot Permissions:</h4>
          <div className="flex flex-wrap gap-2">
            {channel.permissions.canPublish && (
              <div className="badge badge-outline gap-1">
                <FiCheckCircle className="text-success" />
                Can publish posts
              </div>
            )}
            {channel.permissions.canEdit && (
              <div className="badge badge-outline gap-1">
                <FiCheckCircle className="text-success" />
                Can edit posts
              </div>
            )}
            {channel.permissions.canDelete && (
              <div className="badge badge-outline gap-1">
                <FiCheckCircle className="text-success" />
                Can delete posts
              </div>
            )}
            {!channel.permissions.canPublish && (
              <div className="badge badge-outline gap-1">
                <FiAlertCircle className="text-error" />
                Cannot publish posts
              </div>
            )}
          </div>
        </div>
      )}
      */}

      <div className="form-control">
        <label className="cursor-pointer label justify-start gap-3">
          <input
            type="checkbox"
            className="toggle toggle-primary"
            checked={false}
            disabled={true}
          />
          <span className="label-text">Auto-publish content (soon)</span>
        </label>
        <p className="text-xs opacity-70 ml-12">
          {false
            ? "Content will be automatically published without your approval"
            : "You will need to approve content before it's published"}
        </p>
      </div>
    </div>
  );
}
