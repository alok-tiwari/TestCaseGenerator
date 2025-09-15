"""Parser for system context information."""

import re
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass


@dataclass
class ParsedSystemContext:
    """Structured representation of parsed system context."""
    
    tech_stack: List[str]
    data_types: List[str]
    constraints: List[str]
    user_roles: List[str]
    original_text: str
    confidence: float  # 0.0 to 1.0
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "tech_stack": self.tech_stack,
            "data_types": self.data_types,
            "constraints": self.constraints,
            "user_roles": self.user_roles,
            "original_text": self.original_text,
            "confidence": self.confidence,
            "metadata": self.metadata
        }


class SystemContextParser:
    """Parser for system context information."""
    
    def __init__(self):
        """Initialize the parser with patterns and keywords."""
        
        # Technology stack patterns
        self.tech_stack_patterns = {
            "frontend": [
                "react", "angular", "vue", "svelte", "html", "css", "javascript", "typescript",
                "jquery", "bootstrap", "material-ui", "tailwind", "webpack", "vite", "next.js"
            ],
            "backend": [
                "python", "java", "c#", "node.js", "php", "ruby", "go", "rust", "django", "flask",
                "spring", "asp.net", "express", "laravel", "rails", "fastapi", "spring boot"
            ],
            "database": [
                "mysql", "postgresql", "mongodb", "redis", "elasticsearch", "oracle", "sql server",
                "sqlite", "dynamodb", "cassandra", "neo4j", "influxdb"
            ],
            "infrastructure": [
                "docker", "kubernetes", "aws", "azure", "gcp", "heroku", "digitalocean",
                "nginx", "apache", "jenkins", "gitlab", "github actions", "terraform"
            ],
            "testing": [
                "selenium", "cypress", "playwright", "pytest", "junit", "nunit", "jest",
                "mocha", "chai", "cucumber", "behave", "specflow"
            ]
        }
        
        # Data type patterns
        self.data_type_patterns = {
            "user_data": [
                "user credentials", "profile information", "personal data", "contact details",
                "authentication tokens", "session data", "user preferences"
            ],
            "business_data": [
                "orders", "transactions", "invoices", "reports", "analytics", "metrics",
                "financial data", "inventory", "customer data"
            ],
            "system_data": [
                "logs", "configuration", "settings", "cache", "temporary files", "backup data",
                "system metrics", "performance data"
            ],
            "media_data": [
                "images", "videos", "documents", "files", "audio", "attachments", "uploads"
            ]
        }
        
        # Constraint patterns
        self.constraint_patterns = {
            "performance": [
                "response time", "throughput", "latency", "performance", "speed", "efficiency",
                "scalability", "load handling", "concurrent users"
            ],
            "security": [
                "authentication", "authorization", "encryption", "privacy", "gdpr", "compliance",
                "data protection", "secure", "vulnerability", "penetration testing"
            ],
            "reliability": [
                "availability", "uptime", "reliability", "fault tolerance", "disaster recovery",
                "backup", "redundancy", "error handling"
            ],
            "usability": [
                "accessibility", "user experience", "usability", "mobile friendly", "responsive",
                "internationalization", "localization"
            ]
        }
        
        # User role patterns
        self.user_role_patterns = [
            "admin", "administrator", "user", "customer", "guest", "manager", "supervisor",
            "developer", "tester", "analyst", "viewer", "editor", "moderator", "support"
        ]
        
        # Common patterns for extraction
        self.extraction_patterns = {
            "tech_stack": [
                r"built\s+with\s+(.+)",
                r"technology\s*[:=]\s*(.+)",
                r"stack\s*[:=]\s*(.+)",
                r"using\s+(.+)",
                r"developed\s+in\s+(.+)"
            ],
            "data_types": [
                r"handles\s+(.+)",
                r"processes\s+(.+)",
                r"stores\s+(.+)",
                r"manages\s+(.+)",
                r"data\s+types?\s*[:=]\s*(.+)"
            ],
            "constraints": [
                r"must\s+(.+)",
                r"should\s+(.+)",
                r"requirement\s*[:=]\s*(.+)",
                r"constraint\s*[:=]\s*(.+)",
                r"performance\s+requirement\s*[:=]\s*(.+)"
            ],
            "user_roles": [
                r"users?\s+can\s+(.+)",
                r"role\s*[:=]\s*(.+)",
                r"permission\s*[:=]\s*(.+)",
                r"access\s+level\s*[:=]\s*(.+)"
            ]
        }
    
    def parse_system_context(self, context_text: str) -> ParsedSystemContext:
        """Parse system context text into structured format."""
        
        if not context_text or not context_text.strip():
            return self._create_empty_context()
        
        # Extract components using different methods
        tech_stack = self._extract_tech_stack(context_text)
        data_types = self._extract_data_types(context_text)
        constraints = self._extract_constraints(context_text)
        user_roles = self._extract_user_roles(context_text)
        
        # Calculate confidence based on extraction success
        confidence = self._calculate_confidence(
            tech_stack, data_types, constraints, user_roles, context_text
        )
        
        # Extract metadata
        metadata = self._extract_metadata(context_text)
        
        return ParsedSystemContext(
            tech_stack=tech_stack,
            data_types=data_types,
            constraints=constraints,
            user_roles=user_roles,
            original_text=context_text,
            confidence=confidence,
            metadata=metadata
        )
    
    def _extract_tech_stack(self, text: str) -> List[str]:
        """Extract technology stack information."""
        tech_stack = set()
        text_lower = text.lower()
        
        # Extract using pattern matching
        for category, technologies in self.tech_stack_patterns.items():
            for tech in technologies:
                if tech.lower() in text_lower:
                    tech_stack.add(tech)
        
        # Extract using regex patterns
        for pattern in self.extraction_patterns["tech_stack"]:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                extracted_text = match.group(1).strip()
                # Parse the extracted text for technologies
                extracted_techs = self._parse_tech_list(extracted_text)
                tech_stack.update(extracted_techs)
        
        return list(tech_stack)
    
    def _extract_data_types(self, text: str) -> List[str]:
        """Extract data type information."""
        data_types = set()
        text_lower = text.lower()
        
        # Extract using pattern matching
        for category, types in self.data_type_patterns.items():
            for data_type in types:
                if data_type.lower() in text_lower:
                    data_types.add(data_type)
        
        # Extract using regex patterns
        for pattern in self.extraction_patterns["data_types"]:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                extracted_text = match.group(1).strip()
                # Parse the extracted text for data types
                extracted_types = self._parse_data_type_list(extracted_text)
                data_types.update(extracted_types)
        
        return list(data_types)
    
    def _extract_constraints(self, text: str) -> List[str]:
        """Extract constraint information."""
        constraints = set()
        text_lower = text.lower()
        
        # Extract using pattern matching
        for category, constraint_list in self.constraint_patterns.items():
            for constraint in constraint_list:
                if constraint.lower() in text_lower:
                    constraints.add(constraint)
        
        # Extract using regex patterns
        for pattern in self.extraction_patterns["constraints"]:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                extracted_text = match.group(1).strip()
                constraints.add(extracted_text)
        
        return list(constraints)
    
    def _extract_user_roles(self, text: str) -> List[str]:
        """Extract user role information."""
        user_roles = set()
        text_lower = text.lower()
        
        # Extract using pattern matching
        for role in self.user_role_patterns:
            if role.lower() in text_lower:
                user_roles.add(role)
        
        # Extract using regex patterns
        for pattern in self.extraction_patterns["user_roles"]:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                extracted_text = match.group(1).strip()
                # Parse the extracted text for roles
                extracted_roles = self._parse_role_list(extracted_text)
                user_roles.update(extracted_roles)
        
        return list(user_roles)
    
    def _parse_tech_list(self, text: str) -> List[str]:
        """Parse technology list from extracted text."""
        tech_list = []
        
        # Split by common separators
        separators = [",", ";", "|", "and", "&", "\n"]
        for separator in separators:
            if separator in text:
                parts = text.split(separator)
                break
        else:
            parts = [text]
        
        for part in parts:
            part = part.strip()
            if part:
                # Clean up the technology name
                tech = self._clean_tech_name(part)
                if tech:
                    tech_list.append(tech)
        
        return tech_list
    
    def _parse_data_type_list(self, text: str) -> List[str]:
        """Parse data type list from extracted text."""
        data_types = []
        
        # Split by common separators
        separators = [",", ";", "|", "and", "\n"]
        for separator in separators:
            if separator in text:
                parts = text.split(separator)
                break
        else:
            parts = [text]
        
        for part in parts:
            part = part.strip()
            if part:
                data_types.append(part)
        
        return data_types
    
    def _parse_role_list(self, text: str) -> List[str]:
        """Parse role list from extracted text."""
        roles = []
        
        # Split by common separators
        separators = [",", ";", "|", "and", "\n"]
        for separator in separators:
            if separator in text:
                parts = text.split(separator)
                break
        else:
            parts = [text]
        
        for part in parts:
            part = part.strip()
            if part:
                # Check if it's a valid role
                if self._is_valid_role(part):
                    roles.append(part)
        
        return roles
    
    def _clean_tech_name(self, tech: str) -> Optional[str]:
        """Clean and validate technology name."""
        # Remove common prefixes/suffixes
        tech = re.sub(r'^(the\s+|a\s+|an\s+)', '', tech, flags=re.IGNORECASE)
        tech = re.sub(r'(\s+framework|\s+library|\s+tool|\s+technology)$', '', tech, flags=re.IGNORECASE)
        
        # Basic validation
        if len(tech) < 2 or len(tech) > 50:
            return None
        
        # Check if it contains valid characters
        if not re.match(r'^[A-Za-z0-9\s\-\.\+]+$', tech):
            return None
        
        return tech.strip()
    
    def _is_valid_role(self, role: str) -> bool:
        """Check if a role is valid."""
        role_lower = role.lower()
        
        # Check against known patterns
        for pattern in self.user_role_patterns:
            if pattern.lower() in role_lower or role_lower in pattern.lower():
                return True
        
        # Check for common role indicators
        role_indicators = ["user", "admin", "manager", "role", "permission", "access"]
        for indicator in role_indicators:
            if indicator in role_lower:
                return True
        
        return False
    
    def _calculate_confidence(self, tech_stack: List[str], data_types: List[str], 
                            constraints: List[str], user_roles: List[str], 
                            original_text: str) -> float:
        """Calculate confidence score for parsed components."""
        confidence = 0.3  # Base confidence
        
        # Add confidence based on extraction success
        if tech_stack:
            confidence += 0.2
        if data_types:
            confidence += 0.2
        if constraints:
            confidence += 0.15
        if user_roles:
            confidence += 0.15
        
        # Add confidence based on text quality
        text_length = len(original_text.strip())
        if text_length > 100:
            confidence += 0.1
        elif text_length > 50:
            confidence += 0.05
        
        # Add confidence based on structure
        if self._has_structured_format(original_text):
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _has_structured_format(self, text: str) -> bool:
        """Check if text has structured format."""
        structured_indicators = [
            ":", "=", "-", "•", "*", "1.", "2.", "3.",
            "technology", "stack", "data", "constraints", "roles"
        ]
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in structured_indicators)
    
    def _extract_metadata(self, text: str) -> Dict[str, Any]:
        """Extract metadata from system context text."""
        metadata = {}
        
        # Extract tags/labels
        tags = re.findall(r'#(\w+)', text)
        if tags:
            metadata['tags'] = tags
        
        # Extract priority indicators
        priority_indicators = {
            'high': ['critical', 'important', 'high priority', 'urgent'],
            'medium': ['normal', 'standard', 'medium priority'],
            'low': ['low priority', 'nice to have', 'optional']
        }
        
        text_lower = text.lower()
        for priority, indicators in priority_indicators.items():
            if any(indicator in text_lower for indicator in indicators):
                metadata['priority'] = priority
                break
        
        # Extract version information
        version_match = re.search(r'version\s*[:=]\s*([\d\.]+)', text, re.IGNORECASE)
        if version_match:
            metadata['version'] = version_match.group(1)
        
        # Extract environment information
        environment_match = re.search(r'environment\s*[:=]\s*(\w+)', text, re.IGNORECASE)
        if environment_match:
            metadata['environment'] = environment_match.group(1)
        
        return metadata
    
    def _create_empty_context(self) -> ParsedSystemContext:
        """Create empty system context."""
        return ParsedSystemContext(
            tech_stack=[],
            data_types=[],
            constraints=[],
            user_roles=[],
            original_text="",
            confidence=0.0,
            metadata={}
        )
    
    def validate_system_context(self, context: ParsedSystemContext) -> Dict[str, Any]:
        """Validate a parsed system context."""
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": []
        }
        
        # Check if any components were extracted
        if not any([context.tech_stack, context.data_types, context.constraints, context.user_roles]):
            validation_result["warnings"].append("No system context components were extracted")
        
        # Check confidence level
        if context.confidence < 0.5:
            validation_result["warnings"].append("Low confidence in parsing - manual review recommended")
        
        # Check for missing critical information
        if not context.tech_stack:
            validation_result["suggestions"].append("Consider adding technology stack information")
        
        if not context.user_roles:
            validation_result["suggestions"].append("Consider adding user role information")
        
        # Check for potential issues
        if len(context.tech_stack) > 20:
            validation_result["warnings"].append("Technology stack seems too extensive - verify accuracy")
        
        if len(context.constraints) > 15:
            validation_result["warnings"].append("Many constraints identified - verify completeness")
        
        return validation_result
    
    def suggest_improvements(self, context: ParsedSystemContext) -> List[str]:
        """Suggest improvements for system context."""
        suggestions = []
        
        if not context.tech_stack:
            suggestions.append("Add technology stack information (e.g., 'Built with React, Node.js, PostgreSQL')")
        
        if not context.data_types:
            suggestions.append("Specify data types handled by the system (e.g., 'Handles user profiles, orders, payments')")
        
        if not context.constraints:
            suggestions.append("List system constraints (e.g., 'Must support 1000 concurrent users, GDPR compliant')")
        
        if not context.user_roles:
            suggestions.append("Define user roles and permissions (e.g., 'Admin, User, Guest roles with different access levels')")
        
        if context.confidence < 0.7:
            suggestions.append("Use structured format with clear labels (e.g., 'Technology: React, Database: PostgreSQL')")
        
        return suggestions
