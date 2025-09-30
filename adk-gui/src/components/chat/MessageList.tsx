import { useEffect, useRef } from 'react'
import type { Event } from '@/types/adk'
import { formatDate } from '@/lib/utils'
import { User, Bot, MessageSquare } from 'lucide-react'
import { EmptyState } from '@/components/ui/empty-state'
import { Skeleton } from '@/components/ui/loading'

interface MessageListProps {
  events: Event[]
  isLoading?: boolean
}

export function MessageList({ events, isLoading = false }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [events])

  if (isLoading) {
    return (
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="flex gap-3">
            <Skeleton className="w-8 h-8 rounded-full" />
            <div className="flex-1 space-y-2">
              <Skeleton className="h-4 w-3/4" />
              <Skeleton className="h-4 w-1/2" />
            </div>
          </div>
        ))}
      </div>
    )
  }

  if (events.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <EmptyState
          icon={MessageSquare}
          title="No messages yet"
          description="Start a conversation by sending a message below"
        />
      </div>
    )
  }

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {events.map((event) => (
        <div
          key={event.id}
          className={`flex gap-3 animate-in slide-in-from-bottom-2 ${
            event.role === 'user' ? 'justify-end' : 'justify-start'
          }`}
        >
          {event.role === 'agent' && (
            <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center flex-shrink-0 transition-all">
              <Bot className="h-4 w-4 text-primary-foreground" />
            </div>
          )}
          <div
            className={`max-w-[70%] rounded-lg p-3 transition-all ${
              event.role === 'user'
                ? 'bg-primary text-primary-foreground shadow-sm'
                : 'bg-muted shadow-sm'
            }`}
          >
            <div className="text-sm whitespace-pre-wrap break-words">
              {event.content}
            </div>
            <div
              className={`text-xs mt-1 ${
                event.role === 'user'
                  ? 'text-primary-foreground/70'
                  : 'text-muted-foreground'
              }`}
            >
              {formatDate(event.timestamp)}
            </div>
          </div>
          {event.role === 'user' && (
            <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center flex-shrink-0 transition-all">
              <User className="h-4 w-4 text-secondary-foreground" />
            </div>
          )}
        </div>
      ))}
      <div ref={bottomRef} />
    </div>
  )
}