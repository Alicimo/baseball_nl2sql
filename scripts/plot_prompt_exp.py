import dvc.api
import plotly.express as px
import polars as pl


def extract_experiment_data(data: list[dict]) -> pl.DataFrame:
    experiments = []
    for exp in data:
        experiments.append(
            {
                "prompt": exp["generate.prompt"],
                "ast_distance": exp["ast_distance_mean"],
                "token_cosine": exp["token_cosine_mean"],
            }
        )
    return pl.DataFrame(experiments).drop_nulls().unique()


def plot_metrics(df: pl.DataFrame):
    df_melted = df.melt(
        id_vars="prompt",
        value_vars=["ast_distance", "token_cosine"],
        variable_name="Metric",
        value_name="Value",
    )

    fig = px.bar(
        df_melted,
        x="prompt",
        y="Value",
        color="Metric",
        barmode="group",
        title="DVC Experiment Metrics",
    )
    fig.update_layout(
        xaxis_title="Generate Prompt", yaxis_title="Metric Values", xaxis_tickangle=-45
    )
    fig.show()


def main():
    data = dvc.api.exp_show()
    df = extract_experiment_data(data)
    if not df.is_empty():
        plot_metrics(df)
    else:
        print("No valid experiments found.")


if __name__ == "__main__":
    main()
