import json
import re
from pathlib import Path
from typing import Any

import dvc.api
from fire import Fire
from openai import OpenAI
from tqdm import tqdm

# Initialize OpenAI client with local Ollama model
client = OpenAI(base_url="http://localhost:1234/v1", api_key="dummy_key")

# Compile regex patterns once for efficiency
SQL_PATTERN = re.compile(r"<sql>(.*?)</sql>", re.DOTALL)
REASONING_PATTERN = re.compile(r"<reasoning>(.*?)</reasoning>", re.DOTALL)


def load_prompt(schema_path: str, params: dict[str, Any]) -> str:
    """Load prompt and insert context (e.g., schema)."""
    schema = Path(schema_path).read_text()
    prompt_template = Path(params["prompt"]).read_text()
    prompt_template = prompt_template.replace("{{schema}}", schema)
    return prompt_template


def generate_sql(
    prompt_template: str,
    user_question: str,
    model: str,
    temperature: float,
) -> str:
    """Generate SQL query using the LLM"""
    filled_prompt = prompt_template.replace("{{user_question}}", user_question)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": filled_prompt}],
        temperature=temperature,
    )
    return response.choices[0].message.content


def extract_sql_and_reasoning(response: str) -> tuple[str, str]:
    """Extract SQL and reasoning from LLM response using regex"""
    sql_match = SQL_PATTERN.search(response)
    reasoning_match = REASONING_PATTERN.search(response)

    sql = sql_match.group(1).strip() if sql_match else ""
    reasoning = reasoning_match.group(1).strip() if reasoning_match else ""

    return sql, reasoning


def generate_query(
    params: dict[str, Any], prompt_template: str, example: dict[str, Any]
) -> dict[str, str]:
    """Generate SQL using the prompt for the given example."""
    llm_response = generate_sql(
        prompt_template,
        example["question"],
        params["model"],
        params["temperature"],
    )
    generated_sql, reasoning = extract_sql_and_reasoning(llm_response)
    return {
        "question": example["question"],
        "response": llm_response,
        "generated_query": generated_sql,
        "reasoning": reasoning,
    }


def main(
    schema_path: str = "prompts/context/db_schema_descriptive.txt",
    examples_path: str = "data/examples_queries_test.json",
    output_dir: str = "output",
) -> None:
    """
    Generate SQL queries from natural language questions using LLM

    Args:
        schema_path: Path to database schema
        examples_path: Path to test examples
        output_dir: Directory for output files
    """

    # Create output directory if it doesn't exist
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load various inputs
    params = dvc.api.params_show()["generate"]
    prompt_template = load_prompt(schema_path, params)
    examples = json.loads(Path(examples_path).read_text())

    # TODO: Use all examples; currently limiting to 5 for testing
    examples = examples[:5]

    # Generate queries
    generated_queries = []
    for example in tqdm(examples):
        generated_queries.append(generate_query(params, prompt_template, example))

    # Save for evaluation
    (output_dir / "generated_queries.json").write_text(
        json.dumps(generated_queries, indent=2)
    )


if __name__ == "__main__":
    Fire(main)
