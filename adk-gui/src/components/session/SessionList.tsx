import { useSessions, useDeleteSession } from '@/hooks/api/useSessions'
import { formatDate } from '@/lib/utils'
import { Trash2, MessageSquare, FolderOpen } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { EmptyState } from '@/components/ui/empty-state'
import { Skeleton } from '@/components/ui/loading'

interface SessionListProps {
  onSelectSession: (sessionId: string) => void
  selectedSessionId?: string
}

export function SessionList({ onSelectSession, selectedSessionId }: SessionListProps) {
  const { data: sessions, isLoading, error } = useSessions()
  const deleteSession = useDeleteSession()

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation()
    if (confirm('Are you sure you want to delete this session?')) {
      await deleteSession.mutateAsync(id)
    }
  }

  if (isLoading) {
    return (
      <div className="space-y-2 p-4">
        {[...Array(5)].map((_, i) => (
          <Card key={i} className="p-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 flex-1">
                <Skeleton className="h-4 w-4" />
                <Skeleton className="h-4 w-24" />
              </div>
              <Skeleton className="h-8 w-8" />
            </div>
            <Skeleton className="h-3 w-32 mt-2" />
          </Card>
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-4">
        <EmptyState
          icon={MessageSquare}
          title="Error loading sessions"
          description="There was a problem loading your sessions. Please try again."
        />
      </div>
    )
  }

  if (!sessions?.length) {
    return (
      <div className="p-4 h-full flex items-center justify-center">
        <EmptyState
          icon={FolderOpen}
          title="No sessions yet"
          description="Create a new session to get started with your AI assistant"
        />
      </div>
    )
  }

  return (
    <div className="space-y-2 p-4">
      {sessions.map((session) => {
        const isSelected = selectedSessionId === session.id
        
        return (
          <Card
            key={session.id}
            onClick={() => onSelectSession(session.id)}
            hoverable
            className={`p-3 cursor-pointer transition-all ${
              isSelected
                ? 'bg-primary text-primary-foreground ring-2 ring-primary'
                : ''
            }`}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 flex-1 min-w-0">
                <MessageSquare className="h-4 w-4 flex-shrink-0" />
                <span className="font-medium truncate">
                  Session {session.id.slice(0, 8)}
                </span>
                <Badge 
                  size="sm"
                  variant={isSelected ? 'secondary' : 'default'}
                  className="ml-auto flex-shrink-0"
                >
                  Active
                </Badge>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={(e) => handleDelete(session.id, e)}
                className={`ml-2 flex-shrink-0 ${
                  isSelected 
                    ? 'hover:bg-primary-foreground/10 text-primary-foreground' 
                    : ''
                }`}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
            <div
              className={`text-xs mt-1 ${
                isSelected ? 'text-primary-foreground/70' : 'text-muted-foreground'
              }`}
            >
              {formatDate(session.createdAt)}
            </div>
          </Card>
        )
      })}
    </div>
  )
}