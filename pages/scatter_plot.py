import math
import dash
from dash import html, dcc, callback, Input, Output, State, ALL
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.express as px
import numpy as np

from utils.logger import get_child_logger

logger = get_child_logger(__name__)

dash.register_page(__name__)

layout = html.Div(
    [
        html.H1("Scatter Plot", className="page-title"),
        html.Div(
            [
                html.Label(
                    "Select Column for X Axis:", htmlFor="scatter-x-column-selector"
                ),
                dcc.Dropdown(id="scatter-x-column-selector"),
                html.Label(
                    "Select Column for Y Axis:", htmlFor="scatter-y-column-selector"
                ),
                dcc.Dropdown(id="scatter-y-column-selector"),
                html.Label(
                    "Choose Grouping (optional):", htmlFor="scatter-color-selector"
                ),
                dcc.Dropdown(id="scatter-color-selector"),
                html.Label(
                    "Choose Filter Column (optional):",
                    htmlFor="scatter-filter-selector",
                ),
                dcc.Dropdown(id="scatter-filter-selector"),
                html.Div(id="scatter-filter"),
                dcc.Graph(id="scatter-plot"),
                html.Div(id="trendline-stats", className="ols-results"),
            ],
            className="scatter-plot-container",
        ),
    ],
    className="page-content",
)


@callback(
    Output("scatter-x-column-selector", "options"),
    Output("scatter-y-column-selector", "options"),
    Output("scatter-color-selector", "options"),
    Output("scatter-filter-selector", "options"),
    Input("data", "data"),
)
def load_columns_into_dropdowns(data):
    if data is None:
        return (
            ["Upload data first"],
            ["Upload data first"],
            ["Upload data first"],
            ["Upload data first"],
        )
    df = pd.DataFrame(data)
    columns = sorted(df.columns)
    return columns, columns, columns, columns


@callback(
    Output("scatter-filter", "children"),
    Input("scatter-filter-selector", "value"),
    Input("data", "data"),
)
def load_filter_options(filter_col, data):
    if filter_col is None:
        return None
    col = pd.DataFrame(data)[filter_col]
    dtype = str(col.dtype)
    if dtype == "object":
        return dcc.Checklist(
            list(set(col)),
            list(set(col)),
            id={"type": "scatter-filter", "index": "check"},
        )
    else:
        min = float(np.min(col))
        max = float(np.max(col))
        range = max - min
        if range == 0:
            step = 1
        else:
            step = 10 ** round(math.log10(abs(range / 100)))
        return dcc.RangeSlider(
            min - step,
            max + step,
            step,
            marks={min: str(min), max: str(max)},
            value=[min, max],
            tooltip={"placement": "bottom", "always_visible": False},
            id={"type": "scatter-filter", "index": "range"},
        )


@callback(
    Output("scatter-plot", "figure"),
    Output("trendline-stats", "children"),
    Input("data", "data"),
    Input("scatter-x-column-selector", "value"),
    Input("scatter-y-column-selector", "value"),
    Input("scatter-color-selector", "value"),
    Input("scatter-filter-selector", "value"),
    Input({"type": "scatter-filter", "index": ALL}, "value"),
    State({"type": "scatter-filter", "index": ALL}, "id"),
)
def create_graph(
    data,
    x_col,
    y_col,
    color_col,
    filter_col,
    filter_values,
    filter_type,
):
    if data is None or x_col is None or y_col is None:
        raise PreventUpdate
    df = pd.DataFrame(data)
    match filter_type:
        case [{"index": "check"}]:
            df = df[df[filter_col].isin(filter_values[0])]
        case [{"index": "range"}]:
            df = df[df[filter_col].between(*filter_values[0])]
    if color_col is not None:
        fig = px.scatter(
            df.sort_values(color_col),
            x=x_col,
            y=y_col,
            color=color_col,
            trendline="ols",
        )
    else:
        fig = px.scatter(df, x=x_col, y=y_col, trendline="ols")
    results: pd.DataFrame = px.get_trendline_results(fig)
    logger.debug(results)
    if results is not None and len(results.columns) > 1:
        results = results.set_index(list(set(results.columns) - {"px_fit_results"}))
    elif results is not None:
        results.index = ["ALL"]
    else:
        # ols failed most likely due to lack of data
        return fig, [html.H2("Trendline statistics"), html.H3("No trendline data")]
    summaries = []
    for index, result in results.px_fit_results.items():
        summaries.append(html.H3(index))
        summaries.append(
            html.Pre(
                children=result.summary().as_text(),
                className="pre-styling",
            )
        )
    return fig, [html.H2("Trendline statistics"), *summaries]
