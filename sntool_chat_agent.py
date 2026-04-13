"""Terminal chat agent grounded only in the local SNTool data file."""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any

from openai import OpenAI


MODEL_NAME = "gpt-4o"
FALLBACK_MESSAGE = "Sorry i dont know the answer because of my access limitations."
DEFAULT_JSON_FILENAME = "sntool_database.json"


def resolve_database_path(file_name: str = DEFAULT_JSON_FILENAME) -> Path:
    """Return the SNTool data file path, supporting the current workspace layout."""
    candidates = [
        Path(file_name),
        Path("database") / file_name,
    ]

    for path in candidates:
        if path.is_file():
            return path

    raise FileNotFoundError(
        f"Could not find '{file_name}' in the current directory or inside 'database/'."
    )


def load_json_file(file_name: str = DEFAULT_JSON_FILENAME) -> dict[str, Any] | list[Any]:
    """Load the SNTool knowledge base from disk.

    The preferred format is valid JSON. For compatibility with the file currently
    present in this workspace, the loader also supports a Python file that defines
    a top-level `data = {...}` literal.
    """

    file_path = resolve_database_path(file_name)
    raw_text = file_path.read_text(encoding="utf-8")

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        parsed = ast.parse(raw_text, filename=str(file_path))

        for node in parsed.body:
            if not isinstance(node, ast.Assign):
                continue

            if not any(isinstance(target, ast.Name) and target.id == "data" for target in node.targets):
                continue

            try:
                value = ast.literal_eval(node.value)
            except (ValueError, SyntaxError) as exc:
                raise ValueError(
                    f"The file '{file_path}' is not valid JSON and its `data` value "
                    "could not be parsed safely."
                ) from exc

            if isinstance(value, (dict, list)):
                return value

        raise ValueError(
            f"The file '{file_path}' is not valid JSON and does not contain a "
            "top-level `data = {{...}}` or `data = [...]` literal."
        )


def build_system_prompt(knowledge_base: dict[str, Any] | list[Any]) -> str:
    """Create the strict grounding prompt with the full SNTool content embedded."""

    knowledge_json = json.dumps(knowledge_base, ensure_ascii=False, indent=2)

    return f"""
You are an English-language AI assistant for the Sustainable Neighbourhoods Tool (SNTool).

You must answer strictly and only from the SNTool knowledge base included below.
Do not use outside knowledge, assumptions, guesses, or web information.
Do not add facts that are not explicitly supported by the knowledge base.
If the answer is not present in the knowledge base, reply with exactly:
{FALLBACK_MESSAGE}

SNTool knowledge base:
{knowledge_json}
""".strip()


def wrap_user_query(user_input: str) -> str:
    """Enrich each user question with strict analysis instructions."""

    return f"""
Analyze the SNTool knowledge base carefully before answering.
Check the JSON structure and fields step by step.
Answer only with information grounded in the provided SNTool data.
If the requested information is missing or not explicit in the data, reply with exactly:
{FALLBACK_MESSAGE}
Respond in English only.

User question:
{user_input}
""".strip()


def ask_agent(
    client: OpenAI,
    system_prompt: str,
    history: list[dict[str, str]],
    user_input: str,
) -> str:
    """Send the conversation to OpenAI and return the grounded answer."""

    wrapped_input = wrap_user_query(user_input)
    messages = [{"role": "system", "content": system_prompt}, *history, {"role": "user", "content": wrapped_input}]

    response = client.chat.completions.create(
        model=MODEL_NAME,
        temperature=0,
        messages=messages,
    )

    answer = (response.choices[0].message.content or "").strip()
    if not answer:
        answer = FALLBACK_MESSAGE

    history.append({"role": "user", "content": wrapped_input})
    history.append({"role": "assistant", "content": answer})
    return answer


def main() -> None:
    """Run the terminal chat loop with conversation memory."""

    knowledge_base = load_json_file()
    system_prompt = build_system_prompt(knowledge_base)
    client = OpenAI()
    history: list[dict[str, str]] = []

    print("SNTool grounded chat assistant")
    print("Type your question in English. Type 'exit', 'quit', or 'bye' to stop.")

    while True:
        user_input = input("\nYou: ").strip()

        if user_input.lower() in {"exit", "quit", "bye"}:
            print("Assistant: Goodbye.")
            break

        if not user_input:
            print("Assistant: Please enter a question or type 'exit' to quit.")
            continue

        try:
            answer = ask_agent(
                client=client,
                system_prompt=system_prompt,
                history=history,
                user_input=user_input,
            )
        except Exception as exc:
            print(f"Assistant: Error: {exc}")
            continue

        print(f"Assistant: {answer}")


if __name__ == "__main__":
    main()
