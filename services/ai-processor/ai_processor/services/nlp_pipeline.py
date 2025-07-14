import re
import logging
from typing import List, Dict, Any, Optional, Set
import asyncio
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class EntityExtraction:
    """Represents extracted entities from text"""
    persons: List[str]
    organizations: List[str]
    features: List[str]
    technical_terms: List[str]
    requirements: List[str]

class NLPPipeline:
    """NLP pipeline for text preprocessing and basic entity extraction"""
    
    def __init__(self):
        self.person_patterns = [
            r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',  # John Doe
            r'\b[A-Z]\. [A-Z][a-z]+\b',      # J. Smith
            r'\b[A-Z][a-z]+ [A-Z]\.\b',      # John D.
        ]
        
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        
        self.technical_terms = {
            'api', 'rest', 'graphql', 'database', 'mongodb', 'mysql', 'postgresql',
            'redis', 'cache', 'authentication', 'authorization', 'jwt', 'oauth',
            'microservice', 'docker', 'kubernetes', 'aws', 'azure', 'gcp',
            'frontend', 'backend', 'react', 'vue', 'angular', 'node', 'express',
            'python', 'java', 'typescript', 'javascript', 'html', 'css',
            'webhook', 'endpoint', 'service', 'component', 'module', 'library',
            'framework', 'sdk', 'cli', 'ui', 'ux', 'responsive', 'mobile',
            'testing', 'unit test', 'integration test', 'e2e', 'deployment',
            'ci/cd', 'pipeline', 'monitoring', 'logging', 'metrics', 'analytics'
        }
        
        self.requirement_indicators = [
            'must', 'should', 'shall', 'will', 'need to', 'required to',
            'have to', 'ought to', 'expected to', 'supposed to', 'able to',
            'requirement', 'feature', 'functionality', 'capability', 'support'
        ]
        
        self.feature_patterns = [
            r'(?i)(?:feature|functionality|capability|component|module|system)[\s:]*([^\n.!?]+)',
            r'(?i)(?:user can|users can|ability to|support for|implement|build|create|develop)[\s:]*([^\n.!?]+)',
            r'(?i)(?:as a .*, I want to|as a .*, I need to|as a .*, I should be able to)[\s:]*([^\n.!?]+)'
        ]
    
    async def preprocess_text(self, text: str) -> str:
        """
        Preprocess text for better analysis
        
        Args:
            text: Raw text to preprocess
            
        Returns:
            Preprocessed text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep sentence structure
        text = re.sub(r'[^\w\s.,!?;:()\-\[\]{}"]', ' ', text)
        
        # Normalize line breaks
        text = re.sub(r'\n+', '\n', text)
        
        # Remove empty lines
        text = re.sub(r'\n\s*\n', '\n', text)
        
        return text.strip()
    
    async def extract_entities(self, text: str) -> EntityExtraction:
        """
        Extract entities from text using pattern matching
        
        Args:
            text: Text to analyze
            
        Returns:
            EntityExtraction object with extracted entities
        """
        persons = self._extract_persons(text)
        organizations = self._extract_organizations(text)
        features = self._extract_features(text)
        technical_terms = self._extract_technical_terms(text)
        requirements = self._extract_requirements(text)
        
        return EntityExtraction(
            persons=persons,
            organizations=organizations,
            features=features,
            technical_terms=technical_terms,
            requirements=requirements
        )
    
    def _extract_persons(self, text: str) -> List[str]:
        """Extract person names from text"""
        persons = set()
        
        # Extract email addresses and get names from them
        emails = re.findall(self.email_pattern, text)
        for email in emails:
            username = email.split('@')[0]
            # Convert username to potential name
            name_parts = re.split(r'[._-]', username)
            if len(name_parts) >= 2:
                name = ' '.join(part.capitalize() for part in name_parts[:2])
                persons.add(name)
        
        # Extract names using patterns
        for pattern in self.person_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                # Filter out common non-names
                if not any(word.lower() in match.lower() for word in ['user', 'admin', 'system', 'api', 'service', 'team', 'group']):
                    persons.add(match)
        
        return list(persons)
    
    def _extract_organizations(self, text: str) -> List[str]:
        """Extract organization names from text"""
        organizations = set()
        
        # Look for common organization patterns
        org_patterns = [
            r'\b[A-Z][a-z]+ (?:Inc|Corp|LLC|Ltd|Company|Corporation|Solutions|Systems|Technologies)\b',
            r'\b[A-Z]{2,} [A-Z][a-z]+\b',  # IBM Watson, AWS Lambda
            r'\b[A-Z][a-z]+ [A-Z][a-z]+ (?:Inc|Corp|LLC|Ltd)\b'
        ]
        
        for pattern in org_patterns:
            matches = re.findall(pattern, text)
            organizations.update(matches)
        
        return list(organizations)
    
    def _extract_features(self, text: str) -> List[str]:
        """Extract feature descriptions from text"""
        features = set()
        
        for pattern in self.feature_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                # Clean up the match
                feature = match.strip()
                if len(feature) > 10 and len(feature) < 200:  # Reasonable length
                    features.add(feature)
        
        return list(features)
    
    def _extract_technical_terms(self, text: str) -> List[str]:
        """Extract technical terms from text"""
        found_terms = set()
        text_lower = text.lower()
        
        for term in self.technical_terms:
            # Look for whole word matches
            pattern = r'\b' + re.escape(term) + r'\b'
            if re.search(pattern, text_lower):
                found_terms.add(term)
        
        # Look for additional technical patterns
        tech_patterns = [
            r'\b[A-Z][a-z]*[A-Z][a-z]*\b',  # CamelCase
            r'\b\w+\.\w+\b',  # package.module
            r'\b\w+:\/\/\w+\b',  # protocols
            r'\b\w+_\w+\b',  # snake_case
        ]
        
        for pattern in tech_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if len(match) > 3 and match.lower() not in ['the', 'and', 'for', 'with']:
                    found_terms.add(match.lower())
        
        return list(found_terms)
    
    def _extract_requirements(self, text: str) -> List[str]:
        """Extract requirement statements from text"""
        requirements = set()
        
        # Split text into sentences
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20:  # Skip very short sentences
                continue
                
            # Check if sentence contains requirement indicators
            sentence_lower = sentence.lower()
            for indicator in self.requirement_indicators:
                if indicator in sentence_lower:
                    requirements.add(sentence)
                    break
        
        return list(requirements)
    
    async def tokenize_text(self, text: str) -> List[str]:
        """
        Tokenize text into words
        
        Args:
            text: Text to tokenize
            
        Returns:
            List of tokens
        """
        # Simple tokenization - split on whitespace and punctuation
        tokens = re.findall(r'\w+', text.lower())
        return tokens
    
    async def extract_sentences(self, text: str) -> List[str]:
        """
        Extract sentences from text
        
        Args:
            text: Text to process
            
        Returns:
            List of sentences
        """
        # Split on sentence boundaries
        sentences = re.split(r'[.!?]+', text)
        
        # Clean up sentences
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:  # Filter out very short sentences
                cleaned_sentences.append(sentence)
        
        return cleaned_sentences
    
    async def extract_keywords(self, text: str, num_keywords: int = 20) -> List[str]:
        """
        Extract keywords from text using simple frequency analysis
        
        Args:
            text: Text to analyze
            num_keywords: Number of keywords to return
            
        Returns:
            List of keywords
        """
        # Tokenize text
        tokens = await self.tokenize_text(text)
        
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i',
            'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'
        }
        
        filtered_tokens = [token for token in tokens if token not in stop_words and len(token) > 2]
        
        # Count frequency
        word_freq = {}
        for token in filtered_tokens:
            word_freq[token] = word_freq.get(token, 0) + 1
        
        # Sort by frequency and return top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        keywords = [word for word, freq in sorted_words[:num_keywords]]
        
        return keywords
    
    async def analyze_sentiment(self, text: str) -> str:
        """
        Basic sentiment analysis using keyword matching
        
        Args:
            text: Text to analyze
            
        Returns:
            Sentiment: 'positive', 'negative', or 'neutral'
        """
        positive_words = {
            'good', 'great', 'excellent', 'amazing', 'awesome', 'fantastic',
            'wonderful', 'perfect', 'best', 'love', 'like', 'enjoy', 'happy',
            'pleased', 'satisfied', 'impressed', 'successful', 'effective',
            'efficient', 'useful', 'valuable', 'important', 'significant'
        }
        
        negative_words = {
            'bad', 'terrible', 'awful', 'horrible', 'worst', 'hate', 'dislike',
            'angry', 'frustrated', 'disappointed', 'sad', 'annoyed', 'difficult',
            'hard', 'challenging', 'problem', 'issue', 'bug', 'error', 'fail',
            'failure', 'broken', 'wrong', 'poor', 'slow', 'expensive'
        }
        
        tokens = await self.tokenize_text(text)
        
        positive_count = sum(1 for token in tokens if token in positive_words)
        negative_count = sum(1 for token in tokens if token in negative_words)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    async def extract_user_stories(self, text: str) -> List[str]:
        """
        Extract user story patterns from text
        
        Args:
            text: Text to analyze
            
        Returns:
            List of potential user stories
        """
        user_story_patterns = [
            r'(?i)as a ([^,]+), I want to ([^,]+), so that ([^.!?]+)',
            r'(?i)as a ([^,]+), I want to ([^.!?]+)',
            r'(?i)as a ([^,]+), I need to ([^.!?]+)',
            r'(?i)as a ([^,]+), I should be able to ([^.!?]+)'
        ]
        
        stories = []
        for pattern in user_story_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    story = f"As a {match[0]}, I want to {match[1]}"
                    if len(match) > 2:
                        story += f", so that {match[2]}"
                    stories.append(story)
        
        return stories
    
    async def extract_acceptance_criteria(self, text: str) -> List[str]:
        """
        Extract acceptance criteria patterns from text
        
        Args:
            text: Text to analyze
            
        Returns:
            List of potential acceptance criteria
        """
        ac_patterns = [
            r'(?i)given ([^,]+), when ([^,]+), then ([^.!?]+)',
            r'(?i)scenario: ([^.!?]+)',
            r'(?i)acceptance criteria:?\s*([^.!?]+)',
            r'(?i)criteria:?\s*([^.!?]+)'
        ]
        
        criteria = []
        for pattern in ac_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    criterion = f"Given {match[0]}, when {match[1]}, then {match[2]}"
                    criteria.append(criterion)
                else:
                    criteria.append(match)
        
        return criteria 