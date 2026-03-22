# AI Agent - File Management Assistant

A conversational AI agent powered by Groq's LLaMA 3.3-70B model that can read, list, and modify files. This agent demonstrates agentic AI capabilities with structured tool calling and iterative interactions.

## 🎯 What This Application Does

The AI Agent is a conversational interface that allows you to interact with an AI-powered assistant capable of:

- **Read Files** - Extract and display the contents of files in your workspace
- **List Directories** - Browse directory structures and see available files and folders
- **Write/Modify Files** - Create new files or edit existing ones using natural language instructions
- **Multi-turn Conversations** - Have natural conversations where the agent automatically determines which tools to use and when

The agent uses OpenAI-compatible function calling with the Groq API to intelligently interact with your filesystem through conversational prompts.

## 📋 Prerequisites

Before you start, ensure you have:

- **Python 3.14+** (as specified in `pyproject.toml`)
- **pip** or **uv** (for package management)
- **Groq API Key** - Get one for free at [Groq Console](https://console.groq.com/)

## 🚀 Installation

### 1. Clone or Download the Repository

```bash
git clone <repository-url>
cd "AI Agent"
```

### 2. Create a Virtual Environment (Optional but Recommended)

Using Python's built-in venv:

```bash
python3.14 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

Or using uv:

```bash
uv venv
source .venv/bin/activate
```

### 3. Install Dependencies

Using pip:

```bash
pip install -e .
```

Or using uv:

```bash
uv pip install -e .
```

The project depends on:
- `openai>=2.29.0` - OpenAI Python client (compatible with Groq's OpenAI-compatible API)
- `groq>=1.1.1` - Groq SDK
- `pydantic>=2.12.5` - Data validation
- `dotenv>=0.9.9` - Environment variable management

## ⚙️ Configuration

### 1. Set Up Your Groq API Key

Create a `.env` file in the project root directory:

```bash
cp .env.example .env
```

Edit `.env` and add your Groq API key:

```
GROQ_API_KEY=your_actual_api_key_here
```

You can get a free API key from [Groq Console](https://console.groq.com/).

### Environment Variables

- `GROQ_API_KEY` - Your Groq API key (required)

The application will automatically load these from the `.env` file using python-dotenv.

## 🎮 How to Start the Application

### Run the Agent

```bash
python main.py
```

### Interactive Usage

Once started, you'll see the prompt:

```
AI Code Assistant
================
A conversational AI agent that can read, list, and edit files.
Type 'exit' or 'quit' to end the conversation.

You:
```

Now you can interact with the agent naturally:

#### Example 1: List Files

```
You: List all files in the current directory
```

The agent will use the `list_files` tool to show you the directory contents.

#### Example 2: Read a File

```
You: What's in the main.py file?
```

The agent will read and summarize the main.py file.

#### Example 3: Create/Modify a File

```
You: Create a file called test.txt with some example content
```

The agent will use the `write_file` tool to create the file.

#### Example 4: Complex Tasks

```
You: Find all Python files in the tools directory and tell me what each one does
```

The agent will automatically chain multiple tool calls to complete multi-step tasks.

### Exit the Application

Type `exit` or `quit` to end the session:

```
You: exit
Goodbye!
```

## 📁 Project Structure

```
AI Agent/
├── main.py                 # Main application and AIAgent class
├── pyproject.toml          # Project configuration and dependencies
├── .env                    # Environment variables (create from .env.example)
├── .env.example            # Example environment file
├── agent.log               # Application logs (auto-generated)
├── README.md               # This file
├── .python-version         # Python version specification
├── .venv/                  # Virtual environment (auto-created)
├── .git/                   # Git repository
└── tools/
    ├── list_files.py       # Tool to list directory contents
    ├── read_file.py        # Tool to read file contents
    └── write_file.py       # Tool to create and modify files
```

## 🔧 Available Tools

### 1. read_file
Reads and returns the contents of a specified file.

**Usage:** Ask the agent to read a file
```
"What's in the README file?"
"Show me the content of main.py"
```

### 2. list_files
Lists all files and directories in a specified path.

**Usage:** Ask the agent to list files
```
"What files are in the tools directory?"
"List everything in the current folder"
```

### 3. write_file
Creates a new file or modifies an existing file with new content.

**Usage:** Ask the agent to create or modify files
```
"Create a new file called config.py with these settings"
"Update the README with new information"
"Write my notes to a file called notes.txt"
```

## 📊 Logging

The application automatically logs all activities to `agent.log`:

- User queries
- Tool executions
- Tool responses
- Errors and exceptions
- Response summaries

View recent logs:

```bash
tail -50 agent.log
```

## 🔒 Safety Features

The application includes built-in safety mechanisms:

- **Maximum Iterations Limit** - Prevents infinite loops (max 10 iterations per query)
- **Error Handling** - Gracefully handles and logs errors
- **Structured Logging** - All interactions are logged for debugging and auditing
- **Input Validation** - Uses Pydantic for data validation

## 🐛 Troubleshooting

### Issue: "GROQ_API_KEY is not set"

**Solution:** Make sure you have created a `.env` file with your API key:
```bash
cp .env.example .env
# Edit .env and add your actual Groq API key
```

### Issue: Module import errors

**Solution:** Ensure all dependencies are installed:
```bash
pip install -e .
```

Or reinstall them:
```bash
pip install --force-reinstall -e .
```

### Issue: "ModuleNotFoundError" for tools

**Solution:** Make sure you're running the script from the project root directory:
```bash
cd "/path/to/AI Agent"
python main.py
```

### Issue: Agent not responding or slow responses

**Solution:** 
- Check your internet connection
- Verify your Groq API key is valid
- Check `agent.log` for error details
- The model may have rate limits on free tier - try again in a moment

### Issue: EOF when reading input

**Solution:** If the agent exits immediately, check:
1. Your environment is properly activated (if using venv)
2. All dependencies are installed
3. Check `agent.log` for detailed error messages
