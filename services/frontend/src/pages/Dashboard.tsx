import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { 
  ChartBarIcon,
  DocumentIcon,
  ClockIcon,
  UsersIcon,
  CheckCircleIcon,
  ArrowTrendingUpIcon,
  EyeIcon,
  PlusIcon,
  ArrowRightIcon,
  FolderIcon,
  ExclamationTriangleIcon,
  Cog6ToothIcon
} from '@heroicons/react/24/outline'

interface DashboardStats {
  totalProjects: number
  documentsProcessed: number
  epicsGenerated: number
  userStories: number
  averageProcessingTime: number
  activeUsers: number
}

interface RecentActivity {
  id: string
  type: 'document_processed' | 'project_created' | 'epic_generated' | 'story_created'
  title: string
  description: string
  timestamp: string
  projectName?: string
  status: 'success' | 'processing' | 'failed'
}

interface ProjectProgress {
  id: string
  name: string
  progress: number
  totalStories: number
  completedStories: number
  dueDate: string
  status: 'on_track' | 'at_risk' | 'delayed'
}

const mockStats: DashboardStats = {
  totalProjects: 12,
  documentsProcessed: 47,
  epicsGenerated: 89,
  userStories: 234,
  averageProcessingTime: 8.5,
  activeUsers: 6
}

const mockRecentActivity: RecentActivity[] = [
  {
    id: '1',
    type: 'document_processed',
    title: 'Product Requirements Document',
    description: 'Generated 8 epics and 25 user stories',
    timestamp: '2024-01-20T14:30:00Z',
    projectName: 'E-commerce Platform',
    status: 'success'
  },
  {
    id: '2',
    type: 'project_created',
    title: 'Mobile Banking App',
    description: 'New project created with initial setup',
    timestamp: '2024-01-20T12:15:00Z',
    status: 'success'
  },
  {
    id: '3',
    type: 'epic_generated',
    title: 'User Authentication System',
    description: 'Generated from technical specification',
    timestamp: '2024-01-20T11:45:00Z',
    projectName: 'Healthcare Platform',
    status: 'success'
  },
  {
    id: '4',
    type: 'document_processed',
    title: 'API Documentation',
    description: 'Processing failed due to format issues',
    timestamp: '2024-01-20T10:20:00Z',
    projectName: 'Analytics Dashboard',
    status: 'failed'
  },
  {
    id: '5',
    type: 'story_created',
    title: 'Payment Integration',
    description: 'Added to Product Catalog epic',
    timestamp: '2024-01-20T09:30:00Z',
    projectName: 'E-commerce Platform',
    status: 'success'
  }
]

