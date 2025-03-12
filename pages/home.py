import dash
from dash import html

dash.register_page(__name__, path="/")

layout = html.Div(
    [
        html.H1(
            "Golf Performance Analysis Dashboard",
            style={"text-align": "center", "margin-top": "20px"},
        ),
        html.Div(
            [
                html.P(
                    "Welcome to the Golf Performance Analysis Dashboard! Dive deep into your golf swing data with our comprehensive and interactive tools."
                ),
                html.P(
                    "Upload your Trackman data to visualize key metrics, identify trends, and gain valuable insights into your performance."
                ),
                html.P(
                    "Our dashboard offers interactive plots and tables to compare different swings, clubs, and conditions. Whether you're a coach or a player, our tools will help you make data-driven decisions to enhance your game. Start exploring your data today and take your golf performance to the next level!"
                ),
            ],
            style={
                "max-width": "800px",
                "margin": "auto",
                "padding": "20px",
                "line-height": "1.6",
                "font-size": "18px",
                "text-align": "justify",
                "background-color": "#f9f9f9",
                "border-radius": "10px",
                "box-shadow": "0 4px 8px rgba(0, 0, 0, 0.1)",
            },
        ),
    ]
)
