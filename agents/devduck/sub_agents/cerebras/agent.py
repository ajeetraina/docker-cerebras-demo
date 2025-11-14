import os
from typing import Any, Dict

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from .tools import create_mcp_toolsets


class CerebrasCompatibleLiteLlm(LiteLlm):
    """LiteLLM wrapper that filters out Cerebras-unsupported JSON schema fields
    and ensures proper function calling behavior."""
    
    def _filter_json_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively remove unsupported JSON schema fields."""
        if not isinstance(schema, dict):
            return schema
            
        filtered = {}
        unsupported_fields = {'min_length', 'minLength', 'max_length', 'maxLength', 'pattern'}
        
        for key, value in schema.items():
            if key in unsupported_fields:
                continue  # Skip unsupported fields
            elif isinstance(value, dict):
                filtered[key] = self._filter_json_schema(value)
            elif isinstance(value, list):
                filtered[key] = [self._filter_json_schema(item) if isinstance(item, dict) else item for item in value]
            else:
                filtered[key] = value
                
        return filtered
    
    async def acompletion(self, *args, **kwargs):
        """Override acompletion to filter tool schemas and configure for Cerebras."""
        if 'tools' in kwargs and kwargs['tools']:
            # Filter unsupported schema fields
            filtered_tools = []
            for tool in kwargs['tools']:
                if isinstance(tool, dict) and 'function' in tool:
                    filtered_tool = tool.copy()
                    if 'parameters' in filtered_tool['function']:
                        filtered_tool['function']['parameters'] = self._filter_json_schema(
                            filtered_tool['function']['parameters']
                        )
                    filtered_tools.append(filtered_tool)
                else:
                    filtered_tools.append(tool)
            kwargs['tools'] = filtered_tools
            
            # Force auto tool choice for Cerebras - CRITICAL for function calling
            if 'tool_choice' not in kwargs:
                kwargs['tool_choice'] = 'auto'
            
            # Disable parallel tool calls - Cerebras doesn't support this yet
            kwargs['parallel_tool_calls'] = False
            
        return await super().acompletion(*args, **kwargs)


tools = create_mcp_toolsets()

cerebras_agent = Agent(
    model=CerebrasCompatibleLiteLlm(
        model=f"openai/{os.environ.get('CEREBRAS_CHAT_MODEL')}",
        api_base=os.environ.get("CEREBRAS_BASE_URL"),
        api_key=os.environ.get("CEREBRAS_API_KEY"),
        temperature=0.0,
    ),
    name=os.environ.get("CEREBRAS_AGENT_NAME"),
    description=os.environ.get("CEREBRAS_AGENT_DESCRIPTION"),
    instruction=os.environ.get("CEREBRAS_AGENT_INSTRUCTION"),
    tools=tools,
)
