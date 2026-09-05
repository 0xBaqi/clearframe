"""Amazon Bedrock-backed Strands adapter; domain logic remains outside this module."""
from __future__ import annotations

from typing import Callable

from adapters.strands.config import StrandsConfig
from adapters.strands.tools import build_strands_tools
from packages.agent_contract import AgentActionExecutor, AgentActionRequest, AgentActionResult, AgentProvider
from packages.core.clearance import ClearanceEngine
from packages.core.evidence import EvidenceRepository
from packages.core.types import ClearanceResult, ProjectIntent

SYSTEM_PROMPT = """You are ClearFrame's administrative clearance operator. Perform only administrative evidence operations using the supplied tools. No legal advice, no fair-use determination, and no claim that a project is legally safe. When evidence cannot establish an administrative result or legal ambiguity appears, request human review. Never mutate state except through the supplied application-service tools."""

class ProviderExecutionError(RuntimeError):
    """A visible, non-fallback error from the configured live provider."""


class StrandsProvider(AgentProvider, AgentActionExecutor):
    """Real Strands/Bedrock provider with a narrow, application-service tool surface."""
    def __init__(self, repository: EvidenceRepository, service, config: StrandsConfig | None = None, agent_factory: Callable | None = None, tool_factory: Callable | None = None):
        self.repository = repository
        self.service = service
        self.config = config or StrandsConfig.from_env()
        self.agent_factory = agent_factory
        self.tool_factory = tool_factory or build_strands_tools
        self._agent = None

    def _build_agent(self):
        if self._agent is not None:
            return self._agent
        self.config.validate()
        tools = self.tool_factory(self.service)
        if self.agent_factory is not None:
            self._agent = self.agent_factory(self.config, SYSTEM_PROMPT, tools)
            return self._agent
        from strands import Agent
        from strands.models import BedrockModel
        session = None
        if self.config.profile or self.config.session_name:
            import boto3
            session = boto3.Session(profile_name=self.config.profile, region_name=self.config.region)
        model = BedrockModel(model_id=self.config.model_id, region_name=self.config.region, boto_session=session, temperature=0.0)
        self._agent = Agent(model=model, system_prompt=SYSTEM_PROMPT, tools=tools, callback_handler=None)
        return self._agent

    def execute(self, request: AgentActionRequest) -> AgentActionResult:
        prompt = (f"Process the provider-neutral action {request.action} for item {request.item_id}. "
                  f"Reason: {request.reason}. Evidence ID: {request.evidence_id or 'none'}. "
                  "Use only ClearFrame tools, preserve the legal boundary, and report the administrative result.")
        try:
            response = self._build_agent()(prompt)
        except Exception as error:
            message = str(error).lower()
            category = "throttled" if "throttl" in message or "quota" in message else "access denied" if "accessdenied" in message or "expired" in message else "model unavailable" if "model" in message and "available" in message else "network/provider failure"
            raise ProviderExecutionError(f"Strands Bedrock {category}: {error}") from error
        return AgentActionResult(request.id, True, request.id, str(response))

    def run(self, intent: ProjectIntent) -> list[ClearanceResult]:
        self._build_agent()("Inspect the current clearance and evidence state using the supplied tools. Do not mutate state unless an explicit action is requested.")
        return ClearanceEngine(self.repository).run(intent)


class StrandsAgentProvider(AgentProvider):
    """Deterministic compatibility provider retained for offline local tests."""
    def __init__(self, repository: EvidenceRepository):
        self.engine = ClearanceEngine(repository)
    def run(self, intent: ProjectIntent) -> list[ClearanceResult]:
        return self.engine.run(intent)
