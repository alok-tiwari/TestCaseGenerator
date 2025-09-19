"""Parser for acceptance criteria in different formats."""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ParsedCriteria:
    """Structured representation of parsed acceptance criteria."""
    
    given: str
    when: str
    then: str
    original_text: str
    confidence: float  # 0.0 to 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "given": self.given,
            "when": self.when,
            "then": self.then,
            "original_text": self.original_text,
            "confidence": self.confidence
        }


class AcceptanceCriteriaParser:
    """Parser for acceptance criteria in various formats."""
    
    def __init__(self):
        """Initialize the parser with regex patterns."""
        # Given-When-Then patterns
        self.gwt_patterns = [
            # Standard GWT format
            r"Given\s+(.+?)\s+When\s+(.+?)\s+Then\s+(.+)",
            # GWT with commas
            r"Given\s+(.+?),\s*When\s+(.+?),\s*Then\s+(.+)",
            # GWT with line breaks
            r"Given\s+(.+?)\s*\n\s*When\s+(.+?)\s*\n\s*Then\s+(.+)",
            # GWT with bullet points
            r"•\s*Given\s+(.+?)\s*•\s*When\s+(.+?)\s*•\s*Then\s+(.+)",
        ]
        
        # Bullet point patterns
        self.bullet_patterns = [
            r"^[\s•\-\*]\s*(.+)",
            r"^\d+\.\s*(.+)",
        ]
        
        # Action-result patterns
        self.action_result_patterns = [
            r"(.+?)\s+should\s+(.+)",
            r"(.+?)\s+will\s+(.+)",
            r"(.+?)\s+must\s+(.+)",
            r"(.+?)\s+can\s+(.+)",
        ]
    
    def parse_criteria(self, criteria_text: str) -> List[ParsedCriteria]:
        """Parse acceptance criteria text into structured format."""
        
        if not criteria_text or not criteria_text.strip():
            return []
        
        # Clean and normalize input first
        criteria_text = self._preprocess_input(criteria_text)
        
        # Try to parse as Given-When-Then format first
        gwt_criteria = self._parse_gwt_format(criteria_text)
        if gwt_criteria:
            return gwt_criteria
        
        # Try to parse as bullet points
        bullet_criteria = self._parse_bullet_format(criteria_text)
        if bullet_criteria:
            return bullet_criteria
        
        # Try to parse as action-result format
        action_result_criteria = self._parse_action_result_format(criteria_text)
        if action_result_criteria:
            return action_result_criteria
        
        # Fallback: treat as single criteria with improved handling
        return [self._create_fallback_criteria(criteria_text)]
    
    def _preprocess_input(self, text: str) -> str:
        """Clean and normalize input text before parsing."""
        # Remove leading/trailing whitespace
        text = text.strip()
        
        # Normalize line endings
        text = text.replace('\r\n', '\n')
        
        # Remove excessive whitespace
        text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
        
        # Standardize bullet points
        text = re.sub(r'^([•\-\*])\s*', '• ', text, flags=re.MULTILINE)
        
        return text
    
    def _parse_gwt_format(self, text: str) -> List[ParsedCriteria]:
        """Parse Given-When-Then format."""
        results = []
        
        for pattern in self.gwt_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                given = match.group(1).strip()
                when = match.group(2).strip()
                then = match.group(3).strip()
                
                if given and when and then:
                    results.append(ParsedCriteria(
                        given=given,
                        when=when,
                        then=then,
                        original_text=match.group(0),
                        confidence=0.9
                    ))
        
        return results
    
    def _parse_bullet_format(self, text: str) -> List[ParsedCriteria]:
        """Parse bullet point format."""
        lines = text.split('\n')
        criteria_items = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            for pattern in self.bullet_patterns:
                match = re.match(pattern, line)
                if match:
                    criteria_items.append(match.group(1).strip())
                    break
        
        if not criteria_items:
            return []
        
        # Convert bullet points to GWT format
        results = []
        for i, item in enumerate(criteria_items):
            # Try to extract action and result
            action_result = self._extract_action_result(item)
            if action_result:
                given = "the system is in a known state"
                when = action_result["action"]
                then = action_result["result"]
                
                results.append(ParsedCriteria(
                    given=given,
                    when=when,
                    then=then,
                    original_text=item,
                    confidence=0.7
                ))
            else:
                # Treat as a single requirement
                results.append(ParsedCriteria(
                    given="the system is in a known state",
                    when="the requirement is implemented",
                    then=item,
                    original_text=item,
                    confidence=0.5
                ))
        
        return results
    
    def _parse_action_result_format(self, text: str) -> List[ParsedCriteria]:
        """Parse action-result format."""
        results = []
        
        for pattern in self.action_result_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                action = match.group(1).strip()
                result = match.group(2).strip()
                
                if action and result:
                    results.append(ParsedCriteria(
                        given="the system is in a known state",
                        when=action,
                        then=result,
                        original_text=match.group(0),
                        confidence=0.8
                    ))
        
        return results
    
    def _extract_action_result(self, text: str) -> Optional[Dict[str, str]]:
        """Extract action and result from text."""
        for pattern in self.action_result_patterns:
            match = re.match(pattern, text, re.IGNORECASE)
            if match:
                return {
                    "action": match.group(1).strip(),
                    "result": match.group(2).strip()
                }
        return None
    
    def _create_fallback_criteria(self, text: str) -> ParsedCriteria:
        """Create fallback criteria when parsing fails."""
        # Try to split simple Given/When/Then patterns
        if isinstance(text, str):
            parts = text.split('\n')
            if len(parts) >= 3:
                return ParsedCriteria(
                    given=parts[0].strip(),
                    when=parts[1].strip(),
                    then=parts[2].strip(),
                    original_text=text,
                    confidence=0.7
                )
            
            # Handle simple Given/When/Then in one line
            if 'Given' in text and 'When' in text and 'Then' in text:
                try:
                    given = text.split('Given')[1].split('When')[0].strip()
                    when = text.split('When')[1].split('Then')[0].strip()
                    then = text.split('Then')[1].strip()
                    return ParsedCriteria(
                        given=given,
                        when=when,
                        then=then,
                        original_text=text,
                        confidence=0.8
                    )
                except:
                    pass
        
        return ParsedCriteria(
            given="the system is in a known state",
            when="the requirement is implemented",
            then=text.strip(),
            original_text=text,
            confidence=0.3
        )
    
    def extract_keywords(self, criteria: List[str]) -> List[str]:
        """Extract keywords from acceptance criteria."""
        keywords = set()
        
        for criterion in criteria:
            # Extract technical terms, actions, and objects
            words = re.findall(r'\b[A-Za-z][A-Za-z0-9_]*\b', criterion)
            
            # Filter out common words
            common_words = {
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should',
                'could', 'can', 'may', 'might', 'must', 'shall', 'given', 'when', 'then'
            }
            
            for word in words:
                word_lower = word.lower()
                if (word_lower not in common_words and 
                    len(word) > 2 and 
                    not word.isdigit()):
                    keywords.add(word_lower)
        
        return list(keywords)
    
    def identify_edge_cases(self, criteria: List[str]) -> List[str]:
        """Identify potential edge cases from acceptance criteria."""
        edge_cases = []
        
        edge_case_patterns = [
            r'\b(empty|null|none|zero)\b',
            r'\b(maximum|minimum|limit|boundary)\b',
            r'\b(invalid|invalid|wrong|incorrect)\b',
            r'\b(timeout|expired|stale)\b',
            r'\b(concurrent|simultaneous|parallel)\b',
            r'\b(offline|disconnected|unavailable)\b',
            r'\b(permission|access|authorization)\b',
            r'\b(performance|slow|fast|response time)\b'
        ]
        
        for criterion in criteria:
            for pattern in edge_case_patterns:
                if re.search(pattern, criterion, re.IGNORECASE):
                    edge_cases.append(criterion)
                    break
        
        return edge_cases
    
    def validate_criteria(self, criteria: List[str]) -> Dict[str, Any]:
        """Validate acceptance criteria for completeness and clarity."""
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": []
        }
        
        if not criteria:
            validation_result["is_valid"] = False
            validation_result["errors"].append("No acceptance criteria provided")
            return validation_result
        
        for i, criterion in enumerate(criteria):
            if not criterion.strip():
                validation_result["errors"].append(f"Empty criteria at position {i+1}")
                validation_result["is_valid"] = False
                continue
            
            # Check for Given-When-Then structure
            if self._has_gwt_structure(criterion):
                validation_result["suggestions"].append(
                    f"Consider using Given-When-Then format for criterion {i+1}"
                )
            
            # Check for specific actions
            if not self._has_specific_action(criterion):
                validation_result["warnings"].append(
                    f"Criterion {i+1} may lack specific actions"
                )
            
            # Check for measurable outcomes
            if not self._has_measurable_outcome(criterion):
                validation_result["warnings"].append(
                    f"Criterion {i+1} may lack measurable outcomes"
                )
        
        return validation_result
    
    def _has_gwt_structure(self, text: str) -> bool:
        """Check if text has Given-When-Then structure."""
        gwt_words = ["given", "when", "then"]
        text_lower = text.lower()
        return all(word in text_lower for word in gwt_words)
    
    def _has_specific_action(self, text: str) -> bool:
        """Check if text has specific actions."""
        action_words = ["click", "enter", "select", "navigate", "submit", "verify", "check"]
        text_lower = text.lower()
        return any(word in text_lower for word in action_words)
    
    def _has_measurable_outcome(self, text: str) -> bool:
        """Check if text has measurable outcomes."""
        outcome_words = ["should", "will", "must", "can", "appears", "displays", "redirects"]
        text_lower = text.lower()
        return any(word in text_lower for word in outcome_words)
