"""Small Bedrock Converse helper used by probes and smoke runs."""

from __future__ import annotations

import os
import time
from functools import lru_cache
from typing import Any


MODEL_CANDIDATES: dict[str, list[tuple[str, str]]] = {
    "qwen3_235b_a22b_2507_bedrock": [
        ("qwen.qwen3-235b-a22b-2507-v1:0", "expected"),
        ("qwen.qwen3-coder-480b-a35b-v1:0", "substitute_qwen3_coder_480b_a35b"),
        ("qwen.qwen3-vl-235b-a22b", "substitute_qwen3_vl_235b_a22b"),
        ("qwen.qwen3-next-80b-a3b", "substitute_qwen3_next_80b_a3b"),
        ("qwen.qwen3-coder-30b-a3b-v1:0", "substitute_qwen3_coder_30b_a3b"),
        ("qwen.qwen3-32b-v1:0", "substitute_qwen3_32b"),
    ],
    "qwen3_coder_480b_a35b_bedrock": [
        ("qwen.qwen3-coder-480b-a35b-v1:0", "expected"),
        ("qwen.qwen3-235b-a22b-2507-v1:0", "substitute_qwen3_235b_a22b_2507"),
        ("qwen.qwen3-coder-30b-a3b-v1:0", "substitute_qwen3_coder_30b_a3b"),
    ],
    "deepseek_v3_2_bedrock": [
        ("deepseek.v3.2", "expected"),
        ("deepseek.r1-v1:0", "substitute_deepseek_r1"),
        ("moonshot.kimi-k2-thinking", "substitute_kimi_k2_thinking"),
    ],
    "gpt_5_4_bedrock": [
        ("openai.gpt-5.4", "expected"),
        ("openai.gpt-oss-120b-1:0", "substitute_gpt_oss_120b"),
        ("openai.gpt-oss-20b-1:0", "substitute_gpt_oss_20b"),
    ],
    "gpt_5_5_bedrock": [
        ("openai.gpt-5.5", "expected"),
        ("openai.gpt-oss-120b-1:0", "substitute_gpt_oss_120b"),
        ("openai.gpt-oss-20b-1:0", "substitute_gpt_oss_20b"),
    ],
    "claude_opus_4_8_bedrock": [
        ("us.anthropic.claude-opus-4-8", "expected_inference_profile"),
        ("anthropic.claude-opus-4-8", "expected_foundation_model_requires_profile"),
        ("anthropic.claude-opus-4-6-v1", "substitute_claude_opus_4_6"),
        ("anthropic.claude-sonnet-4-6", "substitute_claude_sonnet_4_6"),
    ],
}

MODEL_REGION_PREFERENCES: dict[str, list[str]] = {
    "qwen3_235b_a22b_2507_bedrock": ["us-east-2", "us-west-2", "ap-south-1", "ap-northeast-1", "eu-west-2", "eu-north-1"],
    "qwen3_coder_480b_a35b_bedrock": ["us-east-2", "us-west-2", "ap-south-1", "ap-northeast-1", "eu-west-2", "eu-north-1"],
    "deepseek_v3_2_bedrock": ["us-east-1", "us-east-2", "us-west-2"],
    "gpt_5_4_bedrock": ["us-east-1"],
    "gpt_5_5_bedrock": ["us-east-1"],
    "claude_opus_4_8_bedrock": ["us-east-1", "us-east-2", "us-west-2"],
}


def configure_credentials(region: str, credential_source: str = "ec2-role") -> None:
    """Match the working /home/ubuntu/qwen_bedrock_test.sh credential mode."""

    os.environ["AWS_REGION"] = region
    os.environ["AWS_DEFAULT_REGION"] = region
    if credential_source == "ec2-role":
        for key in ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN", "AWS_PROFILE"):
            os.environ.pop(key, None)
        os.environ["AWS_EC2_METADATA_DISABLED"] = "false"
        os.environ["AWS_SHARED_CREDENTIALS_FILE"] = "/tmp/nonexistent-aws-credentials"
        os.environ["AWS_CONFIG_FILE"] = "/tmp/nonexistent-aws-config"


def identity(region: str, credential_source: str = "ec2-role") -> dict[str, Any]:
    configure_credentials(region, credential_source)
    import boto3

    return boto3.client("sts", region_name=region).get_caller_identity()


