"use client";

import { Button } from "./ui/button";
import { toast } from "sonner";
import { createChat } from "@/client";
import { useRouter } from "next/navigation";
import { ArrowRight } from "lucide-react";

const StartNewChat = () => {
  const router = useRouter();
  return (
    <Button
      onClick={() => {
        toast.promise(createChat, {
          success: ({ data }) => {
            router.push(`/chat/${data?.data?.id}`);
            return "Created";
          },
          loading: "creating....",
          error: "Couldnot initiate chat...",
        });
      }}
      className="w-full mt-4 cursor-pointer"
    >
      Start New chat
      <ArrowRight />
    </Button>
  );
};

export default StartNewChat;
