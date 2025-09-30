import { useState } from 'react'
import { Toaster } from 'react-hot-toast'
import { SessionList } from '@/components/session/SessionList'
import { ChatInterface } from '@/components/chat/ChatInterface'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Button } from '@/components/ui/button'
import { ThemeToggle } from '@/components/theme/ThemeToggle'
import { useCreateSession } from '@/hooks/api/useSessions'
import { Plus } from 'lucide-react'

export function MainLayout() {
  const [selectedSessionId, setSelectedSessionId] = useState<string | null>(null)
  const createSession = useCreateSession()

  const handleCreateSession = async () => {
    const session = await createSession.mutateAsync({
      agentId: 'default',
    })
    setSelectedSessionId(session.id)
  }

  return (
    <>
      <Toaster position="top-right" />
      <div className="h-screen flex flex-col">
        {/* Header */}
        <header className="border-b bg-card px-6 py-3 flex items-center justify-between">
          <h1 className="text-xl font-semibold">ADK GUI</h1>
          <ThemeToggle />
        </header>

        {/* Main Content Area */}
        <div className="flex-1 flex overflow-hidden">
          {/* Sidebar */}
          <div className="w-80 border-r bg-card flex flex-col">
            <div className="p-4 border-b">
              <Button
                onClick={handleCreateSession}
                className="w-full"
                disabled={createSession.isPending}
              >
                <Plus className="h-4 w-4 mr-2" />
                New Session
              </Button>
            </div>
        <ScrollArea className="flex-1">
          <SessionList
            onSelectSession={setSelectedSessionId}
            selectedSessionId={selectedSessionId || undefined}
          />
            </ScrollArea>
          </div>

          {/* Main Content */}
          <div className="flex-1 flex flex-col">
            {selectedSessionId ? (
              <ChatInterface sessionId={selectedSessionId} />
            ) : (
              <div className="flex-1 flex items-center justify-center text-muted-foreground">
                Select a session or create a new one to get started
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  )
}