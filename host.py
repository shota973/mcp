import asyncio
import json
from openai import OpenAI
from fastmcp import Client
from fastmcp.client.transports import PythonStdioTransport, NodeStdioTransport
# OpenAIのクライアントの準備
client = OpenAI(
    base_url = 'http://localhost:11434/v1',
    api_key='ollama', # required, but unused
)

# サーバースクリプトのパス
MY_SERVER_SCRIPT = "server.py"

# MCPサーバからツールスキーマを取得
async def get_tools():
    my_server_transport = PythonStdioTransport(script_path=MY_SERVER_SCRIPT)
    async with Client(my_server_transport) as my_server_client:
        tools = await my_server_client.list_tools()
        return tools

# MCPサーバのツールを呼び出す
async def call_tool(tool_name, tool_args):
    my_server_transport = PythonStdioTransport(script_path=MY_SERVER_SCRIPT)
    async with Client(my_server_transport) as my_server_client:
        result = await my_server_client.call_tool(tool_name, tool_args)
        return result

def main():
    # メッセージリストの準備
    messages = [
        {"role": "user", "content": "Strawberryに含まれるrの数を数えてください。"}
    ]    

    # ツールの準備
    tools = [
        {
            "type": "function",
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.inputSchema
        }
        for tool in asyncio.run(get_tools())
    ]
    print("ツール:", tools)
    tools = [{
      "type": "function",
      "function": {
        "name": "letter_counter",
        "description": "単語の中に文字が何回現れるかを数える。大文字と小文字を区別しない",
        "parameters": {
          "type": "object",
          "properties": {
            "word": {
              "type": "string",
              "description": "分析する単語またはフレーズ"
            },
            "letter": {
              "type": "string",
              "description": "出現回数を数える文字"
            }
          },
          "required": ["word", "letter"]
        }
      }
    }]

    # 推論の実行
    response = client.chat.completions.create(
        model="qwen3:32b",
        messages=messages,
        tools=tools
    )
    print("応答:", response.choices[0].message)
    if response.choices[0].finish_reason == "tool_calls":
        # 関数呼び出し
        tool_calls = response.choices[0].message.tool_calls
        calling_message = vars(response.choices[0].message)
        messages.append(calling_message)
        for tool_call in tool_calls:
            print("関数呼び出し:", tool_call)

            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            result = asyncio.run(call_tool(tool_name, tool_args))
            print("関数呼び出し結果:", result)
            # メッセージリストの準備
            messages.append({
                "type": "function_call_output",
                "call_id": tool_call.id,
                "output": str(result),
                "content": "the result of tool: " + tool_name + " is "+ str(result) + '. Make your answer of "' + messages[0]["content"] + '"',
            })

            print(messages)

        # 推論の実行
        response2 = client.chat.completions.create(
            model="qwen3:32b",
            messages=messages,
            tools=tools,
        )
        print("応答:", response2)        
    else:
        print("関数呼び出しが見つかりませんでした。")

if __name__ == "__main__":
    main()