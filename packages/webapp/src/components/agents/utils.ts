import { TgAgent } from "@viralink-ai/sdk";

export const getBotUsername = (agent?: TgAgent): string => {
  const botUsername = agent?.user_bot?.metadata_?.username;
  return botUsername ? `@${botUsername}` : "";
};

export const getChannelUsername = (agent?: TgAgent): string => {
  const channelUsername = agent?.channel_username;
  return channelUsername ? `@${channelUsername}` : "";
};
