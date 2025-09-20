"""Human readable formatter for generating documentation-style test cases."""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from models.test_models import TestCase, TestStep
from models.input_models import TestCaseRequest


logger = logging.getLogger(__name__)


class HumanReadableFormatter:
    """Formatter for generating human-readable test case documentation."""
    
    def __init__(self):
        """Initialize the human readable formatter."""
        self.template = """# Test Case Documentation

## Overview
{overview}

## Test Cases

{test_cases}

## Summary
- Total Test Cases: {total_count}
- Test Types: {test_types}
- Priority Distribution: {priority_distribution}
- Generated: {generated_timestamp}
"""

        self.test_case_template = """### {test_id}: {title}

**Description:** {description}

**Test Type:** {test_type}
**Priority:** {priority}
**Test Level:** {test_level}

**Tags:** {tags}

**Requirements:** {requirements}

**Preconditions:** {preconditions}

**Test Steps:**
{steps}

**Expected Results:** {expected_results}

**Test Data:** {test_data}

**Notes:** {notes}

---
"""

        self.step_template = """{step_number}. **{action}**
   - Expected Result: {expected_result}
   - Test Data: {test_data}
   - Notes: {notes}"""
    
    def format_test_cases(self, test_cases: List[TestCase], request: TestCaseRequest) -> str:
        """Format test cases into human-readable documentation."""
        
        if not test_cases:
            return "# No test cases to format"
        
        try:
            # Generate overview
            overview = self._generate_overview(test_cases, request)
            
            # Format individual test cases
            formatted_cases = []
            for test_case in test_cases:
                case_content = self._format_single_test_case(test_case)
                if case_content:
                    formatted_cases.append(case_content)
            
            # Generate summary statistics
            summary_stats = self._generate_summary_stats(test_cases)
            
            # Combine into complete documentation
            complete_doc = self.template.format(
                overview=overview,
                test_cases="\n".join(formatted_cases),
                total_count=len(test_cases),
                test_types=", ".join(summary_stats["test_types"]),
                priority_distribution=summary_stats["priority_distribution"],
                generated_timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            
            return complete_doc
            
        except Exception as e:
            logger.error(f"Error formatting test cases to human readable: {e}")
            return f"# Error formatting test cases: {e}"
    
    def _generate_overview(self, test_cases: List[TestCase], request: TestCaseRequest) -> str:
        """Generate overview section for the documentation."""
        
        overview_parts = []
        
        # Add user story if available
        if request.user_story:
            overview_parts.append(f"""**User Story:**
- **Persona:** {request.user_story.persona}
- **Action:** {request.user_story.action}
- **Value:** {request.user_story.value}""")
        
        # Add acceptance criteria
        if request.acceptance_criteria:
            overview_parts.append(f"""**Acceptance Criteria:**
{chr(10).join(f"- {criteria}" for criteria in request.acceptance_criteria.criteria_list)}""")
        
        # Add system context if available
        if request.system_context:
            context_parts = []
            if request.system_context.tech_stack:
                context_parts.append(f"- **Technology Stack:** {', '.join(request.system_context.tech_stack)}")
            if request.system_context.user_roles:
                context_parts.append(f"- **User Roles:** {', '.join(request.system_context.user_roles)}")
            if request.system_context.constraints:
                context_parts.append(f"- **Constraints:** {', '.join(request.system_context.constraints)}")
            
            if context_parts:
                overview_parts.append(f"""**System Context:**
{chr(10).join(context_parts)}""")
        
        # Add test specification
        spec = request.test_specification
        overview_parts.append(f"""**Test Specification:**
- **Test Types:** {', '.join(spec.test_types)}
- **Test Level:** {spec.test_level}
- **Output Format:** {spec.output_format}
- **Priority:** {spec.priority}""")
        
        # Add Jira ticket if available
        if request.jira_ticket_id:
            overview_parts.append(f"**Jira Ticket:** {request.jira_ticket_id}")
        
        return "\n\n".join(overview_parts)
    
    def _format_single_test_case(self, test_case: TestCase) -> str:
        """Format a single test case into human-readable format."""
        
        try:
            # Format test steps
            steps_content = []
            for i, step in enumerate(test_case.steps, 1):
                step_content = self.step_template.format(
                    step_number=i,
                    action=step.action,
                    expected_result=step.expected_result or "Not specified",
                    test_data=step.test_data or "Not specified",
                    notes=step.notes or "No additional notes"
                )
                steps_content.append(step_content)
            
            # Get test data information
            test_data_info = self._format_test_data(test_case.test_data)
            
            # Get preconditions
            preconditions = self._get_preconditions(test_case)
            
            # Get expected results summary
            expected_results = self._get_expected_results_summary(test_case.steps)
            
            # Get notes
            notes = self._get_test_case_notes(test_case)
            
            # Format the test case
            case_content = self.test_case_template.format(
                test_id=test_case.test_id,
                title=test_case.title,
                description=test_case.description,
                test_type=test_case.test_type.value,
                priority=test_case.priority.value,
                test_level=test_case.test_level,
                tags=", ".join(test_case.tags) if test_case.tags else "None",
                requirements=", ".join(test_case.requirements) if test_case.requirements else "None",
                preconditions=preconditions,
                steps="\n".join(steps_content),
                expected_results=expected_results,
                test_data=test_data_info,
                notes=notes
            )
            
            return case_content
            
        except Exception as e:
            logger.warning(f"Failed to format test case {test_case.test_id}: {e}")
            return None
    
    def _format_test_data(self, test_data) -> str:
        """Format test data information."""
        
        if not test_data:
            return "Not specified"
        
        data_parts = []
        
        if test_data.input_data:
            input_items = [f"{k}: {v}" for k, v in test_data.input_data.items()]
            data_parts.append(f"**Input Data:** {', '.join(input_items)}")
        
        if test_data.expected_output:
            output_items = [f"{k}: {v}" for k, v in test_data.expected_output.items()]
            data_parts.append(f"**Expected Output:** {', '.join(output_items)}")
        
        if test_data.preconditions:
            data_parts.append(f"**Preconditions:** {', '.join(test_data.preconditions)}")
        
        if test_data.test_environment:
            env_items = [f"{k}: {v}" for k, v in test_data.test_environment.items()]
            data_parts.append(f"**Test Environment:** {', '.join(env_items)}")
        
        return " | ".join(data_parts) if data_parts else "Not specified"
    
    def _get_preconditions(self, test_case: TestCase) -> str:
        """Get preconditions for the test case."""
        
        preconditions = []
        
        # Add system state preconditions
        preconditions.append("System is in a known state")
        
        # Add user-related preconditions
        if any("user" in tag.lower() for tag in test_case.tags):
            preconditions.append("User is logged into the system")
        
        # Add role-related preconditions
        if any("admin" in tag.lower() for tag in test_case.tags):
            preconditions.append("User has admin privileges")
        
        # Add data-related preconditions
        if test_case.test_data and test_case.test_data.preconditions:
            preconditions.extend(test_case.test_data.preconditions)
        
        return " | ".join(preconditions)
    
    def _get_expected_results_summary(self, steps: List[TestStep]) -> str:
        """Get a summary of expected results from test steps."""
        
        if not steps:
            return "Not specified"
        
        # Collect all expected results
        expected_results = []
        for step in steps:
            if step.expected_result:
                expected_results.append(step.expected_result)
        
        if not expected_results:
            return "Not specified"
        
        # Return unique expected results
        unique_results = list(dict.fromkeys(expected_results))  # Preserve order
        return " | ".join(unique_results)
    
    def _get_test_case_notes(self, test_case: TestCase) -> str:
        """Get additional notes for the test case."""
        
        notes = []
        
        # Add step notes
        for i, step in enumerate(test_case.steps, 1):
            if step.notes and step.notes != "No additional notes":
                notes.append(f"Step {i}: {step.notes}")
        
        # Add test case level notes
        if test_case.result and test_case.result.status.value != "draft":
            notes.append(f"Status: {test_case.result.status.value}")
        
        if test_case.dependencies:
            notes.append(f"Dependencies: {', '.join(test_case.dependencies)}")
        
        return " | ".join(notes) if notes else "No additional notes"
    
    def _generate_summary_stats(self, test_cases: List[TestCase]) -> Dict[str, Any]:
        """Generate summary statistics for the test cases."""
        
        # Count test types
        test_types = {}
        for tc in test_cases:
            tc_type = tc.test_type.value
            test_types[tc_type] = test_types.get(tc_type, 0) + 1
        
        # Count priorities
        priorities = {}
        for tc in test_cases:
            priority = tc.priority.value
            priorities[priority] = priorities.get(priority, 0) + 1
        
        # Format priority distribution
        priority_distribution = ", ".join([f"{priority}: {count}" for priority, count in priorities.items()])
        
        return {
            "test_types": [f"{tc_type} ({count})" for tc_type, count in test_types.items()],
            "priority_distribution": priority_distribution
        }
    
    def format_test_cases_by_type(self, test_cases: List[TestCase], request: TestCaseRequest) -> Dict[str, str]:
        """Format test cases grouped by type into separate documentation files."""
        
        grouped_cases = {}
        
        # Group test cases by type
        for test_case in test_cases:
            test_type = test_case.test_type.value
            if test_type not in grouped_cases:
                grouped_cases[test_type] = []
            grouped_cases[test_type].append(test_case)
        
        # Format each group
        formatted_docs = {}
        for test_type, cases in grouped_cases.items():
            # Create a modified request for this group
            group_request = self._create_group_request(request, test_type)
            
            # Format the group
            formatted_content = self.format_test_cases(cases, group_request)
            
            # Add section header
            formatted_content = f"# {test_type.title()} Test Cases\n\n{formatted_content}"
            
            formatted_docs[test_type] = formatted_content
        
        return formatted_docs
    
    def _create_group_request(self, original_request: TestCaseRequest, test_type: str) -> TestCaseRequest:
        """Create a modified request for a specific test type group."""
        
        # Create a copy of the original request with modified test specification
        from copy import deepcopy
        
        group_request = deepcopy(original_request)
        
        # Update test specification for the group
        group_request.test_specification.test_types = [test_type]
        group_request.test_specification.output_format = "human"
        
        return group_request
    
    def format_single_test_case(self, test_case: TestCase) -> str:
        """Format a single test case as standalone documentation."""
        
        try:
            # Create a minimal request for single test case
            from models.input_models import TestCaseRequest, AcceptanceCriteria, TestSpecification
            
            # Create minimal request
            request = TestCaseRequest(
                acceptance_criteria=AcceptanceCriteria(
                    criteria_type="bullet-style",
                    criteria_list=["Single test case"]
                ),
                test_specification=TestSpecification(
                    test_types=["functional"],
                    test_level="unit",
                    output_format="human"
                )
            )
            
            # Format the test case
            formatted_content = self._format_single_test_case(test_case)
            if not formatted_content:
                return f"# Failed to format test case: {test_case.test_id}"
            
            # Add header
            header = f"""# Test Case Documentation

## Single Test Case

"""
            
            return header + formatted_content
            
        except Exception as e:
            logger.error(f"Error formatting single test case: {e}")
            return f"# Error formatting test case: {e}"
    
    def format_executive_summary(self, test_cases: List[TestCase], request: TestCaseRequest) -> str:
        """Generate an executive summary of the test cases."""
        
        if not test_cases:
            return "# No test cases to summarize"
        
        try:
            # Generate summary statistics
            summary_stats = self._generate_summary_stats(test_cases)
            
            # Calculate coverage metrics
            coverage_metrics = self._calculate_coverage_metrics(test_cases, request)
            
            # Generate executive summary
            executive_summary = f"""# Test Case Executive Summary

## Overview
This document provides a high-level summary of the generated test cases for the specified requirements.

## Test Coverage Summary
- **Total Test Cases:** {len(test_cases)}
- **Test Types:** {', '.join(summary_stats['test_types'])}
- **Priority Distribution:** {summary_stats['priority_distribution']}

## Coverage Metrics
{coverage_metrics}

## Test Case Distribution
{self._generate_test_distribution(test_cases)}

## Recommendations
{self._generate_recommendations(test_cases, request)}

## Generated
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
            
            return executive_summary
            
        except Exception as e:
            logger.error(f"Error generating executive summary: {e}")
            return f"# Error generating executive summary: {e}"
    
    def _calculate_coverage_metrics(self, test_cases: List[TestCase], request: TestCaseRequest) -> str:
        """Calculate and format coverage metrics."""
        
        metrics = []
        
        # Acceptance criteria coverage
        if request.acceptance_criteria:
            ac_count = len(request.acceptance_criteria.criteria_list)
            covered_ac = len(set([req for tc in test_cases for req in tc.requirements if req.startswith("AC-")]))
            ac_coverage = (covered_ac / ac_count) * 100 if ac_count > 0 else 0
            metrics.append(f"- **Acceptance Criteria Coverage:** {ac_coverage:.1f}% ({covered_ac}/{ac_count})")
        
        # Test type coverage
        requested_types = set(request.test_specification.test_types)
        generated_types = set(tc.test_type.value for tc in test_cases)
        type_coverage = len(generated_types.intersection(requested_types)) / len(requested_types) * 100 if requested_types else 0
        metrics.append(f"- **Test Type Coverage:** {type_coverage:.1f}%")
        
        # Priority coverage
        priorities = ["low", "medium", "high", "critical"]
        priority_coverage = len(set(tc.priority.value for tc in test_cases)) / len(priorities) * 100
        metrics.append(f"- **Priority Coverage:** {priority_coverage:.1f}%")
        
        return "\n".join(metrics)
    
    def _generate_test_distribution(self, test_cases: List[TestCase]) -> str:
        """Generate test case distribution information."""
        
        # Group by test type
        type_distribution = {}
        for tc in test_cases:
            tc_type = tc.test_type.value
            type_distribution[tc_type] = type_distribution.get(tc_type, 0) + 1
        
        # Group by priority
        priority_distribution = {}
        for tc in test_cases:
            priority = tc.priority.value
            priority_distribution[priority] = priority_distribution.get(priority, 0) + 1
        
        distribution_text = []
        
        # Test type distribution
        type_text = "**By Test Type:**\n"
        for tc_type, count in type_distribution.items():
            type_text += f"- {tc_type.title()}: {count} test cases\n"
        distribution_text.append(type_text)
        
        # Priority distribution
        priority_text = "**By Priority:**\n"
        for priority, count in priority_distribution.items():
            priority_text += f"- {priority.title()}: {count} test cases\n"
        distribution_text.append(priority_text)
        
        return "\n".join(distribution_text)
    
    def _generate_recommendations(self, test_cases: List[TestCase], request: TestCaseRequest) -> List[str]:
        """Generate recommendations based on test case analysis."""
        
        recommendations = []
        
        # Check for missing test types
        requested_types = set(request.test_specification.test_types)
        generated_types = set(tc.test_type.value for tc in test_cases)
        missing_types = requested_types - generated_types
        
        if missing_types:
            recommendations.append(f"Consider generating additional test cases for: {', '.join(missing_types)}")
        
        # Check priority distribution
        priorities = [tc.priority.value for tc in test_cases]
        if not any(p == "critical" for p in priorities):
            recommendations.append("Consider adding critical priority test cases for high-risk functionality")
        
        # Check test step quality
        total_steps = sum(len(tc.steps) for tc in test_cases)
        avg_steps = total_steps / len(test_cases) if test_cases else 0
        
        if avg_steps < 2:
            recommendations.append("Some test cases may benefit from more detailed step definitions")
        elif avg_steps > 10:
            recommendations.append("Consider breaking down complex test cases into smaller, focused tests")
        
        # Check for edge cases
        edge_case_count = len([tc for tc in test_cases if "edge" in tc.title.lower() or "edge" in tc.tags])
        if edge_case_count < len(test_cases) * 0.2:  # Less than 20% edge cases
            recommendations.append("Consider adding more edge case and negative scenario test cases")
        
        if not recommendations:
            recommendations.append("Test case coverage appears comprehensive for the given requirements")
        
        return recommendations
    
    def add_documentation_metadata(self, content: str, metadata: Dict[str, Any]) -> str:
        """Add metadata to documentation content."""
        
        metadata_section = []
        
        # Add basic metadata
        if "jira_ticket" in metadata:
            metadata_section.append(f"**JIRA Ticket:** {metadata['jira_ticket']}")
        
        if "test_level" in metadata:
            metadata_section.append(f"**Test Level:** {metadata['test_level']}")
        
        if "priority" in metadata:
            metadata_section.append(f"**Priority:** {metadata['priority']}")
        
        if "tags" in metadata:
            metadata_section.append(f"**Tags:** {', '.join(metadata['tags'])}")
        
        if "generated_at" in metadata:
            metadata_section.append(f"**Generated:** {metadata['generated_at']}")
        
        if "requirements" in metadata:
            metadata_section.append(f"**Requirements:** {', '.join(metadata['requirements'])}")
        
        # Add metadata to content
        if metadata_section:
            metadata_header = "\n".join(metadata_section)
            content = f"{metadata_header}\n\n{content}"
        
        return content
