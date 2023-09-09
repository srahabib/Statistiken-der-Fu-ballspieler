import dash
from dash import dcc, html, Input, Output, dash_table
from dash.dash_table.Format import Group
import dash_table
import pandas as pd
from dash import Dash, dash_table
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import random
from dash.dependencies import Input, Output, State


# Read the example DataFrame
df = pd.read_csv('example_df.csv')

# Create a new DataFrame with hyperlinks
df_with_hyperlinks = df.copy()
df_with_hyperlinks['player_id_link'] = df_with_hyperlinks['player_id'].apply(
    lambda x: f"[Details](https://example.com/player/Details?player_id={x})")

# Initialize the Dash app
app = Dash(__name__)

# Define the app layout
app.layout = html.Div([
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='season-dropdown',
                options=[{'label': season, 'value': season} for season in df_with_hyperlinks['season'].unique()],
                value=None,
                multi=True,
                placeholder='Select Season'
            )
        ], style={'width': '48%', 'display': 'inline-block' , 'margin-right': '20px' , 'margin-bottom': '5px'}),
        html.Div([
            dcc.Dropdown(
                id='league-dropdown',
                options=[{'label': league, 'value': league} for league in df_with_hyperlinks['league'].unique()],
                value=None,
                multi=True,
                placeholder='Select League'
            )
        ], style={'width': '48%', 'display': 'inline-block', 'margin-left': '7px', 'margin-bottom': '5px'}),
        html.Div([
            dcc.Dropdown(
                id='team-dropdown',
                options=[],
                multi=True,
                value=None,
                placeholder='Select Team'
            )
        ], style={'width': '48%', 'display': 'inline-block', 'margin-right': '20px'}),
        html.Div([
            dcc.Dropdown(
                id='position-dropdown',
                options=[{'label': pos, 'value': pos} for pos in df_with_hyperlinks['position'].unique()],
                multi=True,
                value=None,
                placeholder='Select Position'
            )
        ], style={'width': '48%', 'display': 'inline-block', 'margin-left': '7px'}),
        dash_table.DataTable(
            id='data-table',
            data=df_with_hyperlinks.head(14).to_dict('records'),
            columns=[
                {"name": "Details", "id": "player_id_link", "presentation": "markdown"},
                {"name": "First Name", "id": "first_name"},
                {"name": "Last Name", "id": "last_name"},
                {"name": "Season", "id": "season"},
                {"name": "League", "id": "league"},
                {"name": "Team", "id": "team"},
                {"name": "Position", "id": "position"},
            ],
            style_table={'width': '100%'},
            style_cell={'textAlign': 'left'},
            style_header={'backgroundColor': '#005ca8', 'color': '#FFFFFF', 'fontWeight': 'bold'},
            style_data={'whiteSpace': 'normal', 'height': 'auto'},
            style_data_conditional=[
                {'if': {'column_id': 'player_id_link'}, 'textAlign': 'left', 'whiteSpace': 'normal', 'height': 'auto', 'backgroundColor': 'inherit', 'color': 'inherit', 'fontWeight': 'normal', 'textDecoration': 'none', 'cursor': 'auto', 'fontSize': '12px'},
                {'if': {'row_index': 'odd'}, 'backgroundColor': '#FFFFFF'},
                {'if': {'row_index': 'even'}, 'backgroundColor': 'rgba(0, 92, 168, 0.65)'},
                {"if": {"state": "selected"}, "backgroundColor": "inherit !important", "border": "inherit !important"}
            ],
            row_selectable='multi',
            selected_rows=[],
            page_size=10,  # Number of rows per page
            page_action='native',  # Use pagination on the client side
            page_current=0,  # Current page number (you can adjust this based on your needs)
        ),
        html.Div(id='selected-rows-output'),
    ], style={'width': '50%', 'display': 'inline-block', 'height': '100vh', 'verticalAlign': 'top'}),
    html.Div([
        dcc.Graph(id='subplots')
    ], style={'display': 'inline-block', 'width': '50%'})
])

color_palette = ['#005ca8', 'rgba(0, 92, 168, 0.65)', '#FF5733', '#34A853', '#FFC300', '#FF5733', '#C70039']

# Define callback to update league options based on selected seasons and teams
@app.callback(
    Output('league-dropdown', 'options'),
    [Input('season-dropdown', 'value'), Input('team-dropdown', 'value')]
)
def update_league_dropdown(selected_seasons, selected_teams):
    filtered_df = df_with_hyperlinks
    
    if selected_seasons:
        filtered_df = filtered_df[filtered_df['season'].isin(selected_seasons)]
    if selected_teams:
        filtered_df = filtered_df[filtered_df['team'].isin(selected_teams)]
    
    league_options = [{'label': league, 'value': league} for league in filtered_df['league'].unique()]
    return league_options


