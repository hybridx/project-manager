import React, { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { 
  ArrowLeftIcon,
  DocumentIcon,
  ChartBarIcon,
  CheckCircleIcon,
  ClockIcon,
  UsersIcon,
  EyeIcon,
  ArrowDownTrayIcon,
  ShareIcon,
  PlusIcon,
  ArrowRightIcon
} from '@heroicons/react/24/outline'
import { DocumentProcessingResponse, Epic, UserStory, Priority, StoryStatus } from '@/types'

const mockProcessingResult: DocumentProcessingResponse = {
  success: true,
  message: 'Document processed successfully',
  document_id: 'doc_123',
  artifacts: {
    epics: [
      {
        id: '1',
        title: 'User Authentication System',
        description: 'Implement secure user authentication with OAuth and multi-factor authentication',
        priority: Priority.HIGH,
        acceptance_criteria: 'Users can register, login, and reset passwords securely with proper error handling',
        estimated_story_points: 34,
        user_stories: [
          {
            id: '1',
            title: 'User Registration',
            description: 'As a new user, I want to create an account so that I can access the platform',
            priority: Priority.HIGH,
            story_points: 13,
            acceptance_criteria: [
              {
                scenario: 'Successful registration',
                steps: [
                  'Given I am on the registration page',
                  'When I enter valid email and password',
                  'And I click the register button',
                  'Then my account is created',
                  'And I receive a confirmation email'
                ]
              },
              {
                scenario: 'Invalid email format',
                steps: [
                  'Given I am on the registration page',
                  'When I enter an invalid email format',
                  'And I click the register button',
                  'Then I see an error message',
                  'And my account is not created'
                ]
              }
            ],
            epic_id: '1',
            status: StoryStatus.BACKLOG
          },
          {
            id: '2',
            title: 'User Login',
            description: 'As a registered user, I want to login to my account so that I can access my dashboard',
            priority: Priority.HIGH,
            story_points: 8,
            acceptance_criteria: [
              {
                scenario: 'Successful login',
                steps: [
                  'Given I am on the login page',
                  'When I enter valid credentials',
                  'And I click the login button',
                  'Then I am redirected to my dashboard',
                  'And I see my profile information'
                ]
              }
            ],
            epic_id: '1',
            status: StoryStatus.BACKLOG
          },
          {
            id: '3',
            title: 'Password Reset',
            description: 'As a user, I want to reset my password so that I can regain access to my account',
            priority: Priority.MEDIUM,
            story_points: 13,
            acceptance_criteria: [
              {
                scenario: 'Password reset request',
                steps: [
                  'Given I forgot my password',
                  'When I click "Forgot Password"',
                  'And I enter my email address',
                  'Then I receive a password reset email',
                  'And I can create a new password'
                ]
              }
            ],
            epic_id: '1',
            status: StoryStatus.BACKLOG
          }
        ]
      },
      {
        id: '2',
        title: 'Product Catalog Management',
        description: 'Build a comprehensive product catalog with inventory management',
        priority: Priority.MEDIUM,
        acceptance_criteria: 'Admin can manage products and users can browse catalog effectively',
        estimated_story_points: 55,
        user_stories: [
          {
            id: '4',
            title: 'Product Listing',
            description: 'As a user, I want to view all available products so that I can make purchase decisions',
            priority: Priority.HIGH,
            story_points: 21,
            acceptance_criteria: [
              {
                scenario: 'Browse products',
                steps: [
                  'Given I am on the products page',
                  'When the page loads',
                  'Then I see a list of all available products',
                  'And each product shows image, name, and price'
                ]
              }
            ],
            epic_id: '2',
            status: StoryStatus.BACKLOG
          },
          {
            id: '5',
            title: 'Product Search',
            description: 'As a user, I want to search for specific products so that I can find what I need quickly',
            priority: Priority.MEDIUM,
            story_points: 13,
            acceptance_criteria: [
              {
                scenario: 'Search functionality',
                steps: [
                  'Given I am on the products page',
                  'When I enter a search term',
                  'And I click search',
                  'Then I see relevant search results',
                  'And results are ranked by relevance'
                ]
              }
            ],
            epic_id: '2',
            status: StoryStatus.BACKLOG
          },
          {
            id: '6',
            title: 'Product Categories',
            description: 'As a user, I want to filter products by category so that I can browse specific types of products',
            priority: Priority.MEDIUM,
            story_points: 21,
            acceptance_criteria: [
              {
                scenario: 'Category filtering',
                steps: [
                  'Given I am on the products page',
                  'When I select a category',
                  'Then I see only products in that category',
                  'And the category filter is highlighted'
                ]
              }
            ],
            epic_id: '2',
            status: StoryStatus.BACKLOG
          }
        ]
      }
    ],
    user_stories: [],
    contributors: ['Product Manager', 'UX Designer', 'Tech Lead'],
    project_summary: 'E-commerce platform with user authentication and product catalog management',
    estimated_duration: '4-6 months',
    key_features: [
      'User registration and authentication',
      'Product catalog with search and filtering',
      'Secure payment processing',
      'Admin dashboard for product management',
      'Mobile-responsive design'
    ],
    technical_requirements: [
      'React.js frontend with TypeScript',
      'Node.js backend with Express',
      'PostgreSQL database',
      'Redis for caching',
      'AWS S3 for image storage',
      'Stripe for payment processing'
    ],
    risks: [
      'Payment integration complexity',
      'User data security requirements',
      'Scalability concerns with large product catalogs',
      'Mobile responsiveness challenges'
    ],
    dependencies: [
      'Payment gateway API approval',
      'SSL certificate setup',
      'Third-party authentication providers',
      'Image optimization service'
    ]
  },
  processing_time: 12.5,
  metadata: {
    word_count: 2500,
    model_used: 'llama3.2:3b',
    document_type: 'prd',
    processing_date: '2024-01-20T15:30:00Z'
  }
}

export default function ProcessingResults() {
  const { documentId } = useParams<{ documentId: string }>()
  const [result, setResult] = useState<DocumentProcessingResponse | null>(mockProcessingResult)
  const [activeTab, setActiveTab] = useState<'overview' | 'epics' | 'stories' | 'insights'>('overview')
  const [loading, setLoading] = useState(false)

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

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

  const getTotalStoryPoints = () => {
    return result?.artifacts?.epics.reduce((total, epic) => total + epic.estimated_story_points, 0) || 0
  }

  const getTotalStories = () => {
    return result?.artifacts?.epics.reduce((total, epic) => total + epic.user_stories.length, 0) || 0
  }

  if (!result) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-center">
          <DocumentIcon className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Processing results not found</h2>
          <p className="text-gray-600 mb-4">The document processing results couldn't be found.</p>
          <Link to="/upload" className="btn btn-primary">
            Process New Document
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
            to="/upload" 
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeftIcon className="h-5 w-5 text-gray-500" />
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Processing Results</h1>
            <p className="text-gray-600">Document ID: {result.document_id}</p>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <button className="btn btn-secondary flex items-center space-x-2">
            <ArrowDownTrayIcon className="h-4 w-4" />
            <span>Export</span>
          </button>
          <button className="btn btn-secondary flex items-center space-x-2">
            <ShareIcon className="h-4 w-4" />
            <span>Share</span>
          </button>
          <Link 
            to="/projects/new"
            className="btn btn-primary flex items-center space-x-2"
          >
            <PlusIcon className="h-4 w-4" />
            <span>Create Project</span>
          </Link>
        </div>
      </div>

      {/* Success Banner */}
      {result.success && (
        <div className="bg-success-50 border border-success-200 rounded-lg p-4">
          <div className="flex items-center space-x-3">
            <CheckCircleIcon className="h-6 w-6 text-success-600" />
            <div>
              <p className="text-success-800 font-semibold">{result.message}</p>
              <p className="text-success-600 text-sm">
                Processed in {result.processing_time}s • {result.metadata?.word_count} words • {result.artifacts?.epics.length} epics • {getTotalStories()} stories
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card">
          <div className="card-body">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Epics Generated</p>
                <p className="text-2xl font-bold text-primary-600">{result.artifacts?.epics.length}</p>
              </div>
              <ChartBarIcon className="h-8 w-8 text-primary-600" />
            </div>
          </div>
        </div>
        
        <div className="card">
          <div className="card-body">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">User Stories</p>
                <p className="text-2xl font-bold text-success-600">{getTotalStories()}</p>
              </div>
              <DocumentIcon className="h-8 w-8 text-success-600" />
            </div>
          </div>
        </div>
        
        <div className="card">
          <div className="card-body">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Story Points</p>
                <p className="text-2xl font-bold text-warning-600">{getTotalStoryPoints()}</p>
              </div>
              <ClockIcon className="h-8 w-8 text-warning-600" />
            </div>
          </div>
        </div>
        
        <div className="card">
          <div className="card-body">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Contributors</p>
                <p className="text-2xl font-bold text-gray-900">{result.artifacts?.contributors.length}</p>
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
              { id: 'overview', label: 'Overview' },
              { id: 'epics', label: 'Epics' },
              { id: 'stories', label: 'User Stories' },
              { id: 'insights', label: 'Insights' }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`px-3 py-2 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        <div className="card-body">
          {activeTab === 'overview' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Project Summary</h3>
                  <p className="text-gray-600 mb-4">{result.artifacts?.project_summary}</p>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Estimated Duration</span>
                      <span className="text-gray-900">{result.artifacts?.estimated_duration}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Processing Time</span>
                      <span className="text-gray-900">{result.processing_time}s</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Model Used</span>
                      <span className="text-gray-900">{result.metadata?.model_used}</span>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Key Features</h3>
                  <ul className="space-y-2">
                    {result.artifacts?.key_features.map((feature, index) => (
                      <li key={index} className="flex items-start space-x-2">
                        <CheckCircleIcon className="h-5 w-5 text-success-600 mt-0.5 flex-shrink-0" />
                        <span className="text-gray-700">{feature}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Technical Requirements</h3>
                  <ul className="space-y-2">
                    {result.artifacts?.technical_requirements.map((req, index) => (
                      <li key={index} className="flex items-start space-x-2">
                        <div className="w-2 h-2 bg-primary-600 rounded-full mt-2 flex-shrink-0"></div>
                        <span className="text-gray-700">{req}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Contributors</h3>
                  <div className="space-y-2">
                    {result.artifacts?.contributors.map((contributor, index) => (
                      <div key={index} className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                          <span className="text-primary-600 font-semibold text-sm">
                            {contributor.charAt(0).toUpperCase()}
                          </span>
                        </div>
                        <span className="text-gray-700">{contributor}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'epics' && (
            <div className="space-y-6">
              {result.artifacts?.epics.map((epic, index) => (
                <motion.div
                  key={epic.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="border border-gray-200 rounded-lg p-6"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <h4 className="text-xl font-semibold text-gray-900 mb-2">{epic.title}</h4>
                      <p className="text-gray-600 mb-3">{epic.description}</p>
                      <p className="text-sm text-gray-500 mb-4">{epic.acceptance_criteria}</p>
                    </div>
                    <div className="flex items-center space-x-3">
                      <span className={`text-sm font-medium ${getPriorityColor(epic.priority)}`}>
                        {epic.priority}
                      </span>
                      <span className="text-sm text-gray-500">
                        {epic.estimated_story_points} pts
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4 text-sm text-gray-500">
                    <span>{epic.user_stories.length} stories</span>
                    <span>{epic.user_stories.reduce((sum, story) => sum + story.story_points, 0)} story points</span>
                  </div>
                </motion.div>
              ))}
            </div>
          )}

          {activeTab === 'stories' && (
            <div className="space-y-4">
              {result.artifacts?.epics.flatMap(epic => epic.user_stories).map((story, index) => (
                <motion.div
                  key={story.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="border border-gray-200 rounded-lg p-6"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h4 className="text-lg font-semibold text-gray-900">{story.title}</h4>
                        <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(story.status)}`}>
                          {story.status}
                        </span>
                      </div>
                      <p className="text-gray-600 mb-4">{story.description}</p>
                      
                      <div className="space-y-3">
                        <h5 className="font-medium text-gray-900">Acceptance Criteria</h5>
                        {story.acceptance_criteria.map((criteria, idx) => (
                          <div key={idx} className="bg-gray-50 p-3 rounded-lg">
                            <p className="font-medium text-gray-900 mb-2">{criteria.scenario}</p>
                            <ol className="list-decimal list-inside space-y-1 text-sm text-gray-600">
                              {criteria.steps.map((step, stepIdx) => (
                                <li key={stepIdx}>{step}</li>
                              ))}
                            </ol>
                          </div>
                        ))}
                      </div>
                    </div>
                    <div className="flex flex-col items-end space-y-2">
                      <span className={`text-sm font-medium ${getPriorityColor(story.priority)}`}>
                        {story.priority}
                      </span>
                      <span className="text-sm text-gray-500">
                        {story.story_points} pts
                      </span>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          )}

          {activeTab === 'insights' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Risks & Challenges</h3>
                  <ul className="space-y-3">
                    {result.artifacts?.risks.map((risk, index) => (
                      <li key={index} className="flex items-start space-x-3">
                        <div className="p-1 bg-red-100 rounded-full">
                          <div className="w-2 h-2 bg-red-600 rounded-full"></div>
                        </div>
                        <span className="text-gray-700">{risk}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Dependencies</h3>
                  <ul className="space-y-3">
                    {result.artifacts?.dependencies.map((dependency, index) => (
                      <li key={index} className="flex items-start space-x-3">
                        <div className="p-1 bg-blue-100 rounded-full">
                          <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                        </div>
                        <span className="text-gray-700">{dependency}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-blue-900 mb-4">Next Steps</h3>
                <div className="space-y-3">
                  <p className="text-blue-800">
                    Based on the analysis, here are the recommended next steps:
                  </p>
                  <ul className="space-y-2">
                    <li className="flex items-center space-x-2">
                      <CheckCircleIcon className="h-4 w-4 text-blue-600" />
                      <span className="text-blue-700">Create a new project to organize these epics and stories</span>
                    </li>
                    <li className="flex items-center space-x-2">
                      <CheckCircleIcon className="h-4 w-4 text-blue-600" />
                      <span className="text-blue-700">Prioritize epics based on business value and dependencies</span>
                    </li>
                    <li className="flex items-center space-x-2">
                      <CheckCircleIcon className="h-4 w-4 text-blue-600" />
                      <span className="text-blue-700">Review and refine user stories with the development team</span>
                    </li>
                    <li className="flex items-center space-x-2">
                      <CheckCircleIcon className="h-4 w-4 text-blue-600" />
                      <span className="text-blue-700">Set up Jira integration for project management</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Action Bar */}
      <div className="flex justify-end space-x-3">
        <Link 
          to="/upload" 
          className="btn btn-secondary"
        >
          Process Another Document
        </Link>
        <Link 
          to="/projects/new" 
          className="btn btn-primary flex items-center space-x-2"
        >
          <span>Create Project from Results</span>
          <ArrowRightIcon className="h-4 w-4" />
        </Link>
      </div>
    </div>
  )
} 