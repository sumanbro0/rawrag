"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Paperclip, FileText } from "lucide-react";
import { toast } from "sonner";
import { useGetMessagesQuery, useSendMessageMutation } from "@/api";
import { Button } from "./ui/button";
import { Spinner } from "./ui/spinner";

export function ChatInterface({ chatId }: { chatId: string }) {
  const [input, setInput] = useState("");
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { data: messages, isLoading } = useGetMessagesQuery(chatId);

  const { mutate: sendMessage, isPending: isSending } =
    useSendMessageMutation();
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  function handleReset() {
    setInput("");
    setUploadedFile(null);
    scrollToBottom();
  }

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setUploadedFile(file);
    }
  };

  const handleSend = () => {
    if (isSending) {
      toast.error("Message is being sent...");
      return;
    }
    handleReset();

    sendMessage(
      {
        chat_id: chatId,
        message: input,
        file: uploadedFile,
      },
      {
        onSuccess: () => {
          toast.success("Message sent successfully");
        },
        onError: (e, variables) => {
          console.log(e);
          setInput(variables.message);
          setUploadedFile(variables.file);
          scrollToBottom();
          toast.error("Failed to send message");
        },
      },
    );
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <div className="flex-1 overflow-y-auto px-6 py-4">
        {messages?.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center">
            {isLoading ? (
              <Spinner className="w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center mb-4" />
            ) : (
              <>
                <div className="w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center mb-4">
                  <FileText className="w-8 h-8 text-gray-500" />
                </div>
                <h2 className="text-2xl font-semibold text-gray-900 mb-2">
                  Upload a document to get started
                </h2>
                <p className="text-gray-600 max-w-md">
                  Upload a PDF, Word document, or text file and start asking
                  questions about it.
                </p>
              </>
            )}
          </div>
        )}

        <div className="max-w-3xl mx-auto space-y-4">
          {messages?.map((message) => (
            <div
              key={message.id}
              className={`flex ${
                message.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                  message.role === "user"
                    ? "bg-primary/90 text-white"
                    : "bg-white text-gray-900 border border-gray-200"
                }`}
              >
                {message.file_name && (
                  <div className="mb-3 flex items-center gap-3 bg-blue-50 border border-gray-200 rounded-lg px-4 py-3">
                    <FileText className="w-5 h-5 text-primary shrink-0" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {message.file_name}
                      </p>
                    </div>
                  </div>
                )}
                <p className="whitespace-pre-wrap wrap-break-words">
                  {message.content}
                </p>
                <span
                  className={`text-xs mt-1 block ${
                    message.role === "user" ? "text-blue-100" : "text-gray-500"
                  }`}
                >
                  {new Date(message.created_at).toLocaleTimeString([], {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </span>
              </div>
            </div>
          ))}

          {isSending && (
            <div className="flex justify-start">
              <div className="bg-white text-gray-900 border border-gray-200 rounded-2xl px-4 py-3">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100" />
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200" />
                </div>
              </div>
            </div>
          )}
        </div>
        <div ref={messagesEndRef} />
      </div>

      <div className="bg-white border-t border-gray-200 px-6 py-4">
        <div className="max-w-5xl mx-auto">
          {uploadedFile && (
            <div className="mb-3 flex items-center gap-3 bg-blue-50 border border-gray-200 rounded-lg px-4 py-3">
              <FileText className="w-5 h-5 text-primary shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {uploadedFile.name}
                </p>
              </div>
            </div>
          )}

          <div className="flex items-center gap-3">
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileUpload}
              multiple={false}
              className="hidden"
              accept=".pdf,.txt,.md"
            />
            <Button
              onClick={() => fileInputRef.current?.click()}
              disabled={isSending}
              className="shrink-0 w-11 h-11 flex items-center justify-center rounded-lg border border-gray-300 hover:bg-gray-50 transition-colors"
              title="Upload document"
              variant={"outline"}
            >
              <Paperclip className="w-5 h-5 text-gray-600" />
            </Button>

            <div className="flex-1 relative">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyPress}
                placeholder="Ask a question about your document..."
                rows={1}
                className="w-full px-4 py-3 pr-12 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent resize-none field-sizing-content"
                style={{ minHeight: "44px", maxHeight: "120px" }}
              />
            </div>

            <Button
              onClick={handleSend}
              disabled={(!input.trim() && !uploadedFile) || isLoading}
              className="shrink-0 w-11 h-11 flex items-center justify-center rounded-lg bg-primary hover:bg-primary disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              variant={"outline"}
            >
              {isSending ? (
                <Spinner className="w-5 h-5 text-white" />
              ) : (
                <Send className="w-5 h-5 text-white" />
              )}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
