import json
import os
from pathlib import Path

from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent
from strands.models import BedrockModel
from strands_tools.code_interpreter import AgentCoreCodeInterpreter

app = BedrockAgentCoreApp()
log = app.logger

REGION = "ap-northeast-1"
MODEL_ID = "jp.anthropic.claude-haiku-4-5-20251001-v1:0"
SYSTEM_PROMPT = Path(__file__).with_name("system_prompt.md").read_text(encoding="utf-8")


@app.entrypoint
async def invoke(payload, context):
    # モデル選択
    model = BedrockModel(
        model_id=MODEL_ID,
        region_name=REGION,
    )

    # Create code interpreter
    code_interpreter = AgentCoreCodeInterpreter(
        region=REGION,
        identifier=os.environ["CODE_INTERPRETER_ID"],
    )

    agent = Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=[code_interpreter.code_interpreter],
        callback_handler=None,
    )
    prompt = json.dumps(payload, ensure_ascii=False)
    stream = agent.stream_async(prompt)
    async for event in stream:
        # Handle Text parts of the response
        if "data" in event and isinstance(event["data"], str):
            yield event["data"]

        # Implement additional handling for other events
        # if "toolUse" in event:
        #   # Process toolUse

        # Handle end of stream
        # if "result" in event:
        #    yield(format_response(event["result"]))


def format_response(result) -> str:
    """Extract code from metrics and format with LLM response."""
    parts = []

    # Extract executed code from metrics
    try:
        tool_metrics = result.metrics.tool_metrics.get("code_interpreter")
        if tool_metrics and hasattr(tool_metrics, "tool"):
            action = tool_metrics.tool["input"]["code_interpreter_input"]["action"]
            if "code" in action:
                parts.append(f"## Executed Code:\n```{action.get('language', 'python')}\n{action['code']}\n```\n---\n")
    except (AttributeError, KeyError):
        pass  # No code to extract

    # Add LLM response
    parts.append(f"## 📊 Result:\n{result!s}")
    return "\n".join(parts)


if __name__ == "__main__":
    app.run()
