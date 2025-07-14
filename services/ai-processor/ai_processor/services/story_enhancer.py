"""
Story enhancer service following Single Responsibility Principle.
Only responsible for enhancing user stories with acceptance criteria and story point estimates.
"""

import json
import logging
from typing import List, Dict, Any, Optional
from ..core.interfaces import StoryEnhancerProtocol, AIClientProtocol
from ..core.config import config
from ..core.error_handler import handle_errors, AIError
from ..models.schemas import UserStory, AcceptanceCriteria, StoryPointEstimate

logger = logging.getLogger(__name__)


class StoryEnhancer:
    """
    Story enhancer service that adds acceptance criteria and estimates to user stories.
    Follows Single Responsibility Principle - only handles story enhancement.
    """
    
    def __init__(self, ai_client: AIClientProtocol):
        self.ai_client = ai_client
        self.model = config.get_ai_model()
        self.temperature = config.get_ai_temperature()
        self.story_point_scale = config.get_story_point_scale()
    
    @handle_errors("ai")
    async def generate_acceptance_criteria(self, story: UserStory) -> List[AcceptanceCriteria]:
        """Generate acceptance criteria for a user story"""
        logger.info(f"Generating acceptance criteria for story: {story.title}")
        
        prompt = self._get_acceptance_criteria_prompt(story)
        
        try:
            response = await self.ai_client.get_structured_response(
                model=self.model,
                prompt=prompt,
                response_format="json",
                temperature=self.temperature
            )
            
            return self._parse_acceptance_criteria_response(response)
        
        except Exception as e:
            raise AIError(f"Failed to generate acceptance criteria: {str(e)}", self.model, {"story_title": story.title})
    
    @handle_errors("ai")
    async def estimate_story_points(
        self,
        story_title: str,
        story_description: str,
        acceptance_criteria: List[str]
    ) -> StoryPointEstimate:
        """Estimate story points for a user story"""
        logger.info(f"Estimating story points for: {story_title}")
        
        prompt = self._get_story_points_prompt(story_title, story_description, acceptance_criteria)
        
        try:
            response = await self.ai_client.get_structured_response(
                model=self.model,
                prompt=prompt,
                response_format="json",
                temperature=self.temperature
            )
            
            return self._parse_story_points_response(response)
        
        except Exception as e:
            raise AIError(f"Failed to estimate story points: {str(e)}", self.model, {"story_title": story_title})
    
    async def enhance_story(self, story: UserStory) -> UserStory:
        """Enhance a story with acceptance criteria and story point estimate"""
        logger.info(f"Enhancing story: {story.title}")
        
        # Generate acceptance criteria
        story.acceptance_criteria = await self.generate_acceptance_criteria(story)
        
        # Estimate story points
        criteria_text = [f"{ac.scenario}: {' '.join(ac.steps)}" for ac in story.acceptance_criteria]
        estimate = await self.estimate_story_points(
            story.title,
            story.description,
            criteria_text
        )
        story.story_points = estimate.story_points
        
        return story
    
    async def enhance_multiple_stories(self, stories: List[UserStory]) -> List[UserStory]:
        """Enhance multiple stories efficiently"""
        logger.info(f"Enhancing {len(stories)} stories")
        
        enhanced_stories = []
        for story in stories:
            try:
                enhanced_story = await self.enhance_story(story)
                enhanced_stories.append(enhanced_story)
            except Exception as e:
                logger.warning(f"Failed to enhance story '{story.title}': {e}")
                # Add the story without enhancement rather than losing it
                enhanced_stories.append(story)
        
        return enhanced_stories
    
    def _get_acceptance_criteria_prompt(self, story: UserStory) -> str:
        """Get prompt for acceptance criteria generation"""
        return f"""
        You are an expert QA analyst. Generate comprehensive acceptance criteria for this user story:
        
        Title: {story.title}
        Description: {story.description}
        Priority: {story.priority}
        
        Generate 3-5 acceptance criteria in Gherkin syntax. Each should include:
        - scenario: Brief description of the scenario
        - steps: Array of Given-When-Then statements
        
        Include scenarios for:
        - Happy path (successful completion)
        - Error handling (invalid inputs, system errors)
        - Edge cases (boundary conditions)
        - User experience considerations
        
        Return a JSON array of objects with 'scenario' and 'steps' fields.
        Example format:
        [
            {{
                "scenario": "User successfully completes action",
                "steps": [
                    "Given the user is authenticated",
                    "When they perform the action", 
                    "Then they see success confirmation"
                ]
            }}
        ]
        
        Return only valid JSON.
        """
    
    def _get_story_points_prompt(self, title: str, description: str, acceptance_criteria: List[str]) -> str:
        """Get prompt for story point estimation"""
        criteria_text = "\n".join(f"- {criteria}" for criteria in acceptance_criteria)
        scale_text = ", ".join(str(point) for point in self.story_point_scale)
        
        return f"""
        You are an expert software estimator. Estimate story points for this user story:
        
        Title: {title}
        Description: {description}
        
        Acceptance Criteria:
        {criteria_text}
        
        Available story point scale: {scale_text}
        
        Consider these factors:
        - Complexity of implementation
        - Amount of code to be written
        - Risk and uncertainty
        - Amount of testing required
        - Integration complexity
        - Learning curve for new technologies
        
        Provide your estimate as a JSON object with:
        {{
            "story_points": <number from the scale>,
            "confidence": <percentage 0-100>,
            "reasoning": "Detailed explanation of the estimate",
            "risks": ["Array of potential risks"],
            "assumptions": ["Array of assumptions made"]
        }}
        
        Return only valid JSON.
        """
    
    def _parse_acceptance_criteria_response(self, response: Dict[str, Any]) -> List[AcceptanceCriteria]:
        """Parse AI response into AcceptanceCriteria objects"""
        criteria = []
        
        if isinstance(response, list):
            criteria_data = response
        else:
            criteria_data = response.get("acceptance_criteria", response.get("criteria", []))
        
        for item in criteria_data:
            try:
                criterion = AcceptanceCriteria(
                    scenario=item.get("scenario", ""),
                    steps=item.get("steps", [])
                )
                criteria.append(criterion)
            except Exception as e:
                logger.warning(f"Failed to parse acceptance criterion: {item}, error: {e}")
                continue
        
        # Ensure we have at least one criterion
        if not criteria:
            criteria.append(AcceptanceCriteria(
                scenario="Basic functionality test",
                steps=[
                    "Given the system is available",
                    "When the user performs the described action",
                    "Then the expected outcome is achieved"
                ]
            ))
        
        return criteria
    
    def _parse_story_points_response(self, response: Dict[str, Any]) -> StoryPointEstimate:
        """Parse AI response into StoryPointEstimate object"""
        try:
            story_points = response.get("story_points", 3)
            
            # Ensure story points is from our scale
            if story_points not in self.story_point_scale:
                # Find the closest value in our scale
                story_points = min(self.story_point_scale, key=lambda x: abs(x - story_points))
            
            return StoryPointEstimate(
                story_points=story_points,
                confidence=response.get("confidence", 0.7),
                reasoning=response.get("reasoning", "Estimate based on story complexity"),
                complexity_factors=response.get("risks", []) + response.get("assumptions", []),
                similar_stories=response.get("similar_stories", [])
            )
        
        except Exception as e:
            logger.warning(f"Failed to parse story points response: {response}, error: {e}")
            return StoryPointEstimate(
                story_points=3,
                confidence=0.5,
                reasoning="Default estimate due to parsing error",
                complexity_factors=["Unable to parse AI response"],
                similar_stories=[]
            ) 