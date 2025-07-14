import React, { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { 
  ArrowLeftIcon,
  PlusIcon,
  DocumentIcon,
  UsersIcon,
  ChartBarIcon,
  Cog6ToothIcon,
  FolderIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  EllipsisVerticalIcon
} from '@heroicons/react/24/outline'
import { Project, Epic, UserStory, Document, Priority, StoryStatus } from '@/types'

const mockProject: Project = {
  id: '1',
  name: 'E-commerce Platform',
  description: 'Building a modern e-commerce platform with AI-powered recommendations and seamless user experience',
  created_at: '2024-01-15T10:30:00Z',
  updated_at: '2024-01-20T14:22:00Z',
  status: 'active' as any,
  team_members: ['alice@company.com', 'bob@company.com', 'charlie@company.com'],
  jira_project_key: 'ECOM',
  documents: [
    {
      id: '1',
      name: 'Product Requirements Document',
      type: 'prd' as any,
      content: 'PRD content...',
      uploaded_at: '2024-01-15T10:30:00Z',
      processed_at: '2024-01-15T10:35:00Z',
      status: 'processed' as any,
      project_id: '1'
    },
    {
      id: '2',
      name: 'Technical Architecture',
      type: 'markdown' as any,
      content: 'Architecture content...',
      uploaded_at: '2024-01-16T09:20:00Z',
      processed_at: '2024-01-16T09:25:00Z',
      status: 'processed' as any,
      project_id: '1'
    }
  ],
  settings: {
    auto_sync_jira: true,
    default_priority: Priority.MEDIUM,
    story_point_scale: [1, 2, 3, 5, 8, 13, 21],
    team_members: ['alice@company.com', 'bob@company.com'],
    notification_preferences: {
      email_on_processing_complete: true,
      jira_notifications: true
    }
  }
}

const mockEpics: Epic[] = [
  {
    id: '1',
    title: 'User Authentication System',
    description: 'Implement secure user authentication with OAuth and multi-factor authentication',
    priority: Priority.HIGH,
    acceptance_criteria: 'Users can register, login, and reset passwords securely',
    estimated_story_points: 21,
    user_stories: [
      {
        id: '1',
        title: 'User Registration',
        description: 'As a new user, I want to create an account',
        priority: Priority.HIGH,
        story_points: 8,
        acceptance_criteria: [{
          scenario: 'Successful registration',
          steps: ['Given valid email and password', 'When user submits form', 'Then account is created']
        }],
        epic_id: '1',
        status: StoryStatus.DONE
      },
      {
        id: '2',
        title: 'User Login',
        description: 'As a user, I want to login to my account',
        priority: Priority.HIGH,
        story_points: 5,
        acceptance_criteria: [{
          scenario: 'Successful login',
          steps: ['Given valid credentials', 'When user logs in', 'Then user is authenticated']
        }],
        epic_id: '1',
        status: StoryStatus.IN_PROGRESS
      },
      {
        id: '3',
        title: 'Password Reset',
        description: 'As a user, I want to reset my password',
        priority: Priority.MEDIUM,
        story_points: 8,
        acceptance_criteria: [{
          scenario: 'Password reset',
          steps: ['Given forgotten password', 'When user requests reset', 'Then reset email is sent']
        }],
        epic_id: '1',
        status: StoryStatus.BACKLOG
      }
    ]
  },
  {
    id: '2',
    title: 'Product Catalog',
    description: 'Build a comprehensive product catalog with search and filtering capabilities',
    priority: Priority.MEDIUM,
    acceptance_criteria: 'Users can browse, search, and filter products effectively',
    estimated_story_points: 34,
    user_stories: [
      {
        id: '4',
        title: 'Product Listing',
        description: 'As a user, I want to view all products',
        priority: Priority.MEDIUM,
        story_points: 13,
        acceptance_criteria: [{
          scenario: 'Product listing',
          steps: ['Given products exist', 'When user visits catalog', 'Then products are displayed']
        }],
        epic_id: '2',
        status: StoryStatus.REVIEW
      },
      {
        id: '5',
        title: 'Product Search',
        description: 'As a user, I want to search for products',
        priority: Priority.MEDIUM,
        story_points: 21,
        acceptance_criteria: [{
          scenario: 'Product search',
          steps: ['Given search query', 'When user searches', 'Then relevant products are shown']
        }],
        epic_id: '2',
        status: StoryStatus.BACKLOG
      }
    ]
  }
]

export default function ProjectDetails() {
  const { id } = useParams<{ id: string }>()
  const [project, setProject] = useState<Project | null>(mockProject)
  const [epics, setEpics] = useState<Epic[]>(mockEpics)
  const [activeTab, setActiveTab] = useState<'overview' | 'epics' | 'stories' | 'documents' | 'team'>('overview')
  const [loading, setLoading] = useState(false)

  const allStories = epics.flatMap(epic => epic.user_stories)
  
  const getStatusColor = (status: StoryStatus) => {
    switch (status) {
      case StoryStatus.DONE:
        return 'bg-success-100 text-success-800'
      case StoryStatus.IN_PROGRESS:
        return 'bg-warning-100 text-warning-800'
      case StoryStatus.REVIEW:
        return 'bg-primary-100 text-primary-800'
      case StoryStatus.BACKLOG:
        return 'bg-gray-100 text-gray-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getPriorityColor = (priority: Priority) => {
    switch (priority) {
      case Priority.HIGH:
        return 'text-red-600'
      case Priority.MEDIUM:
        return 'text-yellow-600'
      case Priority.LOW:
        return 'text-green-600'
      default:
        return 'text-gray-600'
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  const getTotalStoryPoints = () => {
    return epics.reduce((total, epic) => total + epic.estimated_story_points, 0)
  }

  const getCompletedStoryPoints = () => {
    return allStories
      .filter(story => story.status === StoryStatus.DONE)
      .reduce((total, story) => total + story.story_points, 0)
  }

  const getProgressPercentage = () => {
    const total = getTotalStoryPoints()
    const completed = getCompletedStoryPoints()
    return total > 0 ? (completed / total) * 100 : 0
  }

  if (!project) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Project not found</h2>
          <p className="text-gray-600 mb-4">The project you're looking for doesn't exist.</p>
          <Link to="/projects" className="btn btn-primary">
            Back to Projects
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link 
            to="/projects" 
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeftIcon className="h-5 w-5 text-gray-500" />
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{project.name}</h1>
            <p className="text-gray-600">{project.description}</p>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <Link 
            to={`/projects/${project.id}/settings`}
            className="btn btn-secondary flex items-center space-x-2"
          >
            <Cog6ToothIcon className="h-4 w-4" />
            <span>Settings</span>
          </Link>
          <Link 
            to="/upload"
            className="btn btn-primary flex items-center space-x-2"
          >
            <PlusIcon className="h-4 w-4" />
            <span>Add Document</span>
          </Link>
        </div>
      </div>

      {/* Progress Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card">
          <div className="card-body">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Story Points</p>
                <p className="text-2xl font-bold text-gray-900">{getTotalStoryPoints()}</p>
              </div>
              <ChartBarIcon className="h-8 w-8 text-primary-600" />
            </div>
          </div>
        </div>
        
        <div className="card">
          <div className="card-body">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Completed</p>
                <p className="text-2xl font-bold text-success-600">{getCompletedStoryPoints()}</p>
              </div>
              <CheckCircleIcon className="h-8 w-8 text-success-600" />
            </div>
          </div>
        </div>
        
        <div className="card">
          <div className="card-body">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Progress</p>
                <p className="text-2xl font-bold text-primary-600">{Math.round(getProgressPercentage())}%</p>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                <div 
                  className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${getProgressPercentage()}%` }}
                />
              </div>
            </div>
          </div>
        </div>
        
        <div className="card">
          <div className="card-body">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Team Size</p>
                <p className="text-2xl font-bold text-gray-900">{project.team_members.length}</p>
              </div>
              <UsersIcon className="h-8 w-8 text-gray-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="card">
        <div className="card-header border-b-0">
          <nav className="flex space-x-8">
            {[
              { id: 'overview', label: 'Overview', icon: FolderIcon },
              { id: 'epics', label: 'Epics', icon: ChartBarIcon },
              { id: 'stories', label: 'Stories', icon: DocumentIcon },
              { id: 'documents', label: 'Documents', icon: DocumentIcon },
              { id: 'team', label: 'Team', icon: UsersIcon }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center space-x-2 px-3 py-2 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <tab.icon className="h-4 w-4" />
                <span>{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>

        <div className="card-body">
          {activeTab === 'overview' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Project Information</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Created</span>
                      <span className="text-gray-900">{formatDate(project.created_at)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Last Updated</span>
                      <span className="text-gray-900">{formatDate(project.updated_at)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Status</span>
                      <span className="text-gray-900 capitalize">{project.status}</span>
                    </div>
                    {project.jira_project_key && (
                      <div className="flex justify-between">
                        <span className="text-gray-600">Jira Project</span>
                        <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">
                          {project.jira_project_key}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
                  <div className="space-y-3">
                    {project.documents.slice(0, 3).map(doc => (
                      <div key={doc.id} className="flex items-center space-x-3">
                        <div className="p-2 bg-gray-100 rounded-lg">
                          <DocumentIcon className="h-4 w-4 text-gray-600" />
                        </div>
                        <div className="flex-1">
                          <p className="text-sm font-medium text-gray-900">{doc.name}</p>
                          <p className="text-xs text-gray-500">
                            Processed {formatDate(doc.processed_at || doc.uploaded_at)}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'epics' && (
            <div className="space-y-4">
              {epics.map(epic => (
                <motion.div
                  key={epic.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="border border-gray-200 rounded-lg p-4"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <h4 className="text-lg font-semibold text-gray-900">{epic.title}</h4>
                      <p className="text-gray-600 mt-1">{epic.description}</p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className={`text-sm font-medium ${getPriorityColor(epic.priority)}`}>
                        {epic.priority}
                      </span>
                      <span className="text-sm text-gray-500">
                        {epic.estimated_story_points} pts
                      </span>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <span className="text-sm text-gray-500">
                        {epic.user_stories.length} stories
                      </span>
                      <span className="text-sm text-gray-500">
                        {epic.user_stories.filter(s => s.status === StoryStatus.DONE).length} completed
                      </span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-32 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-primary-600 h-2 rounded-full"
                          style={{ 
                            width: `${(epic.user_stories.filter(s => s.status === StoryStatus.DONE).length / epic.user_stories.length) * 100}%` 
                          }}
                        />
                      </div>
                      <button className="p-1 hover:bg-gray-100 rounded-full">
                        <EllipsisVerticalIcon className="h-4 w-4 text-gray-400" />
                      </button>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          )}

          {activeTab === 'stories' && (
            <div className="space-y-4">
              {allStories.map(story => (
                <motion.div
                  key={story.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="border border-gray-200 rounded-lg p-4"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h4 className="text-lg font-semibold text-gray-900">{story.title}</h4>
                        <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(story.status)}`}>
                          {story.status}
                        </span>
                      </div>
                      <p className="text-gray-600 mb-3">{story.description}</p>
                      <div className="flex items-center space-x-4 text-sm text-gray-500">
                        <span className={`font-medium ${getPriorityColor(story.priority)}`}>
                          {story.priority}
                        </span>
                        <span>{story.story_points} pts</span>
                        <span>{story.acceptance_criteria.length} criteria</span>
                      </div>
                    </div>
                    <button className="p-1 hover:bg-gray-100 rounded-full">
                      <EllipsisVerticalIcon className="h-4 w-4 text-gray-400" />
                    </button>
                  </div>
                </motion.div>
              ))}
            </div>
          )}

          {activeTab === 'documents' && (
            <div className="space-y-4">
              {project.documents.map(doc => (
                <motion.div
                  key={doc.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="border border-gray-200 rounded-lg p-4"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="p-2 bg-gray-100 rounded-lg">
                        <DocumentIcon className="h-6 w-6 text-gray-600" />
                      </div>
                      <div>
                        <h4 className="text-lg font-semibold text-gray-900">{doc.name}</h4>
                        <p className="text-sm text-gray-500 capitalize">{doc.type}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-3">
                      <span className="text-sm text-gray-500">
                        {formatDate(doc.uploaded_at)}
                      </span>
                      <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                        doc.status === 'processed' ? 'bg-success-100 text-success-800' : 'bg-gray-100 text-gray-800'
                      }`}>
                        {doc.status}
                      </span>
                      <button className="p-1 hover:bg-gray-100 rounded-full">
                        <EllipsisVerticalIcon className="h-4 w-4 text-gray-400" />
                      </button>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          )}

          {activeTab === 'team' && (
            <div className="space-y-4">
              {project.team_members.map((member, index) => (
                <motion.div
                  key={member}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="border border-gray-200 rounded-lg p-4"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
                        <span className="text-primary-600 font-semibold">
                          {member.charAt(0).toUpperCase()}
                        </span>
                      </div>
                      <div>
                        <h4 className="text-lg font-semibold text-gray-900">{member}</h4>
                        <p className="text-sm text-gray-500">Team Member</p>
                      </div>
                    </div>
                    <button className="p-1 hover:bg-gray-100 rounded-full">
                      <EllipsisVerticalIcon className="h-4 w-4 text-gray-400" />
                    </button>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
} 