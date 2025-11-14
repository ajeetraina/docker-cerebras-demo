# Fix: Cerebras Function Calling with Llama 3.1-8B

This branch fixes the function calling issues when using Cerebras API with the DevDuck agent.

## Problem

When using `llama-3.3-70b` with Cerebras, the agent encountered errors:
- `"Failed to generate tool_calls. Please adjust your prompt"`
- Tool calls were output as text instead of being executed

## Root Cause

**Llama 3.3 70B does not support function calling on Cerebras.** Only Llama 3.1 models support this feature.

## Solution

This branch includes the following fixes:

### 1. **Switch to Llama 3.1-8B** (✅ Supports Function Calling)
   - Updated `.env-sample` to use `llama-3.1-8b`
   - This is the only Llama 3.1 model available on Cerebras that supports function calling

### 2. **Force Proper Tool Calling**
   - Added `tool_choice='auto'` to ensure the model uses tools
   - Added `parallel_tool_calls=False` for better compatibility
   - These settings are in `agents/devduck/sub_agents/cerebras/agent.py`

### 3. **Enable Debug Logging**
   - Enabled LiteLLM debug mode in `agents/main.py`
   - Helps troubleshoot any remaining issues

### 4. **Improved Agent Instructions**
   - Enhanced `compose.yml` with detailed tool usage examples
   - Added step-by-step workflow for documentation search

## How to Use

### 1. Update your `.env` file:

```bash
CEREBRAS_API_KEY=your_cerebras_api_key_here
CEREBRAS_BASE_URL=https://api.cerebras.ai/v1
CEREBRAS_CHAT_MODEL=llama-3.1-8b  # ← Use this model
```

### 2. Checkout this branch:

```bash
git checkout fix/cerebras-llama31-tool-calling
```

### 3. Start the services:

```bash
docker compose down
docker compose up --build
```

### 4. Test the agent:

1. Connect to Cerebras agent: `"Connect me to cerebras agent"`
2. Search documentation: `"Search documentation for Express Routing"`
3. The agent should now:
   - Call `resolve-library-id` with `libraryName: "express"`
   - Call `get-library-docs` with the resolved library ID
   - Return documentation about Express routing

## What Was Changed

### Files Modified:

1. **`agents/devduck/sub_agents/cerebras/agent.py`**
   - Added `tool_choice='auto'`
   - Added `parallel_tool_calls=False`
   - Enhanced the `CerebrasCompatibleLiteLlm` class

2. **`agents/main.py`**
   - Enabled LiteLLM debug logging
   - Uncommented `litellm.set_verbose = True`
   - Uncommented `litellm._turn_on_debug()`

3. **`.env-sample`**
   - Updated to use `llama-3.1-8b`
   - Added comments explaining model requirements

4. **`compose.yml`**
   - Enhanced Cerebras agent instructions
   - Added detailed tool usage workflow
   - Added examples for documentation search

## Debugging

If you still see issues, check the logs:

```bash
docker compose logs -f devduck-agent
```

Look for:
- `POST Request Sent from LiteLLM` - shows the request details
- `tool_calls` in responses - confirms tools are being called
- Any error messages with `APIConnectionError`

## Available Cerebras Models

From the Cerebras Playground, these models are available:

- ✅ `llama-3.1-8b` - Supports function calling (RECOMMENDED)
- ❌ `llama-3.3-70b` - Does NOT support function calling
- 🔍 `qwen-3-32b` - Unknown function calling support
- 🔍 `qwen3-235b` - Unknown function calling support

## Testing Checklist

- [ ] Agent connects successfully
- [ ] `resolve-library-id` is called (not just printed as text)
- [ ] `get-library-docs` is called with the resolved ID
- [ ] Documentation is returned and displayed
- [ ] No `APIConnectionError` about tool_calls

## Additional Notes

- Llama 3.1-8B is smaller than Llama 3.3-70B but handles function calling properly
- If you need more powerful responses without tools, use Llama 3.3-70B and disable tools
- The `CerebrasCompatibleLiteLlm` class filters out JSON schema fields that Cerebras doesn't support

## Need Help?

If you encounter issues:
1. Check that your `.env` file has the correct model: `llama-3.1-8b`
2. Verify debug logs are showing tool calls (not just text output)
3. Ensure your Cerebras API key is valid
4. Check that MCP gateway is running: `docker compose ps mcp-gateway`

---

**Status:** ✅ Ready for testing
**Model:** `llama-3.1-8b` with function calling
**Branch:** `fix/cerebras-llama31-tool-calling`
