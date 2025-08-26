import re
from pathlib import Path

import pandas as pd
from fuzzywuzzy import fuzz


def parse_exact_schema(schema_file):
    """Parses the exact schema file and extracts table and column information.

    Args:
        schema_file (str): Path to the exact schema file.

    Returns:
        dict: A dictionary where keys are table names and values are lists of tuples,
              where each tuple contains (column_name, column_type).
    """
    table_schemas = {}
    current_table = None

    with open(schema_file, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("CREATE TABLE"):
                # Extract table name
                match = re.search(r"CREATE TABLE (\w+)", line)
                if match:
                    current_table = match.group(1)
                    table_schemas[current_table] = []
            elif current_table and line.startswith("player_id"):
                parts = line.split(" ")
                col_name = parts[0]
                col_type = parts[1]
                table_schemas[current_table].append((col_name, col_type))
            elif current_table and line and not line.startswith("."):
                # Extract column name and type
                parts = line.split(" ")
                col_name = parts[0]
                col_type = parts[-1]  # Last word is usually the type
                col_type = col_type.replace(",", "")  # to remove trailing comma
                table_schemas[current_table].append((col_name, col_type))
    return table_schemas


def parse_descriptive_schema(description_file):
    """Parses the descriptive schema file and extracts column descriptions.

    Args:
        description_file (str): Path to the descriptive schema file.

    Returns:
        dict: A dictionary where keys are table names and values are dictionaries.
              Each inner dictionary maps column names to their descriptions.
    """
    table_descriptions = {}
    current_table = None
    with open(description_file, "r") as f:
        content = f.read()

    # Splitting the content by table name
    table_blocks = re.split(r"(\w+)\s+table", content, flags=re.IGNORECASE)

    # Processing each table block
    for i in range(1, len(table_blocks), 2):
        table_name = table_blocks[i].strip()
        table_content = table_blocks[i + 1].strip()

        # Extracting column descriptions using regex
        column_descriptions = {}
        column_entries = re.findall(r"(\w+)\s{2,}(.+)", table_content)
        for entry in column_entries:
            column_name = entry[0].strip()
            description = entry[1].strip()
            column_descriptions[column_name] = description

        table_descriptions[table_name.lower()] = column_descriptions

    return table_descriptions


def fuzzy_match(name, choices, threshold=80):
    """
    Finds the best fuzzy match for a name from a list of choices.

    Args:
        name (str): The name to match.
        choices (list): A list of possible matches.
        threshold (int): Minimum fuzzy match score to consider.

    Returns:
        str: The best matched choice, or None if no good match is found.
    """
    best_match = None
    best_score = 0
    for choice in choices:
        score = fuzz.ratio(
            name.lower(), choice.lower()
        )  # Convert to lowercase for case-insensitive matching
        if score > best_score and score >= threshold:
            best_score = score
            best_match = choice
    return best_match


def combine_schemas(exact_schema, descriptive_schema):
    """Combines the exact and descriptive schemas into a single Pandas DataFrame,
    using fuzzy matching to link table and column names.

    Args:
        exact_schema (dict): Output from parse_exact_schema.
        descriptive_schema (dict): Output from parse_descriptive_schema.

    Returns:
        pandas.DataFrame: A DataFrame containing the combined schema information.
    """
    data = []
    for table_name, columns in exact_schema.items():
        # Fuzzy match table name
        matched_table = fuzzy_match(table_name, list(descriptive_schema.keys()))
        if not matched_table:
            print(f"No matching description found for table: {table_name}")
            continue

        for col_name, col_type in columns:
            # Fuzzy match column name
            matched_col = fuzzy_match(
                col_name, list(descriptive_schema[matched_table].keys())
            )
            if matched_col:
                description = descriptive_schema[matched_table][matched_col]
            else:
                description = "No description found"
                print(
                    f"No matching description found for column: {col_name} in table: {table_name}"
                )

            data.append(
                {
                    "Table": table_name,
                    "Col_Name": col_name,
                    "Col_Type": col_type,
                    "Description": description,
                }
            )
    return pd.DataFrame(data)


# Main execution
if __name__ == "__main__":
    content_dir = Path("prompts/context")
    exact_schema_file = content_dir / "db_schema_exact.txt"
    descriptive_schema_file = content_dir / "db_schema_descriptive.txt"

    exact_schema = parse_exact_schema(exact_schema_file)
    descriptive_schema = parse_descriptive_schema(descriptive_schema_file)
    combined_df = combine_schemas(exact_schema, descriptive_schema)

    print(combined_df.to_string())  # Display the dataframe as a string
    combined_df.to_csv("combined_schema.csv", index=False)
