"""
Jira Issue Creator - Service for creating Jira issues from generated development issues.

This service bridges the gap between AI-generated development issues and Jira project management.
"""

import logging
import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from ..core.error_handler import handle_errors
from ..models.schemas import DevelopmentIssue, IssueType, Priority

logger = logging.getLogger(__name__)


class JiraIssueCreator:
    """
    Service for creating Jira issues from AI-generated development issues.
    """
    
    def __init__(self, jira_base_url: str, username: str, api_token: str):
        self.jira_base_url = jira_base_url.rstrip('/')
        self.username = username
        self.api_token = api_token
        self.session = None
        
        # Mapping from our issue types to Jira issue types
        self.issue_type_mapping = {
            IssueType.FEATURE: "Story",
            IssueType.TASK: "Task", 
            IssueType.BUG: "Bug",
            IssueType.RESEARCH: "Spike",
            IssueType.DOCUMENTATION: "Task",
            IssueType.TESTING: "Test",
            IssueType.INFRASTRUCTURE: "Task"
        }
        
        # Priority mapping
        self.priority_mapping = {
            Priority.HIGH: "High",
            Priority.MEDIUM: "Medium", 
            Priority.LOW: "Low"
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = httpx.AsyncClient(
            auth=(self.username, self.api_token),
            headers={"Content-Type": "application/json"},
            timeout=30.0
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.aclose()
    
    @handle_errors("jira_creation")
    async def create_issues_in_jira(
        self,
        issues: List[DevelopmentIssue],
        project_key: str,
        epic_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create multiple issues in Jira
        
        Args:
            issues: List of development issues to create
            project_key: Jira project key
            epic_name: Optional epic name to group issues under
            
        Returns:
            Dictionary with creation results
        """
        logger.info(f"Creating {len(issues)} issues in Jira project {project_key}")
        
        if not self.session:
            raise RuntimeError("JiraIssueCreator must be used as async context manager")
        
        results = {
            "success": True,
            "created_issues": [],
            "failed_issues": [],
            "epic_key": None,
            "total_created": 0,
            "total_failed": 0
        }
        
        # Create epic if specified
        epic_key = None
        if epic_name:
            epic_key = await self._create_epic(project_key, epic_name)
            results["epic_key"] = epic_key
        
        # Create issues
        for issue in issues:
            try:
                jira_issue = await self._create_single_issue(
                    issue, project_key, epic_key
                )
                results["created_issues"].append({
                    "id": issue.id,
                    "jira_key": jira_issue["key"],
                    "jira_id": jira_issue["id"],
                    "title": issue.title
                })
                results["total_created"] += 1
                
            except Exception as e:
                logger.error(f"Failed to create issue {issue.id}: {e}")
                results["failed_issues"].append({
                    "id": issue.id,
                    "title": issue.title,
                    "error": str(e)
                })
                results["total_failed"] += 1
                results["success"] = False
        
        logger.info(f"Jira creation completed: {results['total_created']} created, {results['total_failed']} failed")
        return results
    
    async def _create_epic(self, project_key: str, epic_name: str) -> Optional[str]:
        """Create an epic in Jira"""
        try:
            epic_data = {
                "fields": {
                    "project": {"key": project_key},
                    "summary": epic_name,
                    "description": f"Epic created for design document issues - {epic_name}",
                    "issuetype": {"name": "Epic"},
                    "customfield_10011": epic_name  # Epic Name field (may vary by Jira instance)
                }
            }
            
            response = await self.session.post(
                f"{self.jira_base_url}/rest/api/2/issue",
                json=epic_data
            )
            
            if response.status_code == 201:
                epic = response.json()
                logger.info(f"Created epic: {epic['key']}")
                return epic["key"]
            else:
                logger.warning(f"Failed to create epic: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.warning(f"Failed to create epic: {e}")
            return None
    
    async def _create_single_issue(
        self, 
        issue: DevelopmentIssue, 
        project_key: str, 
        epic_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a single issue in Jira"""
        
        # Build description with acceptance criteria
        description = issue.description
        if issue.acceptance_criteria:
            description += "\n\n*Acceptance Criteria:*\n"
            for i, criteria in enumerate(issue.acceptance_criteria, 1):
                description += f"{i}. {criteria}\n"
        
        # Add estimated hours to description
        description += f"\n*Estimated Hours:* {issue.estimated_hours}"
        
        # Build issue data
        issue_data = {
            "fields": {
                "project": {"key": project_key},
                "summary": issue.title,
                "description": description,
                "issuetype": {"name": self.issue_type_mapping.get(issue.issue_type, "Task")},
                "priority": {"name": self.priority_mapping.get(issue.priority, "Medium")},
                "labels": issue.labels
            }
        }
        
        # Add epic link if epic exists
        if epic_key:
            issue_data["fields"]["customfield_10014"] = epic_key  # Epic Link field (may vary)
        
        # Add component if specified
        if issue.component:
            issue_data["fields"]["components"] = [{"name": issue.component}]
        
        # Create the issue
        response = await self.session.post(
            f"{self.jira_base_url}/rest/api/2/issue",
            json=issue_data
        )
        
        if response.status_code == 201:
            created_issue = response.json()
            logger.debug(f"Created Jira issue: {created_issue['key']} - {issue.title}")
            return created_issue
        else:
            error_msg = f"Failed to create issue: {response.status_code} - {response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    @handle_errors("jira_linking")
    async def link_dependent_issues(
        self,
        created_issues: List[Dict[str, Any]],
        original_issues: List[DevelopmentIssue]
    ) -> Dict[str, Any]:
        """
        Create issue links for dependent issues in Jira
        
        Args:
            created_issues: List of created Jira issues with keys
            original_issues: Original development issues with dependencies
            
        Returns:
            Results of linking operation
        """
        logger.info("Creating issue links for dependencies")
        
        if not self.session:
            raise RuntimeError("JiraIssueCreator must be used as async context manager")
        
        # Build mapping from issue ID to Jira key
        id_to_key = {
            created["id"]: created["jira_key"] 
            for created in created_issues
        }
        
        results = {
            "success": True,
            "links_created": 0,
            "links_failed": 0,
            "failed_links": []
        }
        
        for original_issue in original_issues:
            if not original_issue.dependencies:
                continue
            
            source_key = id_to_key.get(original_issue.id)
            if not source_key:
                continue
            
            for dependency_id in original_issue.dependencies:
                target_key = id_to_key.get(dependency_id)
                if not target_key:
                    continue
                
                try:
                    await self._create_issue_link(source_key, target_key, "Blocks")
                    results["links_created"] += 1
                    
                except Exception as e:
                    logger.error(f"Failed to link {source_key} -> {target_key}: {e}")
                    results["links_failed"] += 1
                    results["failed_links"].append({
                        "source": source_key,
                        "target": target_key,
                        "error": str(e)
                    })
                    results["success"] = False
        
        logger.info(f"Issue linking completed: {results['links_created']} created, {results['links_failed']} failed")
        return results
    
    async def _create_issue_link(
        self, 
        source_key: str, 
        target_key: str, 
        link_type: str
    ):
        """Create a link between two Jira issues"""
        
        link_data = {
            "type": {"name": link_type},
            "inwardIssue": {"key": target_key},
            "outwardIssue": {"key": source_key}
        }
        
        response = await self.session.post(
            f"{self.jira_base_url}/rest/api/2/issueLink",
            json=link_data
        )
        
        if response.status_code != 201:
            error_msg = f"Failed to create issue link: {response.status_code} - {response.text}"
            raise Exception(error_msg)
    
    async def get_project_info(self, project_key: str) -> Dict[str, Any]:
        """Get information about a Jira project"""
        if not self.session:
            raise RuntimeError("JiraIssueCreator must be used as async context manager")
        
        try:
            response = await self.session.get(
                f"{self.jira_base_url}/rest/api/2/project/{project_key}"
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Project not found: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Failed to get project info for {project_key}: {e}")
            raise
    
    async def get_available_issue_types(self, project_key: str) -> List[Dict[str, Any]]:
        """Get available issue types for a project"""
        if not self.session:
            raise RuntimeError("JiraIssueCreator must be used as async context manager")
        
        try:
            response = await self.session.get(
                f"{self.jira_base_url}/rest/api/2/issue/createmeta?projectKeys={project_key}&expand=projects.issuetypes"
            )
            
            if response.status_code == 200:
                data = response.json()
                if data["projects"]:
                    return data["projects"][0].get("issuetypes", [])
                return []
            else:
                raise Exception(f"Failed to get issue types: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Failed to get issue types for {project_key}: {e}")
            raise


# Utility functions for Jira integration

async def create_jira_issues_from_design(
    issues: List[DevelopmentIssue],
    jira_config: Dict[str, str],
    project_key: str,
    epic_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function to create Jira issues from design document issues
    
    Args:
        issues: List of development issues
        jira_config: Jira configuration (base_url, username, api_token)
        project_key: Jira project key
        epic_name: Optional epic name
        
    Returns:
        Creation results
    """
    async with JiraIssueCreator(
        jira_config["base_url"],
        jira_config["username"], 
        jira_config["api_token"]
    ) as creator:
        
        # Create issues
        creation_results = await creator.create_issues_in_jira(
            issues, project_key, epic_name
        )
        
        # Link dependent issues if any were created
        if creation_results["created_issues"]:
            linking_results = await creator.link_dependent_issues(
                creation_results["created_issues"],
                issues
            )
            creation_results["linking_results"] = linking_results
        
        return creation_results


def validate_jira_config(config: Dict[str, str]) -> bool:
    """Validate Jira configuration"""
    required_fields = ["base_url", "username", "api_token"]
    return all(field in config and config[field] for field in required_fields)