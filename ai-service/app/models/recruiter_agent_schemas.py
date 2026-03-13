from typing import Any, Optional

from pydantic import BaseModel


class RecruiterAgentGenerateRequest(BaseModel):
    model: str
    messages: list[dict[str, Any]]
    tools: Optional[list[dict[str, Any]]] = None
    tool_choice: Optional[str] = "auto"
    temperature: Optional[float] = 0.3
    max_new_tokens: Optional[int] = 512


class RecruiterAgentAssistantMessage(BaseModel):
    content: Optional[str] = None
    tool_calls: Optional[list[dict[str, Any]]] = None


class RecruiterAgentGenerateResponse(BaseModel):
    assistant: dict[str, Any]
