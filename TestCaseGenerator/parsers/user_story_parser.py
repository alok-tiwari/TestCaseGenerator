"""Parser for user stories in various formats."""

import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ParsedUserStory:
    """Structured representation of a parsed user story."""
    
    persona: str
    action: str
    value: str
    original_text: str
    confidence: float  # 0.0 to 1.0
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "persona": self.persona,
            "action": self.action,
            "value": self.value,
            "original_text": self.original_text,
            "confidence": self.confidence,
            "metadata": self.metadata
        }


class UserStoryParser:
    """Parser for user stories in various formats."""
    
    def __init__(self):
        """Initialize the parser with regex patterns."""
        # Standard user story patterns
        self.story_patterns = [
            # Standard format: As a... I want to... So that...
            r"As\s+a\s+(.+?)\s+I\s+want\s+to\s+(.+?)\s+So\s+that\s+(.+)",
            # Alternative format: As a... I want... So that...
            r"As\s+a\s+(.+?)\s+I\s+want\s+(.+?)\s+So\s+that\s+(.+)",
            # With line breaks
            r"As\s+a\s+(.+?)\s*\n\s*I\s+want\s+to\s+(.+?)\s*\n\s*So\s+that\s+(.+)",
            # With bullet points
            r"•\s*As\s+a\s+(.+?)\s*•\s*I\s+want\s+to\s+(.+?)\s*•\s*So\s+that\s+(.+)",
        ]
        
        # Alternative formats
        self.alternative_patterns = [
            # Who-What-Why format
            r"(.+?)\s+needs\s+(.+?)\s+because\s+(.+)",
            r"(.+?)\s+requires\s+(.+?)\s+to\s+(.+)",
            r"(.+?)\s+must\s+be\s+able\s+to\s+(.+?)\s+in\s+order\s+to\s+(.+)",
        ]
        
        # Persona patterns
        self.persona_patterns = [
            r"user",
            r"customer",
            r"admin",
            r"manager",
            r"developer",
            r"tester",
            r"guest",
            r"member",
            r"subscriber",
            r"visitor"
        ]
        
        # Action patterns
        self.action_patterns = [
            r"want\s+to",
            r"need\s+to",
            r"must\s+be\s+able\s+to",
            r"should\s+be\s+able\s+to",
            r"can",
            r"able\s+to"
        ]
        
        # Value patterns
        self.value_patterns = [
            r"so\s+that",
            r"because",
            r"in\s+order\s+to",
            r"to",
            r"for"
        ]
    
    def parse_user_story(self, story_text: str) -> Optional[ParsedUserStory]:
        """Parse a user story into structured format."""
        
        if not story_text or not story_text.strip():
            return None
        
        # Try standard user story format first
        parsed = self._parse_standard_format(story_text)
        if parsed:
            return parsed
        
        # Try alternative formats
        parsed = self._parse_alternative_format(story_text)
        if parsed:
            return parsed
        
        # Try to extract components from unstructured text
        parsed = self._parse_unstructured_format(story_text)
        if parsed:
            return parsed
        
        return None
    
    def parse_multiple_stories(self, stories_text: str) -> List[ParsedUserStory]:
        """Parse multiple user stories from text."""
        
        if not stories_text or not stories_text.strip():
            return []
        
        # Split by common separators
        separators = [
            "\n\n",  # Double line breaks
            "\n---\n",  # Markdown-style separators
            "\n***\n",
            "\n===\n",
            "\n\n---\n\n"
        ]
        
        stories = []
        for separator in separators:
            if separator in stories_text:
                story_parts = stories_text.split(separator)
                break
        else:
            # No separators found, treat as single story
            story_parts = [stories_text]
        
        for story_part in story_parts:
            story_part = story_part.strip()
            if story_part:
                parsed = self.parse_user_story(story_part)
                if parsed:
                    stories.append(parsed)
        
        return stories
    
    def _parse_standard_format(self, text: str) -> Optional[ParsedUserStory]:
        """Parse standard As a... I want to... So that... format."""
        
        for pattern in self.story_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                persona = match.group(1).strip()
                action = match.group(2).strip()
                value = match.group(3).strip()
                
                if persona and action and value:
                    confidence = self._calculate_confidence(persona, action, value)
                    metadata = self._extract_metadata(text)
                    
                    return ParsedUserStory(
                        persona=persona,
                        action=action,
                        value=value,
                        original_text=text,
                        confidence=confidence,
                        metadata=metadata
                    )
        
        return None
    
    def _parse_alternative_format(self, text: str) -> Optional[ParsedUserStory]:
        """Parse alternative user story formats."""
        
        for pattern in self.alternative_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                persona = match.group(1).strip()
                action = match.group(2).strip()
                value = match.group(3).strip()
                
                if persona and action and value:
                    # Normalize action to "I want to..." format
                    action = self._normalize_action(action)
                    value = self._normalize_value(value)
                    
                    confidence = self._calculate_confidence(persona, action, value) * 0.8
                    metadata = self._extract_metadata(text)
                    
                    return ParsedUserStory(
                        persona=persona,
                        action=action,
                        value=value,
                        original_text=text,
                        confidence=confidence,
                        metadata=metadata
                    )
        
        return None
    
    def _parse_unstructured_format(self, text: str) -> Optional[ParsedUserStory]:
        """Parse unstructured text to extract user story components."""
        
        lines = text.split('\n')
        persona = None
        action = None
        value = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Try to identify persona
            if not persona and self._looks_like_persona(line):
                persona = line
                continue
            
            # Try to identify action
            if not action and self._looks_like_action(line):
                action = line
                continue
            
            # Try to identify value
            if not value and self._looks_like_value(line):
                value = line
                continue
        
        if persona and action and value:
            confidence = self._calculate_confidence(persona, action, value) * 0.6
            metadata = self._extract_metadata(text)
            
            return ParsedUserStory(
                persona=persona,
                action=action,
                value=value,
                original_text=text,
                confidence=confidence,
                metadata=metadata
            )
        
        return None
    
    def _looks_like_persona(self, text: str) -> bool:
        """Check if text looks like a persona description."""
        text_lower = text.lower()
        
        # Check for persona patterns
        for pattern in self.persona_patterns:
            if pattern in text_lower:
                return True
        
        # Check for "As a..." format
        if re.match(r"^as\s+a\s+", text_lower):
            return True
        
        return False
    
    def _looks_like_action(self, text: str) -> bool:
        """Check if text looks like an action description."""
        text_lower = text.lower()
        
        # Check for action patterns
        for pattern in self.action_patterns:
            if pattern in text_lower:
                return True
        
        # Check for action verbs
        action_verbs = [
            "click", "enter", "select", "navigate", "submit", "upload", "download",
            "create", "edit", "delete", "view", "search", "filter", "sort"
        ]
        
        for verb in action_verbs:
            if verb in text_lower:
                return True
        
        return False
    
    def _looks_like_value(self, text: str) -> bool:
        """Check if text looks like a value description."""
        text_lower = text.lower()
        
        # Check for value patterns
        for pattern in self.value_patterns:
            if pattern in text_lower:
                return True
        
        # Check for benefit indicators
        benefit_words = [
            "improve", "enhance", "increase", "reduce", "save", "efficient",
            "better", "faster", "easier", "secure", "reliable"
        ]
        
        for word in benefit_words:
            if word in text_lower:
                return True
        
        return False
    
    def _normalize_action(self, action: str) -> str:
        """Normalize action to standard format."""
        action = action.strip()
        
        # Remove common prefixes
        prefixes_to_remove = [
            "needs", "requires", "must be able to", "should be able to"
        ]
        
        for prefix in prefixes_to_remove:
            if action.lower().startswith(prefix.lower()):
                action = action[len(prefix):].strip()
                break
        
        # Ensure it starts with "I want to"
        if not action.lower().startswith("i want to"):
            action = f"I want to {action}"
        
        return action
    
    def _normalize_value(self, value: str) -> str:
        """Normalize value to standard format."""
        value = value.strip()
        
        # Ensure it starts with "So that"
        if not value.lower().startswith("so that"):
            value = f"So that {value}"
        
        return value
    
    def _calculate_confidence(self, persona: str, action: str, value: str) -> float:
        """Calculate confidence score for parsed components."""
        confidence = 0.5  # Base confidence
        
        # Check persona quality
        if self._is_well_formed_persona(persona):
            confidence += 0.2
        
        # Check action quality
        if self._is_well_formed_action(action):
            confidence += 0.2
        
        # Check value quality
        if self._is_well_formed_value(value):
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _is_well_formed_persona(self, persona: str) -> bool:
        """Check if persona is well-formed."""
        return (
            len(persona.split()) >= 2 and
            any(pattern in persona.lower() for pattern in self.persona_patterns)
        )
    
    def _is_well_formed_action(self, action: str) -> bool:
        """Check if action is well-formed."""
        return (
            len(action.split()) >= 3 and
            any(pattern in action.lower() for pattern in self.action_patterns)
        )
    
    def _is_well_formed_value(self, value: str) -> bool:
        """Check if value is well-formed."""
        return (
            len(value.split()) >= 3 and
            any(pattern in value.lower() for pattern in self.value_patterns)
        )
    
    def _extract_metadata(self, text: str) -> Dict[str, Any]:
        """Extract metadata from user story text."""
        metadata = {}
        
        # Extract tags/labels
        tags = re.findall(r'#(\w+)', text)
        if tags:
            metadata['tags'] = tags
        
        # Extract priority indicators
        priority_indicators = {
            'high': ['urgent', 'critical', 'important', 'high priority'],
            'medium': ['normal', 'standard', 'medium priority'],
            'low': ['low priority', 'nice to have', 'optional']
        }
        
        text_lower = text.lower()
        for priority, indicators in priority_indicators.items():
            if any(indicator in text_lower for indicator in indicators):
                metadata['priority'] = priority
                break
        
        # Extract story points if present
        story_points_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:story\s+)?points?', text, re.IGNORECASE)
        if story_points_match:
            metadata['story_points'] = float(story_points_match.group(1))
        
        return metadata
    
    def validate_user_story(self, story: ParsedUserStory) -> Dict[str, Any]:
        """Validate a parsed user story."""
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": []
        }
        
        # Check persona
        if not story.persona or len(story.persona.strip()) < 3:
            validation_result["errors"].append("Persona is too short or missing")
            validation_result["is_valid"] = False
        
        # Check action
        if not story.action or len(story.action.strip()) < 5:
            validation_result["errors"].append("Action is too short or missing")
            validation_result["is_valid"] = False
        
        # Check value
        if not story.value or len(story.value.strip()) < 5:
            validation_result["errors"].append("Value is too short or missing")
            validation_result["is_valid"] = False
        
        # Check confidence
        if story.confidence < 0.5:
            validation_result["warnings"].append("Low confidence in parsing - manual review recommended")
        
        # Suggestions for improvement
        if story.confidence < 0.8:
            validation_result["suggestions"].append("Consider using standard 'As a... I want to... So that...' format")
        
        return validation_result
