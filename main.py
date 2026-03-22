import os
import json
import argparse
import logging
from pydantic import BaseModel
from typing import List, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv

from tools.list_files import list_files
from tools.read_file import read_file
from tools.write_file import write_file

load_dotenv()


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    handlers=[logging.FileHandler("agent.log")],
)

# Suppress verbose HTTP logs
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)


class Tool(BaseModel):
    name: str
    description: str
    input_schema: Dict[str, Any]


def get_client() -> OpenAI:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is not set. Add it to your environment or .env file."
        )

    return OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1",
    )


class AIAgent:
    def __init__(self):
        self.client = get_client()
        self.messages: List[Dict[str, Any]] = [
            {
                "role": "system",
                "content": """You are a helpful coding AI agent that can perform file operations. You have access to three tools:
1. read_file - to read file contents
2. list_files - to list directory contents  
3. write_file - to create or modify files

When you need to use a tool, the system will provide the function calling mechanism. Always call the appropriate tool when needed to accomplish user tasks. After using a tool, the result will be provided to you for further processing or response.

Provide clear, helpful responses in plain text. Be concise and direct.""",
            }
        ]
        self.tools: List[Tool] = []
        self.setup_tools()

    def setup_tools(self):
        self.tools = [
            Tool(
                name="read_file",
                description="Read the contents of a file at the specified path",
                input_schema={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "The path to the file to read",
                        }
                    },
                    "required": ["path"],
                },
            ),
            Tool(
                name="list_files",
                description="List all files and directories in the specified path",
                input_schema={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "The directory path to list (defaults to current directory)",
                        }
                    },
                    "required": [],
                },
            ),
            Tool(
                name="write_file",
                description="Write the contents to the specified file in the directory",
                input_schema={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "The path to the file to edit",
                        },
                        "old_text": {
                            "type": "string",
                            "description": "The text to search for and replace (leave empty to create new file)",
                        },
                        "new_text": {
                            "type": "string",
                            "description": "The text to replace old_text with",
                        },
                    },
                    "required": ["path", "new_text"],
                },
            ),
        ]

    def execute_tools(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        logging.info(f"Executing tool : {tool_name} with the input : {tool_input}")
        try:
            if tool_name == "read_file":
                return read_file(tool_input["path"])
            elif tool_name == "list_files":
                return list_files(tool_input.get("path", "."))
            elif tool_name == "write_file":
                return write_file(
                    tool_input["path"],
                    tool_input.get("old_text", ""),
                    tool_input["new_text"],
                )
            else:
                return f"Unknown tool: {tool_name}"
        except Exception as e:
            logging.error(f"Error executing {tool_name}: {str(e)}")
            return f"Error executing {tool_name}: {str(e)}"

    def chat(self, query: str):
        logging.info(f"User query : {query}")

        self.messages.append({"role": "user", "content": query})

        tool_schemas = [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.input_schema,
                },
            }
            for tool in self.tools
        ]

        max_iterations = 10  # Prevent infinite loops
        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            try:
                response = self.client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=self.messages,  # type: ignore
                    tools=tool_schemas,  # type: ignore
                    max_tokens=4096,
                )

                assistant_message = response.choices[0].message

                # Add assistant's response to messages
                message_to_append = {
                    "role": "assistant",
                    "content": assistant_message.content,
                }

                # Only add tool_calls if they exist - convert to dict for proper serialization
                if assistant_message.tool_calls:
                    message_to_append["tool_calls"] = [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,  # type: ignore
                                "arguments": tc.function.arguments,  # type: ignore
                            },
                        }
                        for tc in assistant_message.tool_calls
                    ]

                self.messages.append(message_to_append)

                # Check if there are tool calls
                if assistant_message.tool_calls:
                    logging.info(
                        f"Iteration {iteration}: Processing {len(assistant_message.tool_calls)} tool call(s)"
                    )
                    for tool_call in assistant_message.tool_calls:
                        tool_name = tool_call.function.name  # type: ignore
                        tool_input = json.loads(tool_call.function.arguments)  # type: ignore

                        tool_result = self.execute_tools(tool_name, tool_input)
                        logging.info(f"Tool Response : {tool_result[:300]}")

                        # Add tool result to messages
                        self.messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": tool_call.id,  # type: ignore
                                "content": tool_result,
                            }
                        )
                else:
                    # No tool calls, return final response
                    logging.info(f"Completed after {iteration} iteration(s)")
                    return (
                        assistant_message.content if assistant_message.content else ""
                    )

            except Exception as e:
                logging.error(f"Error in iteration {iteration}: {str(e)}")
                return f"Error executing : {str(e)}"

        # If we've hit max iterations, return an error
        logging.error(f"Maximum iterations ({max_iterations}) reached")
        return "Error: Agent exceeded maximum iteration limit. The task may require too many tool calls."


def main():
    parser = argparse.ArgumentParser(
        description="AI Code Assistant - A conversational AI agent with file editing capabilities"
    )
    parser.add_argument(
        "--api-key", help="Anthropic API key (or set ANTHROPIC_API_KEY env var)"
    )
    agent = AIAgent()

    print("AI Code Assistant")
    print("================")
    print("A conversational AI agent that can read, list, and edit files.")
    print("Type 'exit' or 'quit' to end the conversation.")
    print()

    while True:
        try:
            user_input = input("You: ").strip()

            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break

            if not user_input:
                continue

            print("\nAssistant: ", end="", flush=True)
            response = agent.chat(user_input)
            logging.info(f"Response for the query : {response}")
            print(response)
            print()

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")
            print()


if __name__ == "__main__":
    main()
