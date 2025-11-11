"""
Design Document Processor - Middleware for processing design documents
and breaking them down into small, actionable issues.

This service extends the existing DocumentOrchestrator to handle design documents
specifically and create granular issues suitable for development workflows.
"""

import logging
import uuid
import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone

from ..core.interfaces import DocumentProcessorProtocol
from ..core.error_handler import handle_errors
from ..models.schemas import (
    UserStory, Epic, AcceptanceCriteria, Priority, 
    ExtractedArtifacts, DocumentProcessingResponse
)
from .ollama_client import OllamaClient

logger = logging.getLogger(__name__)


class DesignIssue:
    """Represents a small, actionable issue derived from design documents"""
    def __init__(
        self,
        id: str,
        title: str,
        description: str,
        issue_type: str,
        priority: Priority,
        component: str,
        estimated_hours: float,
        dependencies: List[str] = None,
        labels: List[str] = None,
        acceptance_criteria: List[str] = None
    ):
        self.id = id
        self.title = title
        self.description = description
        self.issue_type = issue_type  # bug, feature, task, research, documentation
        self.priority = priority
        self.component = component
        self.estimated_hours = estimated_hours
        self.dependencies = dependencies or []
        self.labels = labels or []
        self.acceptance_criteria = acceptance_criteria or []
        self.created_at = datetime.now(timezone.utc)


