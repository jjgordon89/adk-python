import type { TemplateMatch } from '@/types/safetyculture'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

interface TemplateMatchDisplayProps {
  matches: TemplateMatch[]
  onSelectTemplate: (match: TemplateMatch) => void
}

export function TemplateMatchDisplay({ matches, onSelectTemplate }: TemplateMatchDisplayProps) {
  const getConfidenceColor = (score: number): string => {
    if (score >= 0.8) return 'bg-green-500'
    if (score >= 0.6) return 'bg-yellow-500'
    return 'bg-red-500'
  }

  const getConfidenceLabel = (score: number): string => {
    if (score >= 0.8) return 'High Confidence'
    if (score >= 0.6) return 'Medium Confidence'
    return 'Low Confidence'
  }

  const getConfidenceIcon = (score: number): string => {
    if (score >= 0.8) return '✓'
    if (score < 0.6) return '⚠'
    return ''
  }

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Template Matches</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {matches.map((match) => (
          <Card
            key={match.templateId}
            className="cursor-pointer hover:shadow-lg transition-shadow"
            onClick={() => onSelectTemplate(match)}
          >
            <CardHeader>
              <div className="flex items-start justify-between">
                <CardTitle className="text-lg">{match.templateName}</CardTitle>
                <Badge variant="secondary">{match.assetType}</Badge>
              </div>
              <CardDescription className="mt-2">
                {match.reasoning}
              </CardDescription>
            </CardHeader>
            
            <CardContent>
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Match Confidence</span>
                  <span className="font-medium">
                    {getConfidenceIcon(match.matchScore)} {getConfidenceLabel(match.matchScore)}
                  </span>
                </div>
                
                <div className="w-full bg-muted rounded-full h-2.5">
                  <div
                    className={`h-2.5 rounded-full transition-all ${getConfidenceColor(match.matchScore)}`}
                    style={{ width: `${match.matchScore * 100}%` }}
                  />
                </div>
                
                <div className="text-right text-sm text-muted-foreground">
                  {(match.matchScore * 100).toFixed(0)}% match
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {matches.length === 0 && (
        <div className="text-center py-8 text-muted-foreground">
          No template matches found
        </div>
      )}
    </div>
  )
}