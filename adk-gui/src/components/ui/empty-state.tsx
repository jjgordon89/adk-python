import * as React from "react"
import type { LucideIcon } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"

export interface EmptyStateProps {
  /**
   * Icon to display at the top of the empty state
   */
  icon?: LucideIcon
  /**
   * Main title text
   */
  title: string
  /**
   * Description text below the title
   */
  description?: string
  /**
   * Optional action button
   */
  action?: {
    label: string
    onClick: () => void
  }
  /**
   * Additional CSS classes
   */
  className?: string
}

/**
 * EmptyState component displays a centered message when no data is available.
 * Includes optional icon, title, description, and action button.
 */
export function EmptyState({
  icon: Icon,
  title,
  description,
  action,
  className,
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center p-8 text-center",
        className
      )}
    >
      {Icon && (
        <div className="mb-4 rounded-full bg-muted p-4">
          <Icon className="h-8 w-8 text-muted-foreground" aria-hidden="true" />
        </div>
      )}
      <h3 className="mb-2 text-lg font-semibold">{title}</h3>
      {description && (
        <p className="mb-6 text-sm text-muted-foreground max-w-md">
          {description}
        </p>
      )}
      {action && (
        <Button onClick={action.onClick} variant="default">
          {action.label}
        </Button>
      )}
    </div>
  )
}