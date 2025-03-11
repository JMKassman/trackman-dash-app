import dash
from dash import html, callback, Input, Output, dash_table
import pandas as pd


dash.register_page(__name__)

layout = [html.H1("Data Table"), html.Div(id="data-table")]


@callback(Output("data-table", "children"), Input("data", "data"))
def display_data_table(data):
    if data is not None:
        df = pd.DataFrame(data)
        return (
            dash_table.DataTable(
                df.to_dict("records"), [{"name": i, "id": i} for i in df.columns]
            ),
        )
    else:
        return html.P("Upload data first")