const mockProjectProgress: ProjectProgress[] = [
  {
    id: '1',
    name: 'E-commerce Platform',
    progress: 75,
    totalStories: 32,
    completedStories: 24,
    dueDate: '2024-02-15',
    status: 'on_track'
  },
  {
    id: '2',
    name: 'Mobile Banking App',
    progress: 45,
    totalStories: 28,
    completedStories: 13,
    dueDate: '2024-02-28',
    status: 'at_risk'
  },
  {
    id: '3',
    name: 'Analytics Dashboard',
    progress: 90,
    totalStories: 18,
    completedStories: 16,
    dueDate: '2024-01-30',
    status: 'on_track'
  },
  {
    id: '4',
    name: 'Healthcare Platform',
    progress: 20,
    totalStories: 45,
    completedStories: 9,
    dueDate: '2024-03-15',
    status: 'delayed'
  }
]

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats>(mockStats)
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>(mockRecentActivity)
  const [projectProgress, setProjectProgress] = useState<ProjectProgress[]>(mockProjectProgress)
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d'>('30d')

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'document_processed':
        return DocumentIcon
      case 'project_created':
        return FolderIcon
      case 'epic_generated':
        return ChartBarIcon
      case 'story_created':
        return CheckCircleIcon
      default:
        return DocumentIcon
    }
  }

  const getActivityIconColor = (type: string) => {
    switch (type) {
      case 'document_processed':
        return 'bg-blue-100 text-blue-600'
      case 'project_created':
        return 'bg-green-100 text-green-600'
      case 'epic_generated':
        return 'bg-purple-100 text-purple-600'
      case 'story_created':
        return 'bg-yellow-100 text-yellow-600'
      default:
        return 'bg-gray-100 text-gray-600'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'on_track':
        return 'bg-green-100 text-green-800'
      case 'at_risk':
        return 'bg-yellow-100 text-yellow-800'
      case 'delayed':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffTime = Math.abs(now.getTime() - date.getTime())
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    
    if (diffDays === 0) {
      return 'Today'
    } else if (diffDays === 1) {
      return 'Yesterday'
    } else if (diffDays < 7) {
      return `${diffDays} days ago`
    } else {
      return date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric',
        year: diffDays > 365 ? 'numeric' : undefined
      })
    }
  }

  const formatRelativeTime = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffTime = Math.abs(now.getTime() - date.getTime())
    const diffHours = Math.floor(diffTime / (1000 * 60 * 60))
    const diffMinutes = Math.floor(diffTime / (1000 * 60))
    
    if (diffMinutes < 60) {
      return `${diffMinutes}m ago`
    } else if (diffHours < 24) {
      return `${diffHours}h ago`
    } else {
      return formatDate(dateString)
    }
  }

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Welcome back, John!</h1>
          <p className="text-gray-600 mt-2">Here's what's happening with your projects today.</p>
        </div>
        <div className="flex items-center space-x-3">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value as '7d' | '30d' | '90d')}
            className="px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
          </select>
          <Link 
            to="/upload" 
            className="btn btn-primary flex items-center space-x-2"
          >
            <PlusIcon className="h-4 w-4" />
            <span>Upload Document</span>
          </Link>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="card"
        >
          <div className="card-body">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Projects</p>
                <p className="text-2xl font-bold text-gray-900">{stats.totalProjects}</p>
                <p className="text-xs text-green-600 flex items-center mt-1">
                  <ArrowTrendingUpIcon className="h-3 w-3 mr-1" />
                  +2 this month
                </p>
              </div>
              <div className="p-3 bg-primary-100 rounded-full">
                <FolderIcon className="h-6 w-6 text-primary-600" />
              </div>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="card"
        >
          <div className="card-body">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Documents Processed</p>
                <p className="text-2xl font-bold text-success-600">{stats.documentsProcessed}</p>
                <p className="text-xs text-green-600 flex items-center mt-1">
                  <ArrowTrendingUpIcon className="h-3 w-3 mr-1" />
                  +5 this week
                </p>
              </div>
              <div className="p-3 bg-success-100 rounded-full">
                <DocumentIcon className="h-6 w-6 text-success-600" />
              </div>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="card"
        >
          <div className="card-body">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Epics Generated</p>
                <p className="text-2xl font-bold text-warning-600">{stats.epicsGenerated}</p>
                <p className="text-xs text-green-600 flex items-center mt-1">
                  <ArrowTrendingUpIcon className="h-3 w-3 mr-1" />
                  +12 this week
                </p>
              </div>
              <div className="p-3 bg-warning-100 rounded-full">
                <ChartBarIcon className="h-6 w-6 text-warning-600" />
              </div>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="card"
        >
          <div className="card-body">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">User Stories</p>
                <p className="text-2xl font-bold text-error-600">{stats.userStories}</p>
                <p className="text-xs text-green-600 flex items-center mt-1">
                  <ArrowTrendingUpIcon className="h-3 w-3 mr-1" />
                  +28 this week
                </p>
              </div>
              <div className="p-3 bg-error-100 rounded-full">
                <CheckCircleIcon className="h-6 w-6 text-error-600" />
              </div>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="card"
        >
          <div className="card-body">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Avg. Processing</p>
                <p className="text-2xl font-bold text-blue-600">{stats.averageProcessingTime}s</p>
                <p className="text-xs text-red-600 flex items-center mt-1">
                  <ExclamationTriangleIcon className="h-3 w-3 mr-1" />
                  +1.2s slower
                </p>
              </div>
              <div className="p-3 bg-blue-100 rounded-full">
                <ClockIcon className="h-6 w-6 text-blue-600" />
              </div>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="card"
        >
          <div className="card-body">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active Users</p>
                <p className="text-2xl font-bold text-purple-600">{stats.activeUsers}</p>
                <p className="text-xs text-gray-500 flex items-center mt-1">
                  <UsersIcon className="h-3 w-3 mr-1" />
                  Team members
                </p>
              </div>
              <div className="p-3 bg-purple-100 rounded-full">
                <UsersIcon className="h-6 w-6 text-purple-600" />
              </div>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Recent Activity */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="lg:col-span-2"
        >
          <div className="card">
            <div className="card-header">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold text-gray-900">Recent Activity</h2>
                <Link to="/activity" className="text-sm text-primary-600 hover:text-primary-800 flex items-center">
                  View all
                  <ArrowRightIcon className="h-4 w-4 ml-1" />
                </Link>
              </div>
            </div>
            <div className="card-body">
              <div className="space-y-4">
                {recentActivity.map((activity, index) => {
                  const Icon = getActivityIcon(activity.type)
                  return (
                    <motion.div
                      key={activity.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.8 + index * 0.1 }}
                      className="flex items-start space-x-3"
                    >
                      <div className={`p-2 rounded-full ${getActivityIconColor(activity.type)}`}>
                        <Icon className="h-4 w-4" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <p className="text-sm font-medium text-gray-900">{activity.title}</p>
                          <span className="text-xs text-gray-500">{formatRelativeTime(activity.timestamp)}</span>
                        </div>
                        <p className="text-sm text-gray-600 mt-1">{activity.description}</p>
                        {activity.projectName && (
                          <p className="text-xs text-gray-500 mt-1">
                            Project: {activity.projectName}
                          </p>
                        )}
                      </div>
                      <div className="flex-shrink-0">
                        {activity.status === 'success' && (
                          <CheckCircleIcon className="h-4 w-4 text-green-500" />
                        )}
                        {activity.status === 'failed' && (
                          <ExclamationTriangleIcon className="h-4 w-4 text-red-500" />
                        )}
                        {activity.status === 'processing' && (
                          <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
                        )}
                      </div>
                    </motion.div>
                  )
                })}
              </div>
            </div>
          </div>
        </motion.div>

        {/* Project Progress */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="lg:col-span-1"
        >
          <div className="card">
            <div className="card-header">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold text-gray-900">Project Progress</h2>
                <Link to="/projects" className="text-sm text-primary-600 hover:text-primary-800 flex items-center">
                  View all
                  <ArrowRightIcon className="h-4 w-4 ml-1" />
                </Link>
              </div>
            </div>
            <div className="card-body">
              <div className="space-y-4">
                {projectProgress.map((project, index) => (
                  <motion.div
                    key={project.id}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.9 + index * 0.1 }}
                    className="border border-gray-200 rounded-lg p-4"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-medium text-gray-900">{project.name}</h3>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(project.status)}`}>
                        {project.status.replace('_', ' ')}
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-sm text-gray-600 mb-3">
                      <span>{project.completedStories}/{project.totalStories} stories</span>
                      <span>Due {formatDate(project.dueDate)}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${project.progress}%` }}
                      />
                    </div>
                    <p className="text-xs text-gray-500 mt-2">{project.progress}% complete</p>
                  </motion.div>
                ))}
              </div>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Quick Actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1.0 }}
        className="card"
      >
        <div className="card-header">
          <h2 className="text-xl font-semibold text-gray-900">Quick Actions</h2>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Link 
              to="/upload" 
              className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <div className="p-2 bg-blue-100 rounded-lg">
                <DocumentIcon className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <h3 className="font-medium text-gray-900">Upload Document</h3>
                <p className="text-sm text-gray-600">Process new requirements</p>
              </div>
            </Link>
            
            <Link 
              to="/projects/new" 
              className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <div className="p-2 bg-green-100 rounded-lg">
                <PlusIcon className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <h3 className="font-medium text-gray-900">New Project</h3>
                <p className="text-sm text-gray-600">Create project workspace</p>
              </div>
            </Link>
            
            <Link 
              to="/projects" 
              className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <div className="p-2 bg-purple-100 rounded-lg">
                <EyeIcon className="h-5 w-5 text-purple-600" />
              </div>
              <div>
                <h3 className="font-medium text-gray-900">View Projects</h3>
                <p className="text-sm text-gray-600">Browse all projects</p>
              </div>
            </Link>
            
            <Link 
              to="/settings" 
              className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <div className="p-2 bg-gray-100 rounded-lg">
                <Cog6ToothIcon className="h-5 w-5 text-gray-600" />
              </div>
              <div>
                <h3 className="font-medium text-gray-900">Settings</h3>
                <p className="text-sm text-gray-600">Configure preferences</p>
              </div>
            </Link>
          </div>
        </div>
      </motion.div>
    </div>
  )
} 