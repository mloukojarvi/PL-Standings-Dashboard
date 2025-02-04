"""
Dash-based League Table and Statistics Visualization

This script provides functions and callbacks to generate an interactive dashboard for visualizing 
football league standings and statistics using Dash and Plotly.

Imports:
    - json: For reading the 'data.json' file.
    - pandas as pd: For data manipulation and creating league tables.
    - plotly.express as px: For generating scatter and bar plots.
    - dash.dependencies (Input, Output): For defining Dash callbacks.

Functions:
    - create_form(value): Generates an HTML string displaying images for match results.
    - create_club_label(club, badge_url): Creates an HTML label with a club's name and badge.
    - create_table_df(season): Constructs a DataFrame representing the league table.
    - create_columns_list(columns): Defines column properties for the league table.
    - create_plot_df(season): Creates a DataFrame for plotting and maps clubs to badge URLs.
    - create_cond(col, query, color, max_value=None, min_value=None): 
        Generates a conditional formatting rule for table styling.
    - create_style_conds(df): Creates conditional formatting rules based on performance metrics.
    - register_callbacks(app): Registers Dash callbacks for updating tables and plots dynamically.

Dash Callbacks:
    - update_table(selected_season): Updates the league standings table.
    - update_scatter_plot(x_axis, y_axis, selected_season): Creates a scatter plot of selected metrics.
    - update_barplot(bar_variable, selected_season): Generates a bar chart with club badges.
"""


import json
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output

data_file_path = "data.json"
with open(data_file_path, "r") as f:
    data = json.load(f)

plot_columns = ["Won", "Drawn", "Lost", "Goals For", "Goals Against", "Points"]

def create_form(value):
    """
    Generates an HTML string for displaying images representing a given form.

    Args:
        value (str): A string where each character represents a match result:
                    'W' for win, 'L' for loss, and 'D' for draw.

    Returns:
        str: An HTML string containing a flexbox-styled div with images corresponding to each match result.
    """

    style = "display: flex; justify-content: center; align-items: center;"
    form = f"<div style='{style}'>"
    width = 25
    for char in value:
        form += f"<img src='assets/{char.lower()}.png' width={width} style='margin: 2px'>"
    return form + '</div>'

def create_club_label(club, badge_url):
    """
    Generates an HTML string for displaying a club label with a badge and name.

    Args:
        club (str): The name of the club.
        badge_url (str): The URL of the club's badge image.

    Returns:
        str: An HTML string containing a flexbox-styled div with the club's badge and name.
    """

    div_style = "display: flex; justify-content: left; align-items: center"
    img_attributes = "width='30' height='30' style=margin-right: 10px"
    return f"<div style='{div_style}'><img src='{badge_url}' {img_attributes}><p>{club}</p></div>"

def create_table_df(season):
    """
    Creates a Pandas DataFrame representing a league table for a given season.

    Args:
        season (str): The season identifier used to retrieve data.

    Returns:
        pd.DataFrame: A DataFrame containing league table data with the following columns:
            - Position: The ranking position of the club.
            - Club: The club name along with its badge.
            - GP (Played): Number of games played.
            - W (Won): Number of games won.
            - D (Drawn): Number of games drawn.
            - L (Lost): Number of games lost.
            - GF (Goals For): Goals scored by the club.
            - GA (Goals Against): Goals conceded by the club.
            - GD (Goal Difference): Difference between goals scored and conceded.
            - Points: Total points accumulated.
            - Form: Recent match results represented as images.

    Notes:
        - The function extracts data for the given season from `data`.
        - It calculates the "Goal Difference" column as "Goals For" minus "Goals Against."
        - The "Form" column is converted into an HTML representation using `create_form()`.
        - The "Club" column is formatted with club labels and badges using `create_club_label()`.
        - The final table uses shorthand column names for clarity.
    """

    columns = ["badge_url", "club", "played", "won", "drawn", "lost", 
               "goals for", "goals against", "points", "form"]

    df = pd.DataFrame({
        "Position": [int(x) for x in list(data[season].keys())],
        **{k.title(): [v[k] for v in data[season].values()] for k in columns}
    })
    idx = df.columns.get_loc("Goals Against") + 1
    df.insert(idx, "Goal Difference", df["Goals For"] - df["Goals Against"])

    df["Form"] = df["Form"].apply(lambda row: create_form(row))
    df["Club"] = df.apply(lambda x: create_club_label(x.Club, x.Badge_Url), axis=1)

    df = df.drop(columns=["Badge_Url"])
    table_glossary = {"Played": "GP", "Won": "W", "Drawn": "D", 
                      "Lost": "L", "Goals For": "GF", "Goals Against": "GA", 
                      "Goal Difference": "GD"}
    df = df.rename(columns=table_glossary)

    return df

def create_columns_list(columns):
    """
    Generates a list of column definitions for a DataTable, specifying presentation types.

    Args:
        columns (list of str): A list of column names.

    Returns:
        list of dict: A list of dictionaries, where each dictionary represents a column with:
            - "name": The column name.
            - "id": The column identifier.
            - "presentation": "markdown" for specific columns ("Club" and "Form"), otherwise "input".
    """

    markdown_columns = ["Club", "Form"]
    return [
        {"name": col, "id": col, "presentation": "markdown" if col in markdown_columns else "input"}
        for col in columns
    ]

def create_plot_df(season):
    """
    Creates a Pandas DataFrame for plotting league table data and a badge mapping.

    Args:
        season (str): The season identifier used to retrieve data.

    Returns:
        tuple:
            - pd.DataFrame: A DataFrame containing league table data with the following columns:
                - Position: The ranking position of the club.
                - Club: The name of the club.
                - Played: Number of games played.
                - Won: Number of games won.
                - Drawn: Number of games drawn.
                - Lost: Number of games lost.
                - Goals For: Goals scored by the club.
                - Goals Against: Goals conceded by the club.
                - Goal Difference: Difference between goals scored and conceded.
                - Points: Total points accumulated.
            - dict: A dictionary mapping club names to their badge URLs.

    Notes:
        - The function extracts data for the given season from `data`.
        - It calculates the "Goal Difference" column as "Goals For" minus "Goals Against."
        - The "Badge_Url" column is removed from the DataFrame and stored separately in the returned dictionary.
    """
    columns = ["badge_url", "club", "played", "won", "drawn", 
               "lost", "goals for", "goals against", "points"]

    df = pd.DataFrame({
        "Position": list(data[season].keys()),
        **{k.title(): [v[k] for v in data[season].values()] for k in columns}
    })
    df["Goal Difference"] =  df["Goals For"] - df["Goals Against"]

    badges = dict(zip(df["Club"], df["Badge_Url"]))
    df = df.drop(columns=["Badge_Url"])
    
    return df, badges

def create_cond(col, query, color, max_value=None, min_value=None):
    """
    Creates a conditional formatting rule for a DataTable column.

    Args:
        col (str): The column name to apply the condition to.
        query (str): The type of query condition. Must be one of:
            - "max": Highlights the row where the column value equals `max_value`.
            - "min": Highlights the row where the column value equals `min_value`.
            - "pos": Highlights rows where the column value is greater than 0.
            - "neg": Highlights rows where the column value is less than 0.
        color (str): The background color to apply when the condition is met.
        max_value (optional, any): The maximum value used for the "max" condition.
        min_value (optional, any): The minimum value used for the "min" condition.

    Returns:
        dict: A dictionary representing the conditional formatting rule, structured as:
            {
                'if': {'filter_query': <query_condition>, 'column_id': <col>},
                'backgroundColor': <color>
            }

    Raises:
        ValueError: If `query` is "max" but `max_value` is not provided.
        ValueError: If `query` is "min" but `min_value` is not provided.
        ValueError: If an invalid query type is provided.

        if query == "max" and max_value is None:
            raise ValueError("max_values must be provided for 'max' query.")
        if query == "min" and min_value is None:
            raise ValueError("min_values must be provided for 'min' query.")
    """

    query_map = {
        "max": f"{{{col}}} = {max_value}",
        "min": f"{{{col}}} = {min_value}",
        "pos": f"{{{col}}} > 0",
        "neg": f"{{{col}}} < 0"
    }

    if query not in query_map:
        raise ValueError(f"Invalid query type: {query}. Expected one of {list(query_map.keys())}.")

    return {'if': {'filter_query': query_map[query], 'column_id': col}, 'backgroundColor': color}

def create_style_conds(df):
    """
    Generates a list of conditional formatting rules for a DataTable based on performance metrics.

    Args:
        df (pd.DataFrame): The DataFrame containing league table data.

    Returns:
        list of dict: A list of conditional formatting rules, where each rule is a dictionary specifying:
            - A condition (`filter_query`) based on column values.
            - A background color for highlighting specific data points.

    Formatting rules:
        - Columns where higher values are better ("W", "GF", "GD"):
            - Best value: Highlighted in gold (#FFD700).
            - Worst value: Highlighted in grey (#D1D1D1).
        - Columns where lower values are better ("L", "GA"):
            - Best value: Highlighted in gold (#FFD700).
            - Worst value: Highlighted in grey (#D1D1D1).
        - Goal Difference ("GD"):
            - Positive values: Highlighted in light green.
            - Negative values: Highlighted in pink.
        - Position:
            - Teams ranked 18th or lower (relegation zone): Highlighted in pink.

    Notes:
        - Uses `create_cond()` to generate formatting rules for specific conditions.
        - The function calculates column-wise max and min values to determine best/worst performers.
    """

    high_better = ["W", "GF", "GD"]
    low_better = ["L", "GA"]

    best_color = "#FFD700"
    worst_color = "#D1D1D1"

    style_conditions = []

    max_values = df.max().to_dict()
    min_values = df.min().to_dict()

    def add_style_conditions(columns, best_query, worst_query, best_color, worst_color):
        for col in columns:
            style_conditions.append(create_cond(col, best_query, best_color,
                                                max_values[col], min_values[col]))
            style_conditions.append(create_cond(col, worst_query, worst_color,
                                                max_values[col], min_values[col]))

    style_conditions.extend([
        create_cond("GD", "pos", "lightgreen"),
        create_cond("GD", "neg", "pink"),
    ])

    add_style_conditions(high_better, "max", "min", best_color, worst_color)
    add_style_conditions(low_better, "min", "max", best_color, worst_color)

    style_conditions.extend([{'if': {'filter_query': '{Position} > 17', 'column_id': 'Position'},
                               'backgroundColor': 'pink'}])

    return style_conditions

def register_callbacks(app):
    """
    Registers Dash callback functions for updating tables and visualizations dynamically.

    Args:
        app (dash.Dash): The Dash application instance.

    Callbacks:
        1. update_table(selected_season):
            - Updates the league standings table based on the selected season.
            - Outputs:
                - "standings-table" data (list of dicts).
                - "standings-table" columns (list of dicts).
                - "standings-table" style_data_conditional (list of dicts).

        2. update_scatter_plot(x_axis, y_axis, selected_season):
            - Generates a scatter plot for selected performance metrics.
            - Adds club badges as images at corresponding data points.
            - Outputs:
                - "scatter-plot" figure (plotly.graph_objects.Figure).

        3. update_barplot(bar_variable, selected_season):
            - Generates a bar plot for a selected variable (e.g., points, goals).
            - Adds club badges above bars for visual clarity.
            - Outputs:
                - "bar-plot" figure (plotly.graph_objects.Figure).

    Notes:
        - `create_table_df()` is used to generate the table's data.
        - `create_plot_df()` extracts data and badge URLs for plotting.
        - Club badges are added dynamically to both scatter and bar plots.
        - Uses `plotly.express` for visualization.
    """


    @app.callback(
        Output("standings-table", "data"),
        Output("standings-table", "columns"),
        Output("standings-table", "style_data_conditional"),
        [Input("season-dropdown", "value")]
    )
    def update_table(selected_season):
        df = create_table_df(selected_season)
        table_data = df.to_dict('records')
        columns = create_columns_list(df)
        style_conditions = create_style_conds(df)
        return table_data, columns, style_conditions

    @app.callback(
        Output('scatter-plot', 'figure'),
        [Input('x-axis', 'value'),
        Input('y-axis', 'value'),
        Input('season-dropdown', 'value')]
    )
    def update_scatter_plot(x_axis, y_axis, selected_season):
        df, badges = create_plot_df(selected_season)

        # Need to manually set ranges for plot axes to be able 
        # to change to paper-relative coordinates later
        range_x = [int(0.9*df[x_axis].min()), int(1.1*df[x_axis].max())]
        range_y = [int(0.9*df[y_axis].min()), int(1.1*df[y_axis].max())]

        fig = px.scatter(
            df, x=x_axis, y=y_axis,
            range_x = range_x, range_y = range_y,
            title=f'Scatter Plot of <b>{x_axis}</b> vs <b>{y_axis}</b>', 
            height=600,
            )
        
        fig.update_traces(
            marker=dict(opacity=0),
            hoverinfo="none",
            hovertemplate=f"<b>%{{customdata}}</b><br>{x_axis}: %{{x}}<br>{y_axis}: %{{y}}<extra></extra>",
            customdata=df["Club"]
            )

        x_range = fig.layout.xaxis.range  
        y_range = fig.layout.yaxis.range

        # Function to convert data coordinates to paper-relative coordinates
        def to_paper_coords(x_data, y_data, x_range, y_range):
            x_paper = (x_data - x_range[0]) / (x_range[1] - x_range[0])
            y_paper = (y_data - y_range[0]) / (y_range[1] - y_range[0])
            return x_paper, y_paper

        for club, x, y in zip(df["Club"], df[x_axis], df[y_axis]):
            x, y = to_paper_coords(x, y, x_range, y_range)
            fig.add_layout_image(
                dict(
                    source=badges[club],
                    x=x, y=y,
                    xref="paper", yref="paper",
                    sizex=0.1, sizey=0.1,
                    xanchor="center", yanchor="middle",
                    layer="above"
                )
            )

        return fig

    @app.callback(
        Output('bar-plot', 'figure'),
        [Input('bar-variable', 'value'),
        Input('season-dropdown', 'value')]
    )
    def update_barplot(bar_variable, selected_season):
        df, badges = create_plot_df(selected_season)
        fig = px.bar(
            df, x="Club", y=bar_variable,
            title=f'Bar Plot of <b>{bar_variable}</b>',
            height=600
            )

        x_positions = df["Club"] # Stays constant
        y_positions = df[bar_variable]

        max_y = y_positions.max()
        fig.update_layout(yaxis=dict(range=[0, max_y * 1.2]))  # Adds 20% extra space above
        badge_size = max_y*0.1

        for club, x, y in zip(df["Club"], x_positions, y_positions):
            fig.add_layout_image(
                dict(
                    source=badges[club],
                    x=x,
                    y=y + max_y*0.01,  # Slightly above the bar
                    xref="x", yref="y",
                    sizex=badge_size, sizey=badge_size,
                    xanchor="center", yanchor="bottom",
                    layer="above"
                )
            )

        return fig