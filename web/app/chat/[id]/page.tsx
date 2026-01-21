import { ChatInterface } from "@/components/chat-interface";
import StartNewChat from "@/components/start-new-chat";

export default async function ChatPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return (
    <div className="relative">
      <div className="fixed top-4  right-26">
        <StartNewChat />
      </div>

      <ChatInterface chatId={id} />
    </div>
  );
}
