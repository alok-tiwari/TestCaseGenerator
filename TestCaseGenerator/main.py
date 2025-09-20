"""Main application entrypoint: CLI and FastAPI API for the Test Case Generator."""

import asyncio
import json
import logging
from typing import List, Optional

import click
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from config.settings import config, get_llm_config, get_jira_config
from integrations.llm_client import LLMClient
from integrations.jira_client import JiraClient

from models.input_models import (
    AcceptanceCriteria,
    UserStory,
    SystemContext,
    TestSpecification,
    TestCaseRequest,
)
from models.test_models import TestCase
from generators.functional_test_generator import FunctionalTestGenerator
from generators.edge_case_generator import EdgeCaseGenerator
from generators.security_test_generator import SecurityTestGenerator
from formatters.gherkin_formatter import GherkinFormatter
from formatters.code_skeleton_formatter import CodeSkeletonFormatter
from formatters.human_readable_formatter import HumanReadableFormatter


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("testcase_generator")


# FastAPI app
app = FastAPI(title="Test Case Generator API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class GenerateRequest(BaseModel):
    acceptance_criteria: AcceptanceCriteria
    user_story: Optional[UserStory] = None
    system_context: Optional[SystemContext] = None
    test_specification: TestSpecification
    jira_ticket_id: Optional[str] = None
    provider: Optional[str] = None


class GenerateResponse(BaseModel):
    test_cases: List[dict]
    formatted_output: Optional[str] = None


async def _build_generators(llm_client: LLMClient, spec: TestSpecification):
    generators = []
    if "functional" in spec.test_types:
        generators.append(FunctionalTestGenerator(llm_client))
    if "edge" in spec.test_types or "edge_case" in spec.test_types:
        generators.append(EdgeCaseGenerator(llm_client))
    if "security" in spec.test_types:
        generators.append(SecurityTestGenerator(llm_client))
    # Default to functional if none matched
    if not generators:
        generators.append(FunctionalTestGenerator(llm_client))
    return generators


def _get_formatter(output_format: str):
    if output_format == "gherkin":
        return GherkinFormatter()
    if output_format in {"playwright", "pytest", "cypress", "selenium", "junit"}:
        return CodeSkeletonFormatter()
    return HumanReadableFormatter()


async def _generate_internal(req: TestCaseRequest, provider: Optional[str] = None):
    llm_conf = get_llm_config(provider)
    llm_client = LLMClient(llm_conf)
    try:
        generators = await _build_generators(llm_client, req.test_specification)
        all_cases: List[TestCase] = []
        for gen in generators:
            cases = await gen.generate(req)
            all_cases.extend(cases)
        formatter = _get_formatter(req.test_specification.output_format)
        formatted_output = None
        if isinstance(formatter, GherkinFormatter):
            formatted_output = formatter.format_test_cases(all_cases, req)
        elif isinstance(formatter, CodeSkeletonFormatter):
            framework = req.test_specification.output_format
            formatted_output = formatter.format_test_cases(all_cases, req, framework=framework)
        else:
            formatted_output = formatter.format_test_cases(all_cases, req)
        return all_cases, formatted_output
    finally:
        try:
            await llm_client.close()
        except Exception:
            pass


@app.post("/generate", response_model=GenerateResponse)
async def generate_endpoint(payload: GenerateRequest):
    try:
        req = TestCaseRequest(
            acceptance_criteria=payload.acceptance_criteria,
            user_story=payload.user_story,
            system_context=payload.system_context,
            test_specification=payload.test_specification,
            jira_ticket_id=payload.jira_ticket_id,
        )
        test_cases, formatted = await _generate_internal(req, provider=payload.provider)
        return GenerateResponse(
            test_cases=[json.loads(tc.model_dump_json()) for tc in test_cases],
            formatted_output=formatted,
        )
    except Exception as e:
        logger.exception("Generation failed")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "ok"}





# CLI using Click
@click.group()
def cli():
    """Test Case Generator - CLI"""
    pass


