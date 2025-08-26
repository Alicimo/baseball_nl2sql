import json
import os
import re
import time
import traceback
from pathlib import Path

import dvc.api
import openai
from dotenv import load_dotenv
from fire import Fire
from tqdm import tqdm

# Compile regex patterns once for efficiency
SQL_PATTERN = re.compile(r"<sql>(.*?)</sql>", re.DOTALL)
REASONING_PATTERN = re.compile(r"<reasoning>(.*?)</reasoning>", re.DOTALL)


class LLM:
    def __init__(
        self,
        model_name: str,
        client_url: str,
        client_key: str,
        retries: int = 1,
        temperature: float = 1.0,
        max_tokens: int = 300,
    ):
        self.client = openai.OpenAI(base_url=client_url, api_key=client_key)
        self.model_name = model_name
        self.retries = retries
        self.temperature = temperature
        self.max_tokens = max_tokens

    def complete(self, prompt: str) -> str:
        for _ in range(self.retries):
            try:
                completion = self.client.completions.create(
                    model=self.model_name,
                    prompt=prompt,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                )
                return completion.choices[0].text, completion.usage.to_dict()
            except Exception:
                traceback.print_exc()
                time.sleep(10)
        raise Exception("LLM not working")


class SQLGenerator:
    def __init__(self, llm: LLM, prompt_template: str) -> tuple[str, str]:
        self.llm = llm
        self.prompt_template = prompt_template

    def generate(
        self,
        user_question: str,
    ) -> dict[str]:
        """Generate SQL query from user input"""
        filled_prompt = (
            self.prompt_template.replace("{{user_question}}", user_question),
        )
        response, usage = self.llm.complete(filled_prompt)
        sql, reasoning = self._parse_response(response)
        return usage | {
            "question": user_question,
            "response": response,
            "generated_query": sql,
            "reasoning": reasoning,
        }

    def _parse_response(self, response: str) -> tuple[str, str]:
        """Extract SQL and reasoning from LLM response using regex"""
        sql_match = SQL_PATTERN.search(response)
        reasoning_match = REASONING_PATTERN.search(response)

        sql = sql_match.group(1).strip() if sql_match else ""
        reasoning = reasoning_match.group(1).strip() if reasoning_match else ""

        return sql, reasoning


def load_prompt(
    prompt_path: str,
    schema_path: str,
) -> str:
    """Load prompt and insert context (e.g., schema)."""
    schema = Path(schema_path).read_text()
    prompt_template = Path(prompt_path).read_text()
    prompt_template = prompt_template.replace("{{schema}}", schema)
    return prompt_template


def main(
    examples_path: str = "data/examples_queries_test.json",
    output_dir: str = "output",
) -> None:
    """
    Generate SQL queries from natural language questions using LLM

    Args:
        examples_path: Path to test examples
        output_dir: Directory for output files
    """

    # Create output directory if it doesn't exist
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load parameters and configuration
    load_dotenv()
    params = dvc.api.params_show()["generate"]
    prompt_template = load_prompt(
        params["prompt"]["prompt_path"], params["prompt"]["schema_path"]
    )
    examples = json.loads(Path(examples_path).read_text())

    # TODO: Use all examples; currently limiting to 5 for testing
    examples = examples[:5]

    # Initialize LLM client and SQL generator
    llm = LLM(
        model_name=params["llm"]["model"],
        client_url=os.getenv("OPENAI_URL"),
        client_key=os.getenv("OPENAI_KEY"),
        temperature=params["llm"]["temperature"],
        max_tokens=params["llm"]["max_tokens"],
    )

    sql_generator = SQLGenerator(llm=llm, prompt_template=prompt_template)

    # Generate queries using class-based components
    generated_queries = [
        sql_generator.generate(example["question"]) for example in tqdm(examples)
    ]

    # Save results
    (output_dir / "generated_queries.json").write_text(
        json.dumps(generated_queries, indent=2)
    )


if __name__ == "__main__":
    Fire(main)
