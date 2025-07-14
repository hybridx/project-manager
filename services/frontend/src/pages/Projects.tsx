import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { 
  PlusIcon, 
  MagnifyingGlassIcon, 
  FunnelIcon,
  DocumentIcon,
  UsersIcon,
  ChartBarIcon,
  EllipsisVerticalIcon,
  FolderIcon,
  CalendarIcon
} from '@heroicons/react/24/outline'
import { Project, ProjectStatus } from '@/types'

const mockProjects: Project[] = [
  {
    id: '1',
    name: 'E-commerce Platform',
    description: 'Building a modern e-commerce platform with AI-powered recommendations',
    created_at: '2024-01-15T10:30:00Z',
    updated_at: '2024-01-20T14:22:00Z',
    status: ProjectStatus.ACTIVE,
    team_members: ['alice@company.com', 'bob@company.com', 'charlie@company.com'],
    jira_project_key: 'ECOM',
    documents: [],
    settings: {
      auto_sync_jira: true,
      default_priority: 'medium' as any,
      story_point_scale: [1, 2, 3, 5, 8, 13, 21],
      team_members: ['alice@company.com', 'bob@company.com'],
      notification_preferences: {
        email_on_processing_complete: true,
        jira_notifications: true
      }
    }
  },
  {
    id: '2',
    name: 'Mobile Banking App',
    description: 'Secure mobile banking application with biometric authentication',
    created_at: '2024-01-10T09:15:00Z',
    updated_at: '2024-01-18T16:45:00Z',
    status: ProjectStatus.PLANNING,
    team_members: ['david@company.com', 'eve@company.com'],
    documents: [],
    settings: {
      auto_sync_jira: false,
      default_priority: 'high' as any,
      story_point_scale: [1, 2, 3, 5, 8, 13, 21],
      team_members: ['david@company.com', 'eve@company.com'],
      notification_preferences: {
        email_on_processing_complete: true,
        jira_notifications: false
      }
    }
  },
  {
    id: '3',
    name: 'AI Analytics Dashboard',
    description: 'Real-time analytics dashboard for business intelligence',
    created_at: '2024-01-05T11:20:00Z',
    updated_at: '2024-01-19T13:10:00Z',
    status: ProjectStatus.COMPLETED,
    team_members: ['frank@company.com', 'grace@company.com', 'henry@company.com'],
    documents: [],
    settings: {
      auto_sync_jira: true,
      default_priority: 'medium' as any,
      story_point_scale: [1, 2, 3, 5, 8, 13, 21],
      team_members: ['frank@company.com', 'grace@company.com'],
      notification_preferences: {
        email_on_processing_complete: true,
        jira_notifications: true
      }
    }
  }
]

export default function Projects() {
  const [projects, setProjects] = useState<Project[]>(mockProjects)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<ProjectStatus | 'all'>('all')
  const [sortBy, setSortBy] = useState<'name' | 'created_at' | 'updated_at'>('updated_at')

  const filteredProjects = projects.filter(project => {
    const matchesSearch = project.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         project.description.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === 'all' || project.status === statusFilter
    return matchesSearch && matchesStatus
  })

  const sortedProjects = [...filteredProjects].sort((a, b) => {
    if (sortBy === 'name') {
      return a.name.localeCompare(b.name)
    }
    return new Date(b[sortBy]).getTime() - new Date(a[sortBy]).getTime()
  })

  const getStatusColor = (status: ProjectStatus) => {
    switch (status) {
      case ProjectStatus.ACTIVE:
        return 'bg-success-100 text-success-800'
      case ProjectStatus.PLANNING:
        return 'bg-warning-100 text-warning-800'
      case ProjectStatus.COMPLETED:
        return 'bg-primary-100 text-primary-800'
      case ProjectStatus.ON_HOLD:
        return 'bg-gray-100 text-gray-800'
      case ProjectStatus.ARCHIVED:
        return 'bg-gray-100 text-gray-600'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Projects</h1>
          <p className="text-gray-600 mt-1">Manage your project portfolio</p>
        </div>
        <Link 
          to="/projects/new" 
          className="btn btn-primary flex items-center space-x-2"
        >
          <PlusIcon className="h-5 w-5" />
          <span>New Project</span>
        </Link>
      </div>

      {/* Filters and Search */}
      <div className="card">
        <div className="card-body">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search projects..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                />
              </div>
            </div>
            <div className="flex gap-3">
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value as ProjectStatus | 'all')}
                className="px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
              >
                <option value="all">All Status</option>
                <option value={ProjectStatus.ACTIVE}>Active</option>
                <option value={ProjectStatus.PLANNING}>Planning</option>
                <option value={ProjectStatus.COMPLETED}>Completed</option>
                <option value={ProjectStatus.ON_HOLD}>On Hold</option>
                <option value={ProjectStatus.ARCHIVED}>Archived</option>
              </select>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as 'name' | 'created_at' | 'updated_at')}
                className="px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
              >
                <option value="updated_at">Recently Updated</option>
                <option value="created_at">Recently Created</option>
                <option value="name">Name</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Projects Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {sortedProjects.map((project, index) => (
          <motion.div
            key={project.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <Link 
              to={`/projects/${project.id}`}
              className="block card hover:shadow-lg transition-shadow duration-200"
            >
              <div className="card-body">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-primary-100 rounded-lg">
                      <FolderIcon className="h-6 w-6 text-primary-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">{project.name}</h3>
                      <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(project.status)}`}>
                        {project.status}
                      </span>
                    </div>
                  </div>
                  <button className="p-1 hover:bg-gray-100 rounded-full">
                    <EllipsisVerticalIcon className="h-5 w-5 text-gray-400" />
                  </button>
                </div>

                <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                  {project.description}
                </p>

                <div className="space-y-3">
                  <div className="flex items-center justify-between text-sm">
                    <div className="flex items-center space-x-1 text-gray-500">
                      <UsersIcon className="h-4 w-4" />
                      <span>{project.team_members.length} members</span>
                    </div>
                    <div className="flex items-center space-x-1 text-gray-500">
                      <DocumentIcon className="h-4 w-4" />
                      <span>{project.documents.length} docs</span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <div className="flex items-center space-x-1">
                      <CalendarIcon className="h-3 w-3" />
                      <span>Updated {formatDate(project.updated_at)}</span>
                    </div>
                    {project.jira_project_key && (
                      <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded">
                        {project.jira_project_key}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </Link>
          </motion.div>
        ))}
      </div>

      {sortedProjects.length === 0 && (
        <div className="text-center py-12">
          <FolderIcon className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No projects found</h3>
          <p className="text-gray-600 mb-4">
            {searchTerm || statusFilter !== 'all' 
              ? 'Try adjusting your search or filters'
              : 'Get started by creating your first project'
            }
          </p>
          {!searchTerm && statusFilter === 'all' && (
            <Link 
              to="/projects/new" 
              className="btn btn-primary"
            >
              Create Project
            </Link>
          )}
        </div>
      )}
    </div>
  )
} 