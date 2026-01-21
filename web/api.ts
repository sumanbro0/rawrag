import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { getMessagesChatChatIdGet, MessageOut, sendChatMessage } from "./client"
import { getErrorMessage } from "./lib/utils"

export const useGetMessagesQuery = (chatId: string) => {
    return useQuery({
        queryKey: ["messages", chatId],
        queryFn: async () => {
            const res = await getMessagesChatChatIdGet({ path: { chat_id: chatId } })
            if (res.error) {
                throw new Error(getErrorMessage(res.error))
            }
            return res.data?.data ?? null
        }
    })
}

export const useSendMessageMutation = () => {
    const queryClient = useQueryClient()
    return useMutation({
        mutationFn: async ({ chat_id, message, file }: { chat_id: string, message: string, file: File | null }) => {
            const res = await sendChatMessage({ path: { chat_id }, body: { content: message, file } })
            if (res.error) {
                throw new Error(getErrorMessage(res.error))
            }

            return res.data.data ?? null
        },
        onMutate: (data) => {
            queryClient.setQueryData(["messages", data.chat_id], (old: MessageOut[] | null) => {
                const new_message: MessageOut = {
                    chat_id: data.chat_id,
                    content: data.message,
                    created_at: new Date().toLocaleString(),
                    role: "user",
                    file_name: data.file?.name ?? null,
                    id: Math.random(),
                }

                return [...(old ?? []), new_message]
            })
        },
        onSuccess: (_, variables) => {

            queryClient.invalidateQueries({
                queryKey: ["messages", variables.chat_id],
            })
        }
    })
}
