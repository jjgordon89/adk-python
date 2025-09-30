import { useSessionEvents } from '@/hooks/api/useSessions'
import { useAgentInvoke } from '@/hooks/api/useAgentInvoke'
import { MessageList } from './MessageList'
import { MessageInput } from './MessageInput'

interface ChatInterfaceProps {
  sessionId: string
}

export function ChatInterface({ sessionId }: ChatInterfaceProps) {
  const { data: events, isLoading } = useSessionEvents(sessionId)
  const agentInvoke = useAgentInvoke()

  const handleSendMessage = async (message: string) => {
    await agentInvoke.mutateAsync({
      sessionId,
      message,
      streaming: false,
    })
  }

  if (isLoading) {
    return <div className="flex items-center justify-center h-full">Loading messages...</div>
  }

  return (
    <div className="flex flex-col h-full">
      <MessageList events={events || []} />
      <MessageInput
        onSend={handleSendMessage}
        disabled={agentInvoke.isPending}
      />
    </div>
  )
}