@cli.command()
@click.option("--criteria-type", type=click.Choice(["given-when-then", "bullet-style"]), default="bullet-style")
@click.option("--criteria", multiple=True, required=True, help="Acceptance criteria; repeat for multiple")
@click.option("--persona", default=None)
@click.option("--action", default=None)
@click.option("--value", default=None)
@click.option("--tech", multiple=True, default=[])
@click.option("--data", multiple=True, default=[])
@click.option("--constraint", multiple=True, default=[])
@click.option("--role", multiple=True, default=[])
@click.option("--types", multiple=True, default=["functional"], help="Test types e.g. functional,security")
@click.option("--level", default="unit", type=click.Choice(["unit", "integration", "e2e", "system"]))
@click.option("--format", "out_format", default="gherkin", type=click.Choice(["gherkin", "playwright", "pytest", "cypress", "human"]))
@click.option("--priority", default="medium", type=click.Choice(["low", "medium", "high", "critical"]))
@click.option("--jira", "jira_id", default=None, help="Jira ticket id")
@click.option("--provider", default=None, help="LLM provider key from config/llm_config.yaml")
@click.option("--output", "output_path", default=None, help="Optional file path to write formatted output")
def generate(criteria_type, criteria, persona, action, value, tech, data, constraint, role, types, level, out_format, priority, jira_id, provider, output_path):
    """Generate test cases from CLI inputs."""
    user_story = None
    if persona and action and value:
        user_story = UserStory(persona=persona, action=action, value=value)
    sys_ctx = None
    if tech or data or constraint or role:
        sys_ctx = SystemContext(tech_stack=list(tech), data_types=list(data), constraints=list(constraint), user_roles=list(role))
    req = TestCaseRequest(
        acceptance_criteria=AcceptanceCriteria(criteria_type=criteria_type, criteria_list=list(criteria)),
        user_story=user_story,
        system_context=sys_ctx,
        test_specification=TestSpecification(test_types=list(types), test_level=level, output_format=out_format, priority=priority),
        jira_ticket_id=jira_id,
    )

    async def _run():
        cases, formatted = await _generate_internal(req, provider)
        click.echo(f"Generated {len(cases)} test cases")
        if formatted:
            if output_path:
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(formatted)
                click.echo(f"Formatted output written to {output_path}")
            else:
                click.echo(formatted)

    asyncio.run(_run())


@cli.command()
@click.option("--ticket-id", required=True)
@click.option("--format", "out_format", default="gherkin", type=click.Choice(["gherkin", "playwright", "pytest", "cypress", "human"]))
@click.option("--types", multiple=True, default=["functional"], help="Test types e.g. functional,security")
@click.option("--level", default="integration", type=click.Choice(["unit", "integration", "e2e", "system"]))
@click.option("--priority", default="medium", type=click.Choice(["low", "medium", "high", "critical"]))
@click.option("--provider", default=None)
@click.option("--dummy", is_flag=True, help="Use dummy Jira data instead of real API (recommended for testing)")
@click.option("--output", "output_path", default=None)
@click.option("--story-format", "story_format", default="raw", type=click.Choice(["raw", "gherkin"]), help="JIRA user story format: 'raw' for unstructured text or 'gherkin' for Gherkin format")
@click.option("--extract-context/--no-extract-context", default=True, help="Extract system context from JIRA ticket")
@click.option("--context-detail", "context_detail", default="medium", type=click.Choice(["low", "medium", "high"]), help="Level of detail for context extraction")
def generate_from_jira(ticket_id, out_format, types, level, priority, provider, dummy, output_path, story_format, extract_context, context_detail):
    """Generate test cases by pulling data from Jira."""
    jira_conf = get_jira_config()
    if not dummy and not jira_conf:
        raise click.ClickException("Jira config not available. Provide JIRA_* env vars or use --dummy.")

    async def _run():
        if dummy:
            jira_client = None
            # Create a dummy config with the specified story format
            if jira_conf:
                jira_conf.user_story_format = story_format
            ticket = JiraClient(jira_conf).generate_dummy_ticket(ticket_id) if jira_conf else JiraClient.__new__(JiraClient).generate_dummy_ticket(ticket_id)  # type: ignore
        else:
            # Update the config with the specified parameters
            jira_conf.user_story_format = story_format
            jira_conf.extract_context = extract_context
            jira_conf.context_detail_level = context_detail
            jira_client = JiraClient(jira_conf)  # type: ignore
            ticket = await jira_client.fetch_ticket(ticket_id)
        try:
            # Build request from Jira ticket
            ac_type = ticket.get_acceptance_criteria_type()
            ac = AcceptanceCriteria(criteria_type=ac_type, criteria_list=ticket.acceptance_criteria)
            story_parts = ticket.extract_user_story_parts()
            user_story = None
            if story_parts:
                user_story = UserStory(persona=story_parts["persona"], action=story_parts["action"], value=story_parts["value"])
            
            # Extract system context from JIRA ticket
            system_context = None
            if not dummy and jira_client and jira_conf.extract_context:
                context_data = jira_client._extract_system_context(ticket.issue.fields)
                if context_data:
                    system_context = SystemContext(
                        tech_stack=context_data.get('tech_stack', []),
                        data_types=context_data.get('data_types', []),
                        constraints=context_data.get('constraints', []),
                        user_roles=context_data.get('user_roles', [])
                    )
            
            spec = TestSpecification(test_types=list(types), test_level=level, output_format=out_format, priority=priority)
            req = TestCaseRequest(acceptance_criteria=ac, user_story=user_story, system_context=system_context, test_specification=spec, jira_ticket_id=ticket.issue.issue_key)
            cases, formatted = await _generate_internal(req, provider)
            click.echo(f"Generated {len(cases)} test cases from {ticket_id}")
            if formatted:
                if output_path:
                    with open(output_path, "w", encoding="utf-8") as f:
                        f.write(formatted)
                    click.echo(f"Formatted output written to {output_path}")
                else:
                    click.echo(formatted)
        finally:
            if not dummy and jira_client:
                await jira_client.close()

    asyncio.run(_run())