@lru_cache(maxsize=16)
def available_model_ids(region: str, credential_source: str = "ec2-role") -> frozenset[str]:
    configure_credentials(region, credential_source)
    import boto3

    summaries = boto3.client("bedrock", region_name=region).list_foundation_models().get("modelSummaries", [])
    return frozenset(summary["modelId"] for summary in summaries)


@lru_cache(maxsize=16)
def available_inference_profile_ids(region: str, credential_source: str = "ec2-role") -> frozenset[str]:
    configure_credentials(region, credential_source)
    import boto3

    summaries = boto3.client("bedrock", region_name=region).list_inference_profiles().get(
        "inferenceProfileSummaries", []
    )
    return frozenset(summary["inferenceProfileId"] for summary in summaries)


def available_invocable_ids(region: str, credential_source: str = "ec2-role") -> frozenset[str]:
    return available_model_ids(region, credential_source) | available_inference_profile_ids(region, credential_source)


def select_model(
    logical_model: str,
    region: str,
    credential_source: str = "ec2-role",
    strict_expected: bool = False,
) -> tuple[str, str]:
    """Return a concrete Bedrock model ID and whether it is expected/substitute."""

    candidates = MODEL_CANDIDATES.get(logical_model, [(logical_model, "literal")])
    if strict_expected:
        return candidates[0]
    available = available_invocable_ids(region, credential_source)
    for model_id, role in candidates:
        if model_id in available:
            return model_id, role
    return candidates[0][0], "not_listed_using_expected"


def select_region_and_model(
    logical_model: str,
    requested_region: str = "auto",
    credential_source: str = "ec2-role",
    strict_expected: bool = False,
) -> tuple[str, str, str]:
    regions = (
        MODEL_REGION_PREFERENCES.get(logical_model, ["us-east-1"])
        if requested_region in {"", "auto"}
        else [requested_region, *[r for r in MODEL_REGION_PREFERENCES.get(logical_model, []) if r != requested_region]]
    )
    candidates = MODEL_CANDIDATES.get(logical_model, [(logical_model, "literal")])
    candidates = candidates[:1] if strict_expected else candidates
    first_error: str | None = None
    available_by_region: dict[str, frozenset[str]] = {}
    for region in regions:
        try:
            available_by_region[region] = available_invocable_ids(region, credential_source)
        except Exception as exc:
            first_error = f"{type(exc).__name__}: {exc}"
    for model_id, resolution in candidates:
        for region in regions:
            if model_id in available_by_region.get(region, frozenset()):
                return region, model_id, resolution
    if first_error and not available_by_region:
        raise RuntimeError(first_error)
    return regions[0], candidates[0][0], "not_listed_using_expected"


def converse_text(
    logical_model: str,
    prompt: str,
    region: str = "auto",
    credential_source: str = "ec2-role",
    max_tokens: int = 8,
    temperature: float = 0.0,
    strict_expected: bool = False,
) -> dict[str, Any]:
    """Make one tiny Bedrock Converse request and return normalized metadata."""

    import boto3

    region, model_id, resolution = select_region_and_model(logical_model, region, credential_source, strict_expected)
    configure_credentials(region, credential_source)
    runtime = boto3.client("bedrock-runtime", region_name=region)
    started = time.time()
    inference_config: dict[str, Any] = {"maxTokens": max_tokens, "temperature": temperature}
    try:
        response = runtime.converse(
            modelId=model_id,
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig=inference_config,
        )
    except Exception as exc:
        if "temperature" not in str(exc).lower() or "deprecated" not in str(exc).lower():
            raise
        response = runtime.converse(
            modelId=model_id,
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"maxTokens": max_tokens},
        )
        resolution = f"{resolution}+no_temperature_retry"
    elapsed = time.time() - started
    text = "".join(
        part.get("text", "")
        for part in response.get("output", {}).get("message", {}).get("content", [])
    )
    usage = response.get("usage", {})
    metrics = response.get("metrics", {})
    return {
        "logical_model": logical_model,
        "model_id": model_id,
        "model_resolution": resolution,
        "region": region,
        "text": text,
        "usage": usage,
        "metrics": metrics,
        "stop_reason": response.get("stopReason"),
        "latency_s": elapsed,
    }
