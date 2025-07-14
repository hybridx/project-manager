// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  message: string;
  data?: T;
  error?: string;
}

// Document Processing Types
export interface DocumentProcessingRequest {
  content: string;
  document_name: string;
  document_type: string;
  project_id?: string;
  additional_context?: string;
}

export interface DocumentProcessingResponse {
  success: boolean;
  message: string;
  document_id: string;
  artifacts?: ExtractedArtifacts;
  processing_time: number;
  metadata?: Record<string, any>;
}

// Project Artifacts Types
export interface ExtractedArtifacts {
  epics: Epic[];
  user_stories: UserStory[];
  contributors: string[];
  project_summary: string;
  estimated_duration?: string;
  key_features: string[];
  technical_requirements: string[];
  risks: string[];
  dependencies: string[];
}

export interface Epic {
  id?: string;
  title: string;
  description: string;
  priority: Priority;
  acceptance_criteria: string;
  estimated_story_points: number;
  user_stories: UserStory[];
}

export interface UserStory {
  id?: string;
  title: string;
  description: string;
  priority: Priority;
  story_points: number;
  acceptance_criteria: AcceptanceCriteria[];
  epic_id?: string;
  status: StoryStatus;
  estimated_effort?: string;
}

export interface AcceptanceCriteria {
  scenario: string;
  steps: string[];
}

export interface StoryPointEstimate {
  story_points: number;
  confidence: number;
  reasoning: string;
  factors_considered: string[];
  estimation_method: string;
}

// Enums
export enum Priority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical'
}

export enum StoryStatus {
  BACKLOG = 'backlog',
  IN_PROGRESS = 'in_progress',
  REVIEW = 'review',
  DONE = 'done',
  DRAFT = 'draft'
}

export enum DocumentType {
  PRD = 'prd',
  RFC = 'rfc',
  REQUIREMENTS = 'requirements',
  FEATURE_SPEC = 'feature_spec',
  MARKDOWN = 'markdown',
  TEXT = 'text',
  UNKNOWN = 'unknown'
}

// UI State Types
export interface ProcessingState {
  isProcessing: boolean;
  progress: number;
  currentStep: string;
  error?: string;
}

export interface FileUpload {
  file: File;
  progress: number;
  status: 'pending' | 'uploading' | 'processing' | 'complete' | 'error';
  result?: DocumentProcessingResponse;
  error?: string;
}

// Project Management Types
export interface Project {
  id: string;
  name: string;
  description: string;
  created_at: string;
  updated_at: string;
  status: ProjectStatus;
  team_members: string[];
  jira_project_key?: string;
  documents: Document[];
  settings: ProjectSettings;
}

export interface Document {
  id: string;
  name: string;
  type: DocumentType;
  content: string;
  uploaded_at: string;
  processed_at?: string;
  status: DocumentStatus;
  artifacts?: ExtractedArtifacts;
  project_id: string;
}

export interface ProjectSettings {
  auto_sync_jira: boolean;
  default_priority: Priority;
  story_point_scale: number[];
  team_members: string[];
  notification_preferences: NotificationPreferences;
}

export interface NotificationPreferences {
  email_on_processing_complete: boolean;
  slack_webhook_url?: string;
  jira_notifications: boolean;
}

export enum ProjectStatus {
  ACTIVE = 'active',
  PLANNING = 'planning',
  ON_HOLD = 'on_hold',
  COMPLETED = 'completed',
  ARCHIVED = 'archived'
}

export enum DocumentStatus {
  UPLOADED = 'uploaded',
  PROCESSING = 'processing',
  PROCESSED = 'processed',
  ERROR = 'error'
}

// Dashboard Types
export interface DashboardStats {
  total_projects: number;
  total_documents: number;
  total_epics: number;
  total_user_stories: number;
  processing_time_avg: number;
  recent_activity: ActivityItem[];
}

export interface ActivityItem {
  id: string;
  type: 'document_processed' | 'project_created' | 'epic_generated' | 'story_created';
  title: string;
  description: string;
  timestamp: string;
  project_id?: string;
  document_id?: string;
}

// Chart Data Types
export interface ChartData {
  labels: string[];
  datasets: ChartDataset[];
}

export interface ChartDataset {
  label: string;
  data: number[];
  backgroundColor?: string | string[];
  borderColor?: string;
  borderWidth?: number;
}

// Form Types
export interface CreateProjectForm {
  name: string;
  description: string;
  jira_project_key?: string;
  team_members: string[];
  settings: Partial<ProjectSettings>;
}

export interface DocumentUploadForm {
  files: FileList;
  project_id: string;
  document_type: DocumentType;
  additional_context?: string;
}

// Hook Types
export interface UseProcessingReturn {
  processDocument: (request: DocumentProcessingRequest) => Promise<DocumentProcessingResponse>;
  uploadDocument: (formData: FormData) => Promise<DocumentProcessingResponse>;
  generateAcceptanceCriteria: (title: string, description: string) => Promise<AcceptanceCriteria[]>;
  estimateStoryPoints: (title: string, description: string, criteria: string[]) => Promise<StoryPointEstimate>;
  isLoading: boolean;
  error: string | null;
}

// Store Types
export interface AppStore {
  // Projects
  projects: Project[];
  currentProject: Project | null;
  setCurrentProject: (project: Project | null) => void;
  addProject: (project: Project) => void;
  updateProject: (id: string, updates: Partial<Project>) => void;
  deleteProject: (id: string) => void;

  // Documents
  documents: Document[];
  addDocument: (document: Document) => void;
  updateDocument: (id: string, updates: Partial<Document>) => void;
  deleteDocument: (id: string) => void;

  // Processing
  processingState: ProcessingState;
  setProcessingState: (state: Partial<ProcessingState>) => void;

  // UI State
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
  theme: 'light' | 'dark';
  setTheme: (theme: 'light' | 'dark') => void;
} 