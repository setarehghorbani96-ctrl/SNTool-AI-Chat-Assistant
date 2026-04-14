# SNTool AI Chat Assistant

This is a terminal-based AI Agent designed to answer questions strictly based on the local Sustainable Neighbourhoods Tool (SNTool) database. It uses the OpenAI API (`gpt-4o`) but does **not** rely on external web searches or its own general knowledge. It is completely grounded in the local data provided in the JSON file.

## Features
* **Strict Grounding:** Only answers questions using the local JSON database. If the answer isn't in the file, it will tell you.
* **Chat Memory:** Remembers the context of the conversation so you can ask follow-up questions.
* **Prompt Wrapping:** Automatically enriches user queries behind the scenes for higher accuracy and strict adherence to the data.

## Prerequisites
To run this project on your machine, you will need:
1. **Python** installed (version 3.8 or higher is recommended).
2. Your own **OpenAI API Key** (starts with `sk-proj-`).

---

## How to Install and Run

1. Download the Code
Clone this repository to your computer and navigate into the folder:

```bash
git clone [https://github.com/
setarehghorbani96-ctrl
/SNTool-AI-Chat-Assistant.git](https://github.com/setarehghorbani96-ctrl/SNTool-AI-Chat-Assistant.git)
cd SNTool-AI-Chat-Assistant

 2. Install Dependencies
This project requires the official OpenAI Python library. Install it by running:
pip install -r requirements.txt

3. Set Your OpenAI API Key
You must provide your own API key to run the agent. Choose the command that matches your operating system and replace your-api-key-here with your actual key.

For Windows (PowerShell):
$env:OPENAI_API_KEY="your-api-key-here"

For Windows (Command Prompt):
set OPENAI_API_KEY=your-api-key-here

For Mac / Linux (Terminal):
export OPENAI_API_KEY="your-api-key-here"

4. Start the Agent
Once your key is set in the terminal, run the Python script to start chatting:
python sntool_chat_agent.py

Usage:
Type your questions in English and press Enter.
To close the application, simply type exit, quit, or bye.
