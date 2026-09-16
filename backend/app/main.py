"""
RDT Triage API - main entrypoint.
Receives incident reports, runs them through an LLM using ReAct reasoning,
validates the structured output, and returns triage results with metrics.
"""

import json
import re
import time
import traceback
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from app.models.schemas import TriageRequest, TriageResponse, TriageMetrics, TriageFullResponse
from app.prompts.triage_prompt import SYSTEM_PROMPT, build_user_prompt
from app.providers.ollama_provider import OllamaProvider
from app.providers.external_provider import ExternalProvider

load_dotenv()

app = FastAPI(title="RDT Triage API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

COST_PER_MILLION_TOKENS = {
    "ollama": {"input": 0.0, "output": 0.0},
    "external": {"input": 0.05, "output": 0.08},
}


def extract_json_from_response(raw_text: str) -> dict:
    """
    Extracts the JSON object following 'Final Answer:' in the LLM's response.
    Raises ValueError if no valid JSON is found.
    """
    match = re.search(r"Final Answer:\s*(\{.*\})", raw_text, re.DOTALL)
    if not match:
        raise ValueError("No 'Final Answer' JSON block found in model output")

    json_str = match.group(1)
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Malformed JSON in model output: {e}")


def get_provider(provider_name: str):
    if provider_name == "ollama":
        return OllamaProvider()
    elif provider_name == "external":
        return ExternalProvider()
    raise HTTPException(status_code=400, detail=f"Unknown provider: {provider_name}")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/triage", response_model=TriageFullResponse)
async def triage(request: TriageRequest):
    provider = get_provider(request.provider)
    user_prompt = build_user_prompt(request.feedback_text)

    start_time = time.perf_counter()
    try:
        raw_output, input_tokens, output_tokens = await provider.generate(SYSTEM_PROMPT, user_prompt)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=502, detail=f"LLM provider error: {type(e).__name__}: {str(e)}")
    latency_ms = (time.perf_counter() - start_time) * 1000

    try:
        parsed_json = extract_json_from_response(raw_output)
        triage_result = TriageResponse(**parsed_json)
    except (ValueError, ValidationError) as e:
        raise HTTPException(
            status_code=422,
            detail=f"Model output failed schema validation: {str(e)}"
        )

    costs = COST_PER_MILLION_TOKENS[request.provider]
    estimated_cost = (
        (input_tokens / 1_000_000) * costs["input"]
        + (output_tokens / 1_000_000) * costs["output"]
    )

    metrics = TriageMetrics(
        latency_ms=round(latency_ms, 2),
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        estimated_cost=round(estimated_cost, 6),
        provider=request.provider,
        model=provider.model_name,
    )

    return TriageFullResponse(triage=triage_result, metrics=metrics)
