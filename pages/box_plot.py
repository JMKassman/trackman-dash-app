import math
import dash
from dash import html, dcc, callback, Input, Output, State, ALL
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.express as px
import numpy as np
from statsmodels.formula.api import ols


dash.register_page(__name__)

layout = [
    html.H1("Box Plot"),
    html.Label("Select Column for Box Plot:", htmlFor="box-column-selector"),
    dcc.Dropdown(id="box-column-selector"),
    html.Label("Choose Grouping (optional):", htmlFor="box-color-selector"),
    dcc.Dropdown(id="box-color-selector"),
    html.Label("Choose Filter Column (optional):", htmlFor="box-filter-selector"),
    dcc.Dropdown(id="box-filter-selector"),
    html.Div(id="box-filter"),
    dcc.Graph(id="box-plot"),
    html.Button(id="ols-button", children="Run OLS"),
    html.Div(id="ols-results"),
]


@callback(
    Output("box-column-selector", "options"),
    Output("box-color-selector", "options"),
    Output("box-filter-selector", "options"),
    Input("data", "data"),
)
def load_columns_into_dropdowns(data):
    if data is None:
        return ["Upload data first"], ["Upload data first"], ["Upload data first"]
    df = pd.DataFrame(data)
    columns = sorted(df.columns)
    return columns, columns, columns


@callback(
    Output("box-filter", "children"),
    Input("box-filter-selector", "value"),
    Input("data", "data"),
)
def load_filter_options(filter_col, data):
    if filter_col is None:
        return None
    col = pd.DataFrame(data)[filter_col]
    dtype = str(col.dtype)
    if dtype == "object":
        return dcc.Checklist(
            list(set(col)), list(set(col)), id={"type": "box-filter", "index": "check"}
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
            id={"type": "box-filter", "index": "range"},
        )


@callback(
    Output("box-plot", "figure"),
    Input("data", "data"),
    Input("box-column-selector", "value"),
    Input("box-color-selector", "value"),
    Input("box-filter-selector", "value"),
    Input({"type": "box-filter", "index": ALL}, "value"),
    State({"type": "box-filter", "index": ALL}, "id"),
)
def create_graph(
    data,
    data_col,
    color_col,
    filter_col,
    filter_values,
    filter_type,
):
    if data is None or data_col is None:
        raise PreventUpdate
    df = pd.DataFrame(data)
    match filter_type:
        case [{"index": "check"}]:
            df = df[df[filter_col].isin(filter_values[0])]
        case [{"index": "range"}]:
            df = df[df[filter_col].between(*filter_values[0])]
    if color_col is not None:
        return px.box(df.sort_values(color_col), x=data_col, color=color_col)
    else:
        return px.box(df, x=data_col)


@callback(
    Output("ols-results", "children"),
    Input("ols-button", "n_clicks"),
    State("data", "data"),
    State("box-column-selector", "value"),
    State("box-color-selector", "value"),
    State("box-filter-selector", "value"),
    State({"type": "box-filter", "index": ALL}, "value"),
    State({"type": "box-filter", "index": ALL}, "id"),
)
def run_ols(
    n_clicks, data, data_col, grouping_col, filter_col, filter_values, filter_type
):
    if data is None:
        raise PreventUpdate
    if data_col is None:
        return html.P("Select a data column first")
    if grouping_col is None:
        return html.P("Grouping column must be selected and must be categorical")
    df = pd.DataFrame(data)
    match filter_type:
        case [{"index": "check"}]:
            df = df[df[filter_col].isin(filter_values[0])]
        case [{"index": "range"}]:
            df = df[df[filter_col].between(*filter_values[0])]
    if len(df[grouping_col].drop_duplicates()) < 2:
        return html.P("Grouping column must have at least 2 values")
    model = ols(f"{data_col} ~ {grouping_col}", df).fit()
    return html.Pre(
        children=model.summary().as_text(),
        style={
            "whiteSpace": "pre-wrap",
            "background-color": "lightgray",
            "display": "inline-block",
            "padding": "1em",
        },
    )
