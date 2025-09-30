export interface Asset {
  id: string
  name: string
  type: string
  location: string
  siteId: string
  siteName: string
  metadata: Record<string, any>
  lastInspectionDate?: string
}

export interface TemplateMatch {
  templateId: string
  templateName: string
  assetType: string
  matchScore: number
  reasoning: string
}

export interface InspectionTemplate {
  id: string
  name: string
  description: string
  fields: InspectionField[]
}

export interface InspectionField {
  id: string
  type: 'text' | 'number' | 'date' | 'checkbox' | 'select' | 'media'
  label: string
  required: boolean
  options?: string[]
}

export interface Inspection {
  id: string
  templateId: string
  assetId: string
  status: 'draft' | 'completed' | 'submitted'
  responses: Record<string, any>
  createdAt: string
  updatedAt: string
  submittedAt?: string
}