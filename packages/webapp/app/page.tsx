import { AgentsList } from "@/components/agents/AgentsList";
import PageTransition from "@/components/PageTransition";
import UserInfo from "@/components/UserInfo";

export default function Home() {
  return (
    <PageTransition>
      <div className="container mx-auto max-w-md p-4">
        <h1 className="text-2xl font-bold mb-6">Your Channels</h1>
        <UserInfo />
        <AgentsList />
      </div>
    </PageTransition>
  );
}