class DesignDocumentProcessor:
    """
    Specialized processor for design documents that breaks them down into
    small, actionable development issues.
    """
    
    def __init__(self, ollama_client: OllamaClient):
        self.ollama_client = ollama_client
        self.issue_types = {
            "feature": "New functionality to implement",
            "task": "Implementation work or setup",
            "bug": "Defect or issue to fix",
            "research": "Investigation or spike work",
            "documentation": "Documentation to create/update",
            "testing": "Test creation or testing tasks",
            "infrastructure": "Infrastructure or DevOps work"
        }
    
    @handle_errors("design_processing")
    async def process_design_document(
        self,
        content: str,
        document_name: str,
        project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a design document and break it down into actionable issues
        
        Args:
            content: Design document content
            document_name: Name of the document
            project_id: Associated project ID
            
        Returns:
            Dictionary containing processed issues and metadata
        """
        logger.info(f"Processing design document: {document_name}")
        
        # Step 1: Extract design components and requirements
        design_analysis = await self._analyze_design_document(content)
        
        # Step 2: Break down into functional areas
        functional_areas = await self._extract_functional_areas(content, design_analysis)
        
        # Step 3: Generate granular issues for each functional area
        issues = await self._generate_granular_issues(functional_areas, design_analysis)
        
        # Step 4: Prioritize and categorize issues
        prioritized_issues = await self._prioritize_and_categorize_issues(issues)
        
        # Step 5: Create implementation roadmap
        roadmap = await self._create_implementation_roadmap(prioritized_issues)
        
        # Step 6: Generate cross-cutting concerns
        cross_cutting_issues = await self._generate_cross_cutting_issues(design_analysis)
        
        all_issues = prioritized_issues + cross_cutting_issues
        
        result = {
            "success": True,
            "document_name": document_name,
            "project_id": project_id,
            "total_issues": len(all_issues),
            "design_analysis": design_analysis,
            "functional_areas": functional_areas,
            "issues": [self._issue_to_dict(issue) for issue in all_issues],
            "implementation_roadmap": roadmap,
            "metadata": {
                "processing_timestamp": datetime.now(timezone.utc).isoformat(),
                "document_complexity": self._assess_complexity(design_analysis),
                "estimated_total_hours": sum(issue.estimated_hours for issue in all_issues)
            }
        }
        
        logger.info(f"Generated {len(all_issues)} issues from design document")
        return result
    
    async def _analyze_design_document(self, content: str) -> Dict[str, Any]:
        """Analyze the design document to extract high-level components and requirements"""
        
        analysis_prompt = f"""
        Analyze this design document and extract the following information:
        
        1. **System Components**: List all major system components mentioned
        2. **APIs and Interfaces**: List all APIs, endpoints, or interfaces described
        3. **Data Models**: List data structures, entities, or database schemas
        4. **External Dependencies**: List third-party services, libraries, or systems
        5. **Technical Requirements**: List non-functional requirements (performance, security, etc.)
        6. **User Interactions**: List user flows and interaction patterns
        7. **Business Logic**: List core business rules and algorithms
        8. **Infrastructure Needs**: List deployment, scaling, or infrastructure requirements
        
        Document Content:
        {content}
        
        Respond with a JSON structure containing these categories with lists of items.
        """
        
        response = await self.ollama_client.generate_response(analysis_prompt)
        
        try:
            # Parse AI response and extract structured data
            analysis = self._parse_ai_analysis_response(response)
            return analysis
        except Exception as e:
            logger.warning(f"Failed to parse AI analysis response: {e}")
            # Fallback to rule-based extraction
            return self._fallback_analysis(content)
    
    async def _extract_functional_areas(
        self, 
        content: str, 
        design_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract functional areas that can be developed independently"""
        
        functional_prompt = f"""
        Based on this design document and analysis, break down the system into
        functional areas that can be developed independently.
        
        For each functional area, provide:
        1. **Name**: Descriptive name for the area
        2. **Description**: What this area is responsible for
        3. **Components**: Which system components it includes
        4. **Dependencies**: What other areas it depends on
        5. **Priority**: High, Medium, or Low
        6. **Complexity**: Simple, Medium, or Complex
        
        Design Analysis:
        {design_analysis}
        
        Document Content (first 2000 chars):
        {content[:2000]}
        
        Respond with a JSON array of functional areas.
        """
        
        response = await self.ollama_client.generate_response(functional_prompt)
        
        try:
            functional_areas = self._parse_functional_areas_response(response)
            return functional_areas
        except Exception as e:
            logger.warning(f"Failed to parse functional areas: {e}")
            return self._create_default_functional_areas(design_analysis)
    
    async def _generate_granular_issues(
        self,
        functional_areas: List[Dict[str, Any]],
        design_analysis: Dict[str, Any]
    ) -> List[DesignIssue]:
        """Generate granular development issues for each functional area"""
        
        all_issues = []
        
        for area in functional_areas:
            area_issues = await self._generate_issues_for_area(area, design_analysis)
            all_issues.extend(area_issues)
        
        return all_issues
    
    async def _generate_issues_for_area(
        self,
        functional_area: Dict[str, Any],
        design_analysis: Dict[str, Any]
    ) -> List[DesignIssue]:
        """Generate specific issues for a functional area"""
        
        issue_prompt = f"""
        Create detailed development issues for this functional area.
        
        Functional Area: {functional_area['name']}
        Description: {functional_area['description']}
        Components: {functional_area.get('components', [])}
        Complexity: {functional_area.get('complexity', 'Medium')}
        
        Generate 3-8 specific, actionable development issues. For each issue:
        1. **Title**: Clear, specific title (max 60 chars)
        2. **Description**: Detailed description of what needs to be done
        3. **Type**: feature|task|research|documentation|testing|infrastructure
        4. **Priority**: high|medium|low
        5. **Estimated Hours**: Realistic estimate (0.5-16 hours)
        6. **Acceptance Criteria**: 2-4 specific criteria
        7. **Dependencies**: Other issues this depends on
        
        Make issues small enough to complete in 1-2 days.
        Include setup, implementation, testing, and documentation tasks.
        
        Respond with JSON array of issues.
        """
        
        response = await self.ollama_client.generate_response(issue_prompt)
        
        try:
            issues_data = self._parse_issues_response(response)
            issues = []
            
            for issue_data in issues_data:
                issue = DesignIssue(
                    id=f"{functional_area['name'].lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}",
                    title=issue_data.get('title', ''),
                    description=issue_data.get('description', ''),
                    issue_type=issue_data.get('type', 'task'),
                    priority=Priority(issue_data.get('priority', 'medium')),
                    component=functional_area['name'],
                    estimated_hours=float(issue_data.get('estimated_hours', 4.0)),
                    dependencies=issue_data.get('dependencies', []),
                    labels=[functional_area['name'].lower(), issue_data.get('type', 'task')],
                    acceptance_criteria=issue_data.get('acceptance_criteria', [])
                )
                issues.append(issue)
            
            return issues
            
        except Exception as e:
            logger.warning(f"Failed to parse issues for area {functional_area['name']}: {e}")
            return self._create_fallback_issues_for_area(functional_area)
    
    async def _prioritize_and_categorize_issues(
        self,
        issues: List[DesignIssue]
    ) -> List[DesignIssue]:
        """Prioritize issues based on dependencies and complexity"""
        
        # Sort by priority and dependencies
        def priority_score(issue):
            priority_weights = {"high": 3, "medium": 2, "low": 1}
            type_weights = {
                "infrastructure": 5,  # Setup first
                "research": 4,        # Research early
                "feature": 3,         # Core features
                "task": 2,           # Implementation tasks
                "testing": 1,        # Testing after features
                "documentation": 0   # Documentation last
            }
            
            return (
                priority_weights.get(issue.priority.value, 1) * 10 +
                type_weights.get(issue.issue_type, 1) * 5 +
                (10 - issue.estimated_hours)  # Prefer smaller tasks initially
            )
        
        return sorted(issues, key=priority_score, reverse=True)
    
    async def _create_implementation_roadmap(
        self,
        issues: List[DesignIssue]
    ) -> Dict[str, Any]:
        """Create an implementation roadmap based on issues"""
        
        # Group issues by component and priority
        roadmap = {
            "phases": [],
            "total_estimated_hours": sum(issue.estimated_hours for issue in issues),
            "total_issues": len(issues)
        }
        
        # Phase 1: Infrastructure and Research
        phase1_issues = [i for i in issues if i.issue_type in ["infrastructure", "research"]]
        if phase1_issues:
            roadmap["phases"].append({
                "name": "Phase 1: Foundation & Research",
                "description": "Setup infrastructure and conduct necessary research",
                "issues": len(phase1_issues),
                "estimated_hours": sum(i.estimated_hours for i in phase1_issues),
                "issue_ids": [i.id for i in phase1_issues]
            })
        
        # Phase 2: Core Features
        phase2_issues = [i for i in issues if i.issue_type in ["feature", "task"] and i.priority == Priority.HIGH]
        if phase2_issues:
            roadmap["phases"].append({
                "name": "Phase 2: Core Features",
                "description": "Implement high-priority features",
                "issues": len(phase2_issues),
                "estimated_hours": sum(i.estimated_hours for i in phase2_issues),
                "issue_ids": [i.id for i in phase2_issues]
            })
        
        # Phase 3: Additional Features
        phase3_issues = [i for i in issues if i.issue_type in ["feature", "task"] and i.priority != Priority.HIGH]
        if phase3_issues:
            roadmap["phases"].append({
                "name": "Phase 3: Additional Features",
                "description": "Implement remaining features",
                "issues": len(phase3_issues),
                "estimated_hours": sum(i.estimated_hours for i in phase3_issues),
                "issue_ids": [i.id for i in phase3_issues]
            })
        
        # Phase 4: Testing and Documentation
        phase4_issues = [i for i in issues if i.issue_type in ["testing", "documentation"]]
        if phase4_issues:
            roadmap["phases"].append({
                "name": "Phase 4: Testing & Documentation",
                "description": "Complete testing and documentation",
                "issues": len(phase4_issues),
                "estimated_hours": sum(i.estimated_hours for i in phase4_issues),
                "issue_ids": [i.id for i in phase4_issues]
            })
        
        return roadmap
    
    async def _generate_cross_cutting_issues(
        self,
        design_analysis: Dict[str, Any]
    ) -> List[DesignIssue]:
        """Generate issues for cross-cutting concerns like security, monitoring, etc."""
        
        cross_cutting_issues = []
        
        # Security issues
        if any("security" in str(item).lower() for items in design_analysis.values() for item in items):
            security_issue = DesignIssue(
                id=f"security_{uuid.uuid4().hex[:8]}",
                title="Implement security measures",
                description="Implement authentication, authorization, and data protection",
                issue_type="feature",
                priority=Priority.HIGH,
                component="Security",
                estimated_hours=8.0,
                labels=["security", "cross-cutting"],
                acceptance_criteria=[
                    "Authentication system implemented",
                    "Authorization checks in place",
                    "Sensitive data encrypted",
                    "Security tests pass"
                ]
            )
            cross_cutting_issues.append(security_issue)
        
        # Monitoring and logging
        monitoring_issue = DesignIssue(
            id=f"monitoring_{uuid.uuid4().hex[:8]}",
            title="Setup monitoring and logging",
            description="Implement application monitoring, logging, and alerting",
            issue_type="infrastructure",
            priority=Priority.MEDIUM,
            component="Monitoring",
            estimated_hours=6.0,
            labels=["monitoring", "cross-cutting"],
            acceptance_criteria=[
                "Application logs configured",
                "Health checks implemented",
                "Error tracking setup",
                "Performance metrics collected"
            ]
        )
        cross_cutting_issues.append(monitoring_issue)
        
        # Documentation
        docs_issue = DesignIssue(
            id=f"documentation_{uuid.uuid4().hex[:8]}",
            title="Create comprehensive documentation",
            description="Create API documentation, user guides, and deployment docs",
            issue_type="documentation",
            priority=Priority.LOW,
            component="Documentation",
            estimated_hours=12.0,
            labels=["documentation", "cross-cutting"],
            acceptance_criteria=[
                "API documentation complete",
                "User guide written",
                "Deployment guide created",
                "Code comments added"
            ]
        )
        cross_cutting_issues.append(docs_issue)
        
        return cross_cutting_issues
    
    def _parse_ai_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse AI analysis response into structured data"""
        # Try to extract JSON from response
        import json
        try:
            # Look for JSON in the response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        # Fallback parsing
        return self._fallback_analysis(response)
    
    def _fallback_analysis(self, content: str) -> Dict[str, Any]:
        """Fallback analysis when AI parsing fails"""
        return {
            "system_components": self._extract_components_heuristic(content),
            "apis_interfaces": self._extract_apis_heuristic(content),
            "data_models": self._extract_models_heuristic(content),
            "external_dependencies": self._extract_dependencies_heuristic(content),
            "technical_requirements": self._extract_requirements_heuristic(content),
            "user_interactions": [],
            "business_logic": [],
            "infrastructure_needs": []
        }
    
    def _extract_components_heuristic(self, content: str) -> List[str]:
        """Extract system components using heuristics"""
        components = []
        # Look for common patterns like "Component", "Service", "Module"
        patterns = [
            r'(\w+)\s+(component|service|module|system)',
            r'(component|service|module|system)\s+(\w+)',
            r'class\s+(\w+)',
            r'interface\s+(\w+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    components.extend([m for m in match if m.lower() not in ['component', 'service', 'module', 'system']])
                else:
                    components.append(match)
        
        return list(set(components))[:10]  # Limit to 10 components
    
    def _extract_apis_heuristic(self, content: str) -> List[str]:
        """Extract APIs using heuristics"""
        apis = []
        patterns = [
            r'(GET|POST|PUT|DELETE|PATCH)\s+(/[\w/]+)',
            r'endpoint[:\s]+([/\w]+)',
            r'api[:\s]+([/\w]+)',
            r'route[:\s]+([/\w]+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    apis.append(' '.join(match))
                else:
                    apis.append(match)
        
        return list(set(apis))[:15]  # Limit to 15 APIs
    
    def _extract_models_heuristic(self, content: str) -> List[str]:
        """Extract data models using heuristics"""
        models = []
        patterns = [
            r'(model|entity|schema|table)\s+(\w+)',
            r'(\w+)\s+(model|entity|schema|table)',
            r'class\s+(\w+)(?:Model|Entity|Schema)?'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    models.extend([m for m in match if m.lower() not in ['model', 'entity', 'schema', 'table']])
                else:
                    models.append(match)
        
        return list(set(models))[:10]  # Limit to 10 models
    
    def _extract_dependencies_heuristic(self, content: str) -> List[str]:
        """Extract external dependencies using heuristics"""
        deps = []
        patterns = [
            r'(redis|mongodb|postgresql|mysql|elasticsearch)',
            r'(react|vue|angular|express|fastapi|django)',
            r'(aws|azure|gcp|docker|kubernetes)',
            r'import\s+(\w+)',
            r'require\s*\(\s*[\'"]([^\'"]+)[\'"]'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            deps.extend(matches)
        
        return list(set(deps))[:10]  # Limit to 10 dependencies
    
    def _extract_requirements_heuristic(self, content: str) -> List[str]:
        """Extract technical requirements using heuristics"""
        requirements = []
        patterns = [
            r'(performance|security|scalability|availability|reliability)',
            r'(\d+)\s*(ms|seconds?|minutes?)\s*(response|latency)',
            r'(\d+)\s*(users?|requests?|connections?)',
            r'(ssl|https|encryption|authentication|authorization)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    requirements.append(' '.join(str(m) for m in match))
                else:
                    requirements.append(match)
        
        return list(set(requirements))[:8]  # Limit to 8 requirements
    
    def _parse_functional_areas_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse functional areas from AI response"""
        try:
            import json
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return self._create_default_functional_areas({})
    
    def _create_default_functional_areas(self, design_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create default functional areas when parsing fails"""
        return [
            {
                "name": "Core Backend",
                "description": "Main application backend and business logic",
                "components": design_analysis.get("system_components", [])[:3],
                "dependencies": [],
                "priority": "High",
                "complexity": "Medium"
            },
            {
                "name": "Data Layer",
                "description": "Database models and data access layer",
                "components": design_analysis.get("data_models", [])[:3],
                "dependencies": ["Core Backend"],
                "priority": "High",
                "complexity": "Medium"
            },
            {
                "name": "API Layer",
                "description": "REST API endpoints and external interfaces",
                "components": design_analysis.get("apis_interfaces", [])[:3],
                "dependencies": ["Core Backend"],
                "priority": "Medium",
                "complexity": "Simple"
            }
        ]
    
    def _parse_issues_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse issues from AI response"""
        try:
            import json
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        # Fallback to empty list - will trigger fallback issue creation
        return []
    
    def _create_fallback_issues_for_area(self, functional_area: Dict[str, Any]) -> List[DesignIssue]:
        """Create fallback issues when AI parsing fails"""
        area_name = functional_area.get('name', 'Unknown Area')
        
        return [
            DesignIssue(
                id=f"{area_name.lower().replace(' ', '_')}_setup_{uuid.uuid4().hex[:8]}",
                title=f"Setup {area_name}",
                description=f"Initial setup and scaffolding for {area_name}",
                issue_type="task",
                priority=Priority.HIGH,
                component=area_name,
                estimated_hours=4.0,
                labels=[area_name.lower(), "setup"],
                acceptance_criteria=[
                    f"{area_name} structure created",
                    "Basic configuration in place",
                    "Initial tests written"
                ]
            ),
            DesignIssue(
                id=f"{area_name.lower().replace(' ', '_')}_impl_{uuid.uuid4().hex[:8]}",
                title=f"Implement {area_name} core functionality",
                description=f"Implement the main functionality for {area_name}",
                issue_type="feature",
                priority=Priority.MEDIUM,
                component=area_name,
                estimated_hours=8.0,
                dependencies=[f"{area_name.lower().replace(' ', '_')}_setup"],
                labels=[area_name.lower(), "implementation"],
                acceptance_criteria=[
                    "Core functionality implemented",
                    "Unit tests pass",
                    "Code review completed"
                ]
            )
        ]
    
    def _assess_complexity(self, design_analysis: Dict[str, Any]) -> str:
        """Assess the complexity of the design document"""
        total_items = sum(len(items) if isinstance(items, list) else 0 
                         for items in design_analysis.values())
        
        if total_items > 30:
            return "High"
        elif total_items > 15:
            return "Medium"
        else:
            return "Low"
    
    def _issue_to_dict(self, issue: DesignIssue) -> Dict[str, Any]:
        """Convert DesignIssue to dictionary for JSON serialization"""
        return {
            "id": issue.id,
            "title": issue.title,
            "description": issue.description,
            "issue_type": issue.issue_type,
            "priority": issue.priority.value,
            "component": issue.component,
            "estimated_hours": issue.estimated_hours,
            "dependencies": issue.dependencies,
            "labels": issue.labels,
            "acceptance_criteria": issue.acceptance_criteria,
            "created_at": issue.created_at.isoformat()
        }