import json
from typing import Any, Optional

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


_model = None
_tokenizer = None


def load_model(model_id: str) -> None:
    global _model, _tokenizer
    if _model is not None and _tokenizer is not None:
        return

    _tokenizer = AutoTokenizer.from_pretrained(model_id)

    dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    _model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=dtype,
        device_map="auto" if torch.cuda.is_available() else None,
    )


def _format_chat(messages: list[dict[str, Any]]) -> str:
    # Simple deterministic prompt format to elicit JSON tool calling
    parts: list[str] = []
    for m in messages:
        role = m.get("role")
        content = m.get("content", "")
        if role == "system":
            parts.append(f"[SYSTEM]\n{content}")
        elif role == "user":
            parts.append(f"[USER]\n{content}")
        elif role == "assistant":
            parts.append(f"[ASSISTANT]\n{content}")
        elif role == "tool":
            name = m.get("name")
            parts.append(f"[TOOL:{name}]\n{content}")

    parts.append(
        "[ASSISTANT]\n"
        "Respond ONLY as JSON with this schema: "
        '{"content": string|null, "tool_calls": [{"id": string, "function": {"name": string, "arguments": object}}] | []}. '
        "If you want to message the candidate, use the tool send_message. "
        "If qualified, schedule_interview with an ISO UTC datetime string."
    )
    return "\n\n".join(parts)


def generate(
    model_id: str,
    messages: list[dict[str, Any]],
    tools: Optional[list[dict[str, Any]]] = None,
    temperature: float = 0.3,
    max_new_tokens: int = 512,
) -> dict:
    load_model(model_id)

    prompt = _format_chat(messages)

    inputs = _tokenizer(prompt, return_tensors="pt")
    if torch.cuda.is_available():
        inputs = {k: v.to(_model.device) for k, v in inputs.items()}

    with torch.no_grad():
        out = _model.generate(
            **inputs,
            do_sample=temperature > 0,
            temperature=temperature,
            max_new_tokens=max_new_tokens,
            pad_token_id=_tokenizer.eos_token_id,
        )

    text = _tokenizer.decode(out[0], skip_special_tokens=True)
    json_str = text.split("[ASSISTANT]")[-1].strip()

    try:
        parsed = json.loads(json_str)
    except Exception:
        parsed = {"content": json_str, "tool_calls": []}

    if "tool_calls" not in parsed:
        parsed["tool_calls"] = []

    return parsed
