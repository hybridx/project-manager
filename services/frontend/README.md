# AI Project Manager Frontend

A modern, beautiful, and fully functional React frontend for the AI-driven project management system. Built with cutting-edge technologies and designed for optimal user experience.

## 🎨 Features

### ✨ Beautiful & Modern UI
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile devices
- **Modern Design System**: Clean, minimal design with consistent spacing and typography
- **Smooth Animations**: Framer Motion animations for enhanced user experience
- **Tailwind CSS**: Utility-first CSS framework for rapid UI development
- **Professional Color Palette**: Thoughtfully chosen colors for optimal readability

### 🚀 Core Functionality

#### 📊 Dashboard
- **Real-time Statistics**: Total projects, documents processed, epics generated, user stories
- **Activity Feed**: Live updates on document processing, project creation, and epic generation
- **Project Progress**: Visual progress bars and status indicators
- **Quick Actions**: Fast access to common tasks
- **Time Range Filtering**: View data for last 7, 30, or 90 days

#### 📄 Document Upload
- **Drag & Drop Interface**: Intuitive file upload with visual feedback
- **File Preview**: Preview selected files before processing
- **Processing Status**: Real-time progress indicators and status updates
- **Multiple File Types**: Support for PDF, Word docs, Markdown, and text files
- **Processing Options**: Document type selection and additional context

#### 📁 Project Management
- **Project Cards**: Beautiful card-based project display
- **Search & Filter**: Find projects by name, status, or other criteria
- **Status Indicators**: Visual project status (Active, Planning, Completed, etc.)
- **Team Information**: Team member count and Jira integration status
- **Sorting Options**: Sort by name, creation date, or last updated

#### 🎯 Project Details
- **Tabbed Interface**: Organized view of Overview, Epics, Stories, Documents, and Team
- **Progress Tracking**: Visual progress bars and completion statistics
- **Epic Management**: View and manage project epics with story point estimation
- **Story Management**: Detailed user stories with acceptance criteria
- **Document History**: Track all processed documents for the project
- **Team Collaboration**: Team member management and role assignment

#### 📋 Processing Results
- **Comprehensive Results**: Detailed view of generated epics and user stories
- **Interactive Tabs**: Overview, Epics, Stories, and Insights sections
- **Export Options**: Download results in various formats
- **Insights Panel**: Risks, dependencies, and next steps recommendations
- **Project Creation**: Direct project creation from processing results

#### ⚙️ Settings
- **Account Management**: Profile information and avatar settings
- **Project Defaults**: Default priorities and story point scales
- **Integrations**: Jira and Slack integration configuration
- **Notifications**: Email and Slack notification preferences
- **Security**: Two-factor authentication and session management
- **Appearance**: Theme, language, and timezone settings

### 🛠️ Technical Features

#### 🏗️ Architecture
- **Component-Based**: Modular React components for maintainability
- **TypeScript**: Full type safety and better developer experience
- **Custom Hooks**: Reusable logic for common operations
- **State Management**: Efficient state handling with React hooks
- **Routing**: React Router for seamless navigation

#### 🎭 User Experience
- **Loading States**: Skeleton screens and loading indicators
- **Error Handling**: Graceful error messages and recovery
- **Toast Notifications**: Non-intrusive success and error messages
- **Keyboard Navigation**: Full keyboard accessibility
- **Screen Reader Support**: ARIA labels and semantic HTML

#### 📱 Responsive Design
- **Mobile-First**: Optimized for mobile devices
- **Sidebar Navigation**: Collapsible sidebar for desktop, overlay for mobile
- **Touch-Friendly**: Optimized touch targets and gestures
- **Flexible Layouts**: CSS Grid and Flexbox for responsive layouts

## 🚀 Getting Started

### Prerequisites
- Node.js 18.0.0 or higher
- npm 8.0.0 or higher

### Installation
```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Development Commands
```bash
# Run linter
npm run lint

# Fix linting issues
npm run lint:fix

# Type checking
npm run type-check

# Format code
npm run format

# Run tests
npm run test

# Run tests with UI
npm run test:ui

# Generate test coverage
npm run test:coverage
```

## 🏗️ Project Structure

```
src/
├── components/          # Reusable UI components
│   └── Layout.tsx      # Main layout with navigation
├── pages/              # Route components
│   ├── Dashboard.tsx   # Main dashboard
│   ├── DocumentUpload.tsx
│   ├── Projects.tsx
│   ├── ProjectDetails.tsx
│   ├── ProcessingResults.tsx
│   └── Settings.tsx
├── types/              # TypeScript type definitions
│   └── index.ts
├── hooks/              # Custom React hooks
├── utils/              # Utility functions
├── styles/             # Global styles and Tailwind config
│   └── globals.css
├── App.tsx             # Main app component
└── main.tsx           # App entry point
```

## 🎨 Design System

### Colors
- **Primary**: Blue scale for main actions and links
- **Secondary**: Gray scale for secondary elements
- **Success**: Green for positive actions and states
- **Warning**: Yellow for warnings and attention
- **Error**: Red for errors and dangerous actions

### Typography
- **Font Family**: Inter for UI text, JetBrains Mono for code
- **Font Weights**: 300, 400, 500, 600, 700
- **Responsive Sizing**: Scales appropriately across screen sizes

### Components
- **Buttons**: Primary, secondary, outline, and ghost variants
- **Cards**: Consistent card design with headers, bodies, and footers
- **Forms**: Styled inputs, selects, and form controls
- **Navigation**: Sidebar navigation with active states
- **Badges**: Status indicators and labels

## 🔧 Configuration

### Environment Variables
```env
# API Configuration
VITE_API_URL=http://localhost:8000
VITE_API_TIMEOUT=30000

# Feature Flags
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_SENTRY=false

# Development
VITE_DEV_MODE=true
```

### Tailwind Configuration
The project uses a custom Tailwind configuration with:
- Extended color palette
- Custom component classes
- Responsive breakpoints
- Animation utilities

## 🚀 Deployment

### Production Build
```bash
npm run build
```

### Docker Deployment
```bash
# Build image
docker build -t ai-project-manager-frontend .

# Run container
docker run -p 3000:80 ai-project-manager-frontend
```

### Nginx Configuration
The project includes an optimized Nginx configuration for:
- Static file serving
- Gzip compression
- Browser caching
- SPA routing support

## 📊 Performance

### Optimization Features
- **Code Splitting**: Automatic route-based code splitting
- **Tree Shaking**: Unused code elimination
- **Asset Optimization**: Optimized images and fonts
- **Lazy Loading**: Components loaded on demand
- **Caching**: Aggressive caching strategies

### Bundle Analysis
```bash
npm run build:analyze
```

## 🧪 Testing

### Test Coverage
- **Unit Tests**: Component and utility function tests
- **Integration Tests**: Feature workflow tests
- **E2E Tests**: Full application flow tests
- **Accessibility Tests**: WCAG compliance tests

### Running Tests
```bash
# Run all tests
npm test

# Watch mode
npm run test:watch

# Coverage report
npm run test:coverage
```

## 🎯 Features in Development

- [ ] Dark mode support
- [ ] Real-time collaboration
- [ ] Advanced analytics dashboard
- [ ] AI-powered insights
- [ ] Offline support
- [ ] PWA capabilities

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🌟 Acknowledgments

- **Design Inspiration**: Modern SaaS applications and design systems
- **Icons**: Heroicons for beautiful SVG icons
- **Animations**: Framer Motion for smooth animations
- **UI Components**: Tailwind UI and Headless UI for accessible components

---

Built with ❤️ by the AI Project Manager team 