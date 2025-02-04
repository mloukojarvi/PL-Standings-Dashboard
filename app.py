"""
Premier League Standings Dashboard

This script initializes and runs a Dash web application that visualizes Premier League standings 
and statistics using interactive tables and plots.

Imports:
    - Dash, html, dash_table, dcc: Components for building the Dash web application.
    - plotly.io as pio: Sets default plot style.
    - json: Handles reading and parsing league data.
    - fetch_data: Fetches and processes league data.
    - callbacks.register_callbacks: Registers callback functions for interactive updates.

Workflow:
    1. Fetch and load league standings from `data.json`.
    2. Initialize a Dash application with:
        - A dropdown to select a season.
        - A table displaying league standings with conditional formatting.
        - A bar chart for comparing team statistics.
        - A scatter plot for visualizing correlations between statistics.
    3. Register callbacks to update the UI based on user interactions.
    4. Run the app in debug mode.

Layout:
    - **Season Selection**: Dropdown for choosing the Premier League season.
    - **Standings Table**: Displays teams' positions, points, and performance with visual indicators.
    - **Bar Chart**: Shows a selected statistical category for all teams.
    - **Scatter Plot**: Plots any two statistical variables against each other.

Usage:
    Run this script to start the web application. The app will be available in a browser at `http://127.0.0.1:8050/`.
"""


from dash import Dash, html, dash_table, dcc
import plotly.io as pio
import json
import fetch_data
from callbacks import register_callbacks
import os.path

# Prevents the program from continuously fetching data
data_file_path = "data.json"
if not os.path.exists(data_file_path):
    fetch_data.main()

with open(data_file_path, "r") as f:
    data = json.load(f)

seasons = list(data.keys())

### Styling for divs and plots ###
plot_columns = ["Won", "Drawn", "Lost", "Goals For", "Goals Against", "Points"]
table_glossary = {"Played": "GP", "Won": "W", "Drawn": "D", "Lost": "L", "Goals For": "GF",
                  "Goals Against": "GA", "Goal Difference": "GD"}

pio.templates.default = "plotly_white"

main_style = {
    "padding": "10px",
    "width": "1000px",
    "margin": "0 auto",
    "font-family": "Helvetica",
}

selection_style = {
    "display": "flex",
    "align-items": "center"
}

section_style = {
    "border": "1px solid black", 
    "padding": "20px",
    "border-radius": "15px",
    "margin-bottom": "20px"
}
### End of styling ###E

app = Dash(__name__, suppress_callback_exceptions=True)

app.layout = html.Div(children=[
    html.Div(children=[
        html.Div(
            children=[
                html.Img(
                    src="assets/main-logo.png", 
                    style={"height": "75px", "margin-right": "20px"}
                ),
                html.H1(
                    id="title",
                    children="Premier League Standings for Season:",
                    style={"margin": "0"}
                )
            ],
            style={
                "display": "flex", 
                "align-items": "center",
                "margin-bottom": "20px"
            }
        ),
        dcc.Dropdown(
            id="season-dropdown",
            options=[{"label": season, "value": season} for season in seasons],
            value=seasons[0],
            style={"width": "200px", "margin-left": "10px", "margin-top": "-10px"}
        ),
    ], style=selection_style),

    html.Div(id="main-content", children=[
        # Standings Table Section
        html.Div([
            dash_table.DataTable(
                id="standings-table",
                columns=[],
                markdown_options={"html": True},
                data=[],
                style_cell={'textAlign': 'center', 'justify-content': 'center', "font-family": "Helvetica"},
                style_data_conditional=[],
                sort_action="native"
            ),

            html.Div(children=[
                    dcc.Markdown(f"**GLOSSARY**: {', '.join([f'**{x[1]}**: {x[0]}' for x in table_glossary.items()])}"),
                    dcc.Markdown(
                        """
                        **EXPLANATION:** The best value in columns *W*, *L*, *GF*, *GA*, and *GD* is highlighted in gold, 
                        and the worst value in gray. In the column *GD* positive values are highlighted in green and
                        negative values in red. In the column *Position* clubs highlighted in red were demoted or are
                        currently at the risk of being demoted if the ongoing season is selected.
                        """
                    ),
                ], style={"margin-top": "20px", "font-size": "12px", "color": "gray"})

        ], style=section_style),

        # Bar Plot Section
        html.Div(children=[
            dcc.Graph(id="bar-plot"),

            html.Div(children=[
                html.P("y-axis:"),
                dcc.Dropdown(
                    id='bar-variable',
                    options=[{'label': col, 'value': col} for col in plot_columns],
                    value='Points',
                    style={"width": "200px", "margin-left": "10px"}
                ),
            ], style=selection_style)

        ], style=section_style),

        # Scatter Plot Section
        html.Div(children=[
            dcc.Graph(id="scatter-plot"),

            html.Div(children=[
                html.P("x-axis:"),
                dcc.Dropdown(
                    id='x-axis',
                    options=[{'label': col, 'value': col} for col in plot_columns],
                    value='Goals For',
                    style={"width": "200px", "margin-left": "10px"}
                ),
            ], style=selection_style),
            
            html.Div(children=[
                html.P("y-axis:"),
                dcc.Dropdown(
                    id='y-axis',
                    options=[{'label': col, 'value': col} for col in plot_columns],
                    value='Goals Against',
                    style={"width": "200px", "margin-left": "10px"}
                ),
            ], style=selection_style)

        ], style=section_style)

    ],)
], style = main_style)

register_callbacks(app)

if __name__ == "__main__":
    app.run_server(
        debug=False,
        host="0.0.0.0",
        port=8050,
        dev_tools_ui=False,
        dev_tools_props_check=False,
        dev_tools_hot_reload=False
    )

