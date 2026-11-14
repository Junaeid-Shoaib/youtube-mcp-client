import asyncio
from langchain_mcp_adapters import client
from langchain_mcp_adapters.client import MultiServerMCPClient
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import ToolMessage
import os

load_dotenv()

SERVERS = {
    # "expense": {
    #     "transport": "stdio",
    #     "command": "uv",
    #     "args": [
    #         "run",
    #         "--project",
    #         "/Users/junaeidshoaib/Documents/Projects/MCP/Expense-tracker-mcp-server",
    #         "fastmcp",
    #         "run",
    #         "/Users/junaeidshoaib/Documents/Projects/MCP/Expense-tracker-mcp-server/src/expense_tracker_mcp_server/main2.py"
    #     ]
    # },

    "expense-remote":{
        
        "transport": "streamable_http",
        "url": "https://aj-mcp-test.fastmcp.app/mcp",
        "headers": {
            "Authorization": f"Bearer {os.environ['HORIZON_API_KEY']}"
        }
    }
}

async def main():
    print("Starting MultiServerMCPClient...")
    client = MultiServerMCPClient(SERVERS)
    
    tools = await client.get_tools()

    named_tool = {}
    for tool in tools:
        named_tool[tool.name] = tool



    llm = ChatAnthropic(model="claude-haiku-5-5")
    llm_with_tools = llm.bind_tools(tools)

    prompt = "Add an expense of gbp 150 for travel on 2026-10-16. And summarize the all expenses"


    #[
    # response = await llm_with_tools.ainvoke([prompt])

    # if not getattr(response, "tool_calls", None):
    #     print(response.content)
    #     return

    #single tool call
    # selected_tool =response.tool_calls[0]["name"]
    # selected_args = response.tool_calls[0]["args"]
    # selected_tool_id = response.tool_calls[0]["id"]

    # tool_result = await named_tool[selected_tool].ainvoke(selected_args)

    # tool_message = ToolMessage(content=tool_result, tool_call_id=selected_tool_id)

    # final_response = await llm_with_tools.ainvoke([prompt, response, tool_message])

    #multiple tool calls
    # tool_messages = []
    # for call in response.tool_calls:
    #     result = await named_tool[call["name"]].ainvoke(call["args"])
    #     tool_messages.append(ToolMessage(content=result, tool_call_id=call["id"]))

    # final_response = await llm_with_tools.ainvoke([prompt, response] + tool_messages)

    # print("Final response:", final_response.content)
    #]

    #muti trip tool calls

    messages = [prompt]
    while True:
        response = await llm_with_tools.ainvoke(messages)
        
        if not response.tool_calls:
            content = response.content                      # 1
            if isinstance(content, str):                    # 2
                text = content                              # 3
            else:                                           # 4
                text = "".join(b["text"] for b in content if b.get("type") == "text")   # 5
            print("Final response:", text)                  # 6
            break                                           # 7

        messages.append(response)
        for call in response.tool_calls:
            result = await named_tool[call["name"]].ainvoke(call["args"])
            messages.append(ToolMessage(content=result, tool_call_id=call["id"]))


if __name__ == "__main__":
    asyncio.run(main())