# Define callback to update team options based on selected seasons and leagues
@app.callback(
    Output('team-dropdown', 'options'),
    [Input('season-dropdown', 'value'), Input('league-dropdown', 'value')]
)
def update_team_dropdown(selected_seasons, selected_leagues):
    if not selected_seasons and not selected_leagues:
        team_options = [{'label': team, 'value': team} for team in df_with_hyperlinks['team'].unique()]
    elif selected_seasons and not selected_leagues:
        filtered_df = df_with_hyperlinks[df_with_hyperlinks['season'].isin(selected_seasons)]
        team_options = [{'label': team, 'value': team} for team in filtered_df['team'].unique()]
    elif not selected_seasons and selected_leagues:
        filtered_df = df_with_hyperlinks[df_with_hyperlinks['league'].isin(selected_leagues)]
        team_options = [{'label': team, 'value': team} for team in filtered_df['team'].unique()]
    else:
        filtered_df = df_with_hyperlinks[
            (df_with_hyperlinks['season'].isin(selected_seasons)) &
            (df_with_hyperlinks['league'].isin(selected_leagues))
        ]
        team_options = [{'label': team, 'value': team} for team in filtered_df['team'].unique()]
    return team_options

# Define callback to update position options based on selected seasons, leagues, and teams
@app.callback(
    Output('position-dropdown', 'options'),
    [Input('season-dropdown', 'value'), Input('league-dropdown', 'value'), Input('team-dropdown', 'value')]
)
def update_position_dropdown(selected_seasons, selected_leagues, selected_teams):
    filtered_df = df_with_hyperlinks

    if selected_seasons:
        filtered_df = filtered_df[filtered_df['season'].isin(selected_seasons)]
    if selected_leagues:
        filtered_df = filtered_df[filtered_df['league'].isin(selected_leagues)]
    if selected_teams:
        filtered_df = filtered_df[filtered_df['team'].isin(selected_teams)]

    position_options = [{'label': position, 'value': position} for position in filtered_df['position'].unique()]
    return position_options


@app.callback(
    Output('data-table', 'selected_rows'),
    [Input('data-table', 'selected_rows')],
)
def enforce_selected_rows_limit(selected_rows):
    if len(selected_rows) > 4:
        return selected_rows[:4]
    return selected_rows


# Define callback to update table data based on selected values
@app.callback(
    Output('data-table', 'data'),
    [Input('season-dropdown', 'value'), Input('league-dropdown', 'value'), Input('team-dropdown', 'value'), Input('position-dropdown', 'value')]
)
def update_table_data(selected_seasons, selected_leagues, selected_teams, selected_positions):
    filtered_df = df_with_hyperlinks
    
    if selected_seasons:
        filtered_df = filtered_df[filtered_df['season'].isin(selected_seasons)]
    
    if selected_leagues:
        filtered_df = filtered_df[filtered_df['league'].isin(selected_leagues)]
    
    if selected_teams:
        filtered_df = filtered_df[filtered_df['team'].isin(selected_teams)]
    
    if selected_positions:
        filtered_df = filtered_df[filtered_df['position'].isin(selected_positions)]
    
    return filtered_df.head(14).to_dict('records')

# ... (previous code)

@app.callback(
    Output('subplots', 'figure'),
    [Input('data-table', 'selected_rows')],
    [State('data-table', 'data')]
)
def update_subplots(selected_rows, table_data):
    if selected_rows:
        selected_data = [table_data[i] for i in selected_rows]
        
        fig = make_subplots(rows=2, cols=2, subplot_titles=["Goals", "Assists", "Average Distance Covered", "Average Minutes Played"],
                           horizontal_spacing=0.1, vertical_spacing=0.15) # Adjust spacing between subplots

        legend_entries = set()  # To track unique player names for legend

        for i, data in enumerate(selected_data):
            player_name = f'{data["first_name"]} {data["last_name"]} | {data["season"]}'
            color = color_palette[i % len(color_palette)]

            # Only add a new legend entry if the player name is not already in the set
            if player_name not in legend_entries:
                legend_entries.add(player_name)
                showlegend = True
            else:
                showlegend = False

            fig.add_trace(go.Bar(x=[data["first_name"]], y=[data['goals']], name=player_name, marker_color=color, showlegend=showlegend), row=1, col=1)
            fig.add_trace(go.Bar(x=[data["first_name"]], y=[data['assists']], name=player_name, marker_color=color, showlegend=False), row=1, col=2)
            fig.add_trace(go.Bar(x=[data["first_name"]], y=[data['avg_distance_covered']], name=player_name, marker_color=color, showlegend=False), row=2, col=1)
            fig.add_trace(go.Bar(x=[data["first_name"]], y=[data['avg_minutes_played']], name=player_name, marker_color=color, showlegend=False), row=2, col=2)
            
            

        fig.update_layout(height=600, showlegend=True, legend_title_text='Player')
        fig.update_xaxes(showticklabels=False)
        return fig
    else:
        return go.Figure()




if __name__ == '__main__':
    app.run_server(debug=False)
