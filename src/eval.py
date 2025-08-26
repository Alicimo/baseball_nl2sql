import json
from collections import Counter
from math import sqrt
from pathlib import Path
from typing import Any

from fire import Fire
from sqlglot import Expression, diff, parse_one, tokenize
from sqlglot.optimizer.normalize import normalize
from tqdm import tqdm


def normalize_sql(sql: str) -> str:
    """Normalize SQL, e.g., strip aliases."""
    tree = parse_one(sql)
    tree = normalize(tree)  # Normalize column references to remove alias impact
    return tree.sql()


def count_nodes(ast: Expression) -> int:
    """Count the number of nodes in an ast."""
    return len(list(ast.walk()))


def ast_distance(sql_1: str, sql_2: str) -> float:
    """Calculate the distance between two sql strings as the edit distance.

    Change Distiller algorithm, created by Fluri et al

    The algorithm consists of two high-level steps:
      1. Finding appropriate matchings between pairs of nodes that are part of compared ASTs.
      2. Generating the so-called “edit script” from the matching set built in the 1st step.
    """
    sql_1_ast = parse_one(sql_1)
    sql_2_ast = parse_one(sql_2)
    edits = diff(sql_1_ast, sql_2_ast, delta_only=True)
    total_nodes = count_nodes(sql_1_ast) + count_nodes(sql_2_ast)
    return len(edits) / total_nodes if total_nodes > 0 else 0


def tokenize_sql(sql: str) -> Counter[str]:
    """Tokenizes SQL query and return unique tokens and their counts"""
    parsed = tokenize(sql)
    tokens = Counter()
    for token in parsed:
        tokens[token.text.lower()] += 1
    return tokens


def cosine_similarity(sql_1: str, sql_2: str) -> float:
    """Computes Cosine Similarity between two SQL strings."""
    tokens_1 = tokenize_sql(sql_1)
    tokens_2 = tokenize_sql(sql_2)

    if len(tokens_1) == 0 or len(tokens_2) == 0:
        return 0.0

    intersection = set(tokens_1) & set(tokens_2)
    dot_product = sum(tokens_1[token] * tokens_2[token] for token in intersection)
    magnitude1 = sqrt(sum(tokens_1[token] ** 2 for token in tokens_1))
    magnitude2 = sqrt(sum(tokens_2[token] ** 2 for token in tokens_2))

    return dot_product / (magnitude1 * magnitude2)


def evaluate_query(gen_query: str, ref_example: str) -> dict[str, Any]:
    """Evaluate a single query against a reference example."""
    if gen_query["question"] != ref_example["question"]:
        raise ValueError("Questions don't match")

    # Handle edge case of no query returned
    if not gen_query["generated_query"]:
        return {
            "question": gen_query["question"],
            "generated_query": gen_query["generated_query"],
            "reference_query": ref_example["query"],
            "ast_distance": 1,
            "token_cosine": 0,
        }

    gen_normed = normalize_sql(gen_query["generated_query"])
    ref_normed = normalize_sql(ref_example["query"])

    return {
        "question": gen_query["question"],
        "generated_query": gen_query["generated_query"],
        "reference_query": ref_example["query"],
        "ast_distance": ast_distance(gen_normed, ref_normed),
        "token_cosine": cosine_similarity(gen_normed, ref_normed),
    }


def main(
    generated_queries_path: str,
    reference_examples_path: str,
    output_dir: str = "output",
) -> None:
    """
    Evaluate generated SQL queries against reference queries

    Args:
        generated_queries_path: Path to generated queries JSON file
        reference_examples_path: Path to reference examples JSON file
        output_dir: Directory for output files
    """
    # Create output directory if it doesn't exist
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load data
    generated_queries = json.loads(Path(generated_queries_path).read_text())
    reference_examples = json.loads(Path(reference_examples_path).read_text())

    # Match and evaluate each query
    results = []
    for gen_query, ref_example in tqdm(zip(generated_queries, reference_examples)):
        results.append(evaluate_query(gen_query, ref_example))

    # Save full evaluation results
    (output_dir / "eval.json").write_text(json.dumps(results, indent=2))

    # Save tracked metric(s)
    metrics = {
        "ast_distance_mean": sum([result["ast_distance"] for result in results])
        / len(results),
        "token_cosine_mean": sum([result["token_cosine"] for result in results])
        / len(results),
    }
    (output_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    Fire(main)
