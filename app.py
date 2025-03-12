import base64
import io
import logging
import re
import csv

import pandas as pd
from dash import Dash, Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate
import dash

from utils.logger import get_child_logger, set_parent_log_level

logger = get_child_logger(__name__)

app = Dash(use_pages=True, external_stylesheets=["/assets/styles.css"])

app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        dcc.Store(id="data", storage_type="session"),
        html.Div(id="error"),
        dcc.Upload(
            id="upload-data",
            children=html.Div(["Drag and Drop or ", html.A("Select File")]),
            style={
                "height": "60px",
                "lineHeight": "60px",
                "borderWidth": "1px",
                "borderStyle": "dashed",
                "borderRadius": "5px",
                "textAlign": "center",
                "margin": "10px",
            },
            multiple=False,
        ),
        html.Ul(id="tabs", className="tabs"),
        dash.page_container,
    ]
)


@app.callback(
    Output("tabs", "children"),
    Input("url", "pathname"),
)
def update_active_tab(pathname):
    return [
        html.Li(
            dcc.Link(
                f"{page['name']}",
                href=page["relative_path"],
                className="active" if page["relative_path"] == pathname else "",
            ),
            className="tab",
        )
        for page in dash.page_registry.values()
    ]


@app.callback(
    Output("error", "children"),
    Output("data", "data"),
    Output("upload-data", "children"),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
)
def update_data(content: str | None, name: str | None):
    if content is None:
        raise PreventUpdate
    content_string = content.split(",")[1]
    decoded = base64.b64decode(content_string).decode("utf-8")
    try:
        if name.endswith(".csv"):
            logger.debug("Reading csv")
            if match := re.match(r"sep=(.)", decoded.splitlines()[0]):
                # This is a csv exported directly from trackman
                sep = match.group(1)
                logger.debug("Reading trackman csv with sep %s", sep)
                df = pd.read_csv(
                    io.StringIO(decoded),
                    sep=sep,
                    skiprows=1,
                    quotechar='"',
                    quoting=csv.QUOTE_ALL,
                    header=[0, 1],
                )
                logger.debug("original columns:")
                logger.debug(df.columns)
                # Combine headers and units, ignoring empty units
                df.columns = [
                    f"{col[0]} {col[1]}" if "Unnamed" not in col[1] else col[0]
                    for col in df.columns.values
                ]
                logger.debug("new columns:")
                logger.debug(df.columns)
            else:
                # Assume the csv is normal with no sep row to start and no units row
                logger.debug("Reading normal csv")
                df = pd.read_csv(io.StringIO(decoded))
        else:
            logger.debug("Uploaded file is not a csv. File name: %s", name)
            return (
                html.Div(["Please upload a csv"]),
                None,
                html.Div(["Drag and Drop or ", html.A("Select File")]),
            )
    except Exception as e:
        logger.error("Failed to read file")
        logger.exception(e)
        return (
            html.Div(["There was an error processing this file."]),
            None,
            html.Div(["Drag and Drop or ", html.A("Select File")]),
        )
    logger.debug(df)
    return (
        None,
        df.to_dict("records"),
        html.Div(
            [
                f"{name} has been uploaded. Drag and Drop or ",
                html.A("Select File"),
                " to replace the current file",
            ]
        ),
    )


if __name__ == "__main__":
    set_parent_log_level(logging.DEBUG)
    app.run(debug=True)