@cli.command()
@click.option("--host", default="0.0.0.0")
@click.option("--port", default=8000, type=int)
@click.option("--reload", is_flag=True, default=False)
def serve(host, port, reload):
    """Run the FastAPI server."""
    uvicorn.run("main:app", host=host, port=port, reload=reload)





@cli.command()
@click.argument("feature_id")
@click.option("--format", "out_format", default="gherkin", type=click.Choice(["gherkin", "playwright", "pytest", "cypress", "human"]))
@click.option("--types", multiple=True, default=["functional"], help="Test types e.g. functional,security")
@click.option("--level", default="integration", type=click.Choice(["unit", "integration", "e2e", "system"]))
@click.option("--priority", default="medium", type=click.Choice(["low", "medium", "high", "critical"]))
@click.option("--provider", default=None)
@click.option("--output", "output_path", default=None)
def generate_from_feature(feature_id, out_format, types, level, priority, provider, output_path):
    """Generate test cases from a synthetic feature by ID."""
    local_provider = get_local_data_provider()
    
    if not local_provider.is_local_mode_enabled():
        raise click.ClickException("Local mode not available. Check your synthetic_data directory.")
    
    # Get feature data
    feature = local_provider.get_feature_by_id(feature_id)
    if not feature:
        available_ids = [f['id'] for f in local_provider.get_feature_summary()]
        raise click.ClickException(f"Feature {feature_id} not found. Available IDs: {', '.join(available_ids)}")
    
    # Build request from synthetic feature
    acceptance_criteria = local_provider.get_feature_acceptance_criteria(feature_id)
    user_story = local_provider.get_feature_user_story(feature_id)
    system_context = local_provider.get_feature_system_context(feature_id)
    
    if not acceptance_criteria:
        raise click.ClickException(f"Feature {feature_id} has no acceptance criteria defined.")
    
    # Use default provider if none specified
    if not provider:
        provider = local_provider.config.get('default_provider', 'ollama')
    
    spec = TestSpecification(
        test_types=list(types), 
        test_level=level, 
        output_format=out_format, 
        priority=priority
    )
    
    req = TestCaseRequest(
        acceptance_criteria=acceptance_criteria,
        user_story=user_story,
        system_context=system_context,
        test_specification=spec,
        jira_ticket_id=feature_id
    )
    
    async def _run():
        cases, formatted = await _generate_internal(req, provider)
        click.echo(f"Generated {len(cases)} test cases from feature {feature_id}")
        click.echo(f"Feature: {feature.name}")
        click.echo(f"Provider: {provider}")
        
        if formatted:
            if output_path:
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(formatted)
                click.echo(f"Formatted output written to {output_path}")
            else:
                click.echo(formatted)
    
    asyncio.run(_run())


if __name__ == "__main__":
    cli()
