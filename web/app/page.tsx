import StartNewChat from "@/components/start-new-chat";
import { FileText } from "lucide-react";

export default function Home() {
  return (
    <div className="flex items-center justify-center h-full min-h-screen w-full bg-gray-50">
      <div className="flex flex-col justify-center items-center gap-2 bg-background p-4 rounded-lg border-2">
        <div className="w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center mb-4">
          <FileText className="w-8 h-8 text-gray-500" />
        </div>
        <p className="text-gray-600 max-w-md text-center">
          Upload a PDF, Word document, or text file and start asking questions
          about it.
        </p>
        <StartNewChat />
      </div>
    </div>
  );
}
