from datetime import date, time, timedelta, datetime
import os
import re
from re import match
from dash_core_components.Dropdown import Dropdown
import dateutil.parser
import locale
from dateutil.relativedelta import relativedelta
from io import StringIO
from math import comb
import locale

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_table
import dash_bootstrap_components as dbc

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from controls import CHAMPIONNATS, DROPDOWN_TO_CSV, DROPDOWN_TO_LOGO, DROPDOWN_TO_LINK
from utils import get_ranking_away, get_ranking_home, encode_image, create_score, create_classement_col, df_to_datatable

locale.setlocale(locale.LC_TIME, 'fr_FR')
pd.options.mode.chained_assignment = None

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)

#OPTIONS
saison="2021"

app.config['suppress_callback_exceptions'] = True

server = app.server

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Accueil", href="/Home")),
        dbc.NavItem(dbc.NavLink("Stats du championnat", href="/Stats-championnats")),
        dbc.NavItem(dbc.NavLink("Stats par équipe", href="/Stats-par-equipes")),
        dbc.NavItem(dbc.NavLink("Face à Face", href="/face-to-face")),
    ],
    brand="Football Data",
    brand_href="#",
    color="primary",
    dark=True,
)

dropdown = dbc.DropdownMenu(
    [   
        dbc.DropdownMenuItem("France", header=True) ,
        dbc.DropdownMenuItem("Ligue 1", id='France1'),
        dbc.DropdownMenuItem("Ligue 2", id='France2'),
        dbc.DropdownMenuItem(divider=True),
        dbc.DropdownMenuItem("Allemagne", header=True) ,
        dbc.DropdownMenuItem("Bundesliga 1", id='Allemagne1'),
        dbc.DropdownMenuItem("Bundesliga 2", id='Allemagne2'),
        dbc.DropdownMenuItem(divider=True),
        dbc.DropdownMenuItem("Angleterre", header=True) ,
        dbc.DropdownMenuItem("Premiere League", id='Angleterre1'),
        dbc.DropdownMenuItem("Championship", id='Angleterre2'),
        dbc.DropdownMenuItem(divider=True),
        dbc.DropdownMenuItem("Espagne", header=True) ,
        dbc.DropdownMenuItem("Liga", id='Espagne1'),
        dbc.DropdownMenuItem("Liga Smart Bank", id='Espagne2'),
        dbc.DropdownMenuItem(divider=True),
        dbc.DropdownMenuItem("Italie", header=True) ,
        dbc.DropdownMenuItem("Série A", id='Italie1'),
        dbc.DropdownMenuItem("Série B", id='Italie2'),
        dbc.DropdownMenuItem(divider=True)
    ],
    label="Choix du championnat",
    nav=True,
    in_navbar=True
)

navbar_titre = dbc.NavbarSimple(
    dropdown,
    brand="App Data Visualisation Football",
    brand_href="#",
    color="primary",
    dark=True,
)

app.layout = html.Div(
    [dcc.Location(id="url", refresh=False),
    navbar_titre,
    html.Br(),
    html.Div(html.H4(id='path-csv'), style={'display':'none'}),
    html.Div(html.H4(id='nom-ligue'), style={'display':'none'}),

    dbc.Row(
        [
            dbc.Col(html.Img(
                id='logo-ligue',
                className='logo'
            ), width={'offset':1}
            ),
            dbc.Col(html.Div(html.H1(id='phrase-ligue'), style={"text-align":"center", 'margin-top':'5mm'})),
            dbc.Col(dbc.Button("Site de la ligue", id ='button-ligue', color="primary"), width=3, style={'margin-top':'4mm'})
        ],
    ),
    html.Br(),
    navbar,
    html.Div(
        [
            html.Div(
                [
                dbc.Alert('Attention, les statistiques détaillées ne sont pas disponibles pour certains matchs ... ', color="danger"),
                dbc.Alert(html.Div(id='matchs-bugged'), color='danger'),
                ],
                id="warning-NaN",
                style={'display':'block'}),
                html.Div(id='clubs-bugs',style={'display':'none'})
        ]
    ),
    html.Div(id="page-content"),
    ],
    className='page'
)

@app.callback(
    Output('path-csv', 'children'),
    Output('nom-ligue', 'children'),
    Output('phrase-ligue', 'children'),

    [
        Input("France1", 'n_clicks'),
        Input("France2", 'n_clicks'),
        Input("Allemagne1", 'n_clicks'),
        Input("Allemagne2", 'n_clicks'),
        Input("Angleterre1", 'n_clicks'),
        Input("Angleterre2", 'n_clicks'),
        Input("Espagne1", 'n_clicks'),
        Input("Espagne2", 'n_clicks'),
        Input("Italie1", 'n_clicks'),
        Input("Italie2", 'n_clicks'),
    ]
)
def get_csv_path(*args):
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = 'France1'
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    encoded_image = encode_image(DROPDOWN_TO_LOGO.get(button_id))
    source = 'data:image/png;base64,{}'.format(encoded_image.decode()),
    return DROPDOWN_TO_CSV.get(button_id), button_id, "{}".format(CHAMPIONNATS.get(button_id))

@app.callback(
    Output('logo-ligue', 'src'),
    Input('nom-ligue', 'children')
)
def get_ligue_logo(ligue):
    encoded_image = encode_image(DROPDOWN_TO_LOGO.get(ligue))
    return 'data:image/png;base64,{}'.format(encoded_image.decode())

@app.callback(
    Output('button-ligue', 'href'),
    Input('nom-ligue', 'children')
)
def get_ligue_logo(ligue):
    return DROPDOWN_TO_LINK.get(ligue)

@app.callback(
    [Output('warning-NaN', 'style'),
    Output('matchs-bugged', 'children'),
    Output('clubs-bugs', 'children')],
    Input('path-csv', 'children')
)
def check_nan_in_df(path_csv):
    df = pd.read_csv(path_csv, engine='python')
    df = df[['Div','Date','Time','HomeTeam','AwayTeam','FTHG','FTAG','FTR','HTHG','HTAG','HTR','HS','AS','HST','AST','HF','AF','HC','AC','HY','AY','HR','AR',]]
    if df.isnull().any(axis=1).any():
        bug = df[df.isnull().any(axis=1)][['HomeTeam','AwayTeam', 'Date']]
        clubs = np.unique(bug[['HomeTeam', 'AwayTeam']].values).tolist()
        phrase = [html.Div("Match(s) concerné(s) :")]
        matchs = [html.Div("{}-{}  ({})".format(item[0], item[1], item[2])) for item in bug.values.tolist()]
        return {'display':'block'}, phrase+matchs, clubs
    else:
        return {'display':'none'}, None, [None]



home_layout = html.Div(
    [
        html.Div(
            [
                html.Br(),
                html.Div(
                    [
                        dbc.CardDeck(
                            [
                                dbc.Card(
                                    [
                                        html.H6(['Matchs effectués',], className='card-title', style={"text-align":'center', 'margin-top':'4mm'}),
                                        html.H3(dbc.Badge(id='nombre-match', color='primary'), style={"text-align":'center'})
                                    ],
                                    color="primary",
                                    inverse=True,
                                    className='box-small'
                                ),
                                dbc.Card(
                                    [
                                        html.H6('Avancement de la saison', className='card-title', style={"text-align":'center', 'margin-top':'4mm'}),
                                        dbc.Progress(id='progress-bar',value=0, striped=True)
                                    ],
                                    color='primary',
                                    inverse=True,
                                    className='box-small'
                                ),
                                dbc.Card(
                                    [
                                        html.H6('Buts Marqués', className='card-title', style={"text-align":'center', 'margin-top':'4mm'}),
                                        html.H3(dbc.Badge(id='nombre-buts', color="primary"), style={"text-align":'center'}),
                                    ],
                                    color='primary',
                                    inverse=True,
                                    className='box-small'
                                ),
                                dbc.Card(
                                    [
                                        html.H6('Buts / matchs', className='card-title', style={"text-align":'center', 'margin-top':'4mm'}),
                                        html.H3(dbc.Badge(id="but-par-match", color="primary"), style={"text-align":'center'}),
                                    ],
                                    color='primary',
                                    inverse=True,
                                    className='box-small'
                                ),
                                dbc.Card(
                                    [
                                        html.H6('1 but toutes les', className="card-title", style={"text-align":'center', 'margin-top':'4mm'}),
                                        html.H3(dbc.Badge(id="but-toutes-les", color="primary"), style={"text-align":'center'}),
                                    ],
                                    color='primary',
                                    inverse=True,
                                    className='box-small'
                                ),
                            ],
                            className='row',
                        ),
                    ]
                ),
                html.Br(),
                html.H1('Classements', style={"text-align":"center"}),
                html.Div(
                    [
                        dcc.Tabs(
                            [
                                dcc.Tab(
                                    [
                                        dash_table.DataTable(
                                            id='table_général',
                                            sort_action='native',
                                            page_action="native",
                                            page_current= 0,
                                            page_size=30,
                                            style_data_conditional=[
                                                {
                                                    'if': {'row_index': 'odd'},
                                                    'backgroundColor': 'rgb(248, 248, 248)'
                                                }
                                            ],
                                            style_header={
                                                'backgroundColor': 'rgb(230, 230, 230)',
                                                'fontWeight': 'bold'
                                            },
                                        ), 
                                    ],
                                    label="Classement Général",
                                    #tab_id="tab-1",
                                    #tabClassName="ml-auto"
                                ), 
                                dcc.Tab(
                                    [
                                        dash_table.DataTable(
                                            id='table_domicile',
                                            sort_action='native',
                                            page_action="native",
                                            page_current= 0,
                                            page_size=30,
                                            style_data_conditional=[
                                                {
                                                    'if': {'row_index': 'odd'},
                                                    'backgroundColor': 'rgb(248, 248, 248)'
                                                }
                                            ],
                                            style_header={
                                                'backgroundColor': 'rgb(230, 230, 230)',
                                                'fontWeight': 'bold'
                                            },
                                        ), 
                                    ],
                                    label="Classement à domicile",
                                    #tab_id='tab-2',
                                    #tabClassName="ml-auto"
                                ),
                                    
                                dcc.Tab(
                                    [
                                        dash_table.DataTable(
                                            id='table_exterieur',
                                            sort_action='native',
                                            page_action="native",
                                            page_current= 0,
                                            page_size=30,
                                            style_data_conditional=[
                                                {
                                                    'if': {'row_index': 'odd'},
                                                    'backgroundColor': 'rgb(248, 248, 248)'
                                                }
                                            ],
                                            style_header={
                                                'backgroundColor': 'rgb(230, 230, 230)',
                                                'fontWeight': 'bold'
                                            },
                                        ), 
                                    ],
                                    label="Classement à l'extérieur",
                                    #tab_id='tab-3',
                                    #tabClassName="ml-auto"
                                )
                            ], 
                            id='tab-classement',
                            #active_tab='tab-1'
                        )
                    ],
                    className='table-custom'
                ),
            ],
        ),
    ],
    className='page'
)



@app.callback(
    [Output("progress-bar", "value"), Output("progress-bar", "children"), Output('nombre-match', 'children')],
    Input('path-csv', 'children'),
)
def update_progress_bar(path_csv):
    df = pd.read_csv(path_csv)
    clubs = np.unique(df[['HomeTeam', 'AwayTeam']].values).tolist()
    len_season = comb(len(clubs), 2)*2
    progress =  round((len(df)/len_season)*100)
    return progress, f"{progress} %" if progress >= 5 else "", "{}/{}".format(len(df), len_season)

@app.callback(
    [Output("nombre-buts", "children"), Output("but-par-match", "children"), Output('but-toutes-les', 'children')],
    Input('path-csv', 'children'),
)
def update_but_infos(path_csv):
    df = pd.read_csv(path_csv)
    nombre_but = df.FTHG.sum() + df.FTAG.sum()
    but_par_match = nombre_but/len(df)
    but_toute_les = 90/but_par_match
    return nombre_but, round(but_par_match,2), "{} minutes".format(round(but_toute_les))

@app.callback(
    [
        Output('table_général', 'data'), Output('table_général', 'columns'),
        Output('table_domicile', 'data'), Output('table_domicile', 'columns'),
        Output('table_exterieur', 'data'), Output('table_exterieur', 'columns'),
    ],
    Input('path-csv', 'children'),
)
def update_classement(path_csv):
    df = pd.read_csv(path_csv)
    #Classement général
    dic = {
        team:{'Club':team,
            'Points': df[(df.HomeTeam == team)]['FTR'].apply(get_ranking_home).sum() + df[(df.AwayTeam == team)]['FTR'].apply(get_ranking_away).sum(),
            'Joués':len(df[(df.HomeTeam==team)|(df.AwayTeam == team)]),
            'Gagnés':len(df[((df.HomeTeam==team) & (df.FTR=='H'))|((df.AwayTeam == team)&(df.FTR=='A'))]),
            'Nul':len(df[((df.HomeTeam==team) & (df.FTR=='D'))|((df.AwayTeam == team)&(df.FTR=='D'))]),
            'Perdus':len(df[((df.HomeTeam==team) & (df.FTR=='A'))|((df.AwayTeam == team)&(df.FTR=='H'))]),
            'Pour':df[(df.HomeTeam==team)].FTHG.sum() + df[(df.AwayTeam==team)].FTAG.sum(),
            'Contre':df[(df.HomeTeam==team)].FTAG.sum() + df[(df.AwayTeam==team)].FTHG.sum(),
            'Goal Average':df[(df.HomeTeam==team)].FTHG.sum() + df[(df.AwayTeam==team)].FTAG.sum() - df[(df.HomeTeam==team)].FTAG.sum() - df[(df.AwayTeam==team)].FTHG.sum(),
        }
        for team in df.HomeTeam.unique()
    }
    
    df_ranking = pd.DataFrame.from_dict(dic, orient='index')
    
    df_ranking.sort_values(['Points', 'Goal Average'], ascending=False, inplace=True)
    df_ranking = create_classement_col(df_ranking)
    data_table_general, columns_table_general = df_to_datatable(df_ranking)
    #Classement domicile
    dic = {
        team:{'Club':team,
            'Points': df[(df.HomeTeam == team)]['FTR'].apply(get_ranking_home).sum(),
            'Joués':len(df[(df.HomeTeam==team)]),
            'Gagnés':len(df[((df.HomeTeam==team) & (df.FTR=='H'))]),
            'Nul':len(df[((df.HomeTeam==team) & (df.FTR=='D'))]),
            'Perdus':len(df[((df.HomeTeam==team) & (df.FTR=='A'))]),
            'Pour':df[(df.HomeTeam==team)].FTHG.sum(),
            'Contre':df[(df.HomeTeam==team)].FTAG.sum(),
            'Goal Average':df[(df.HomeTeam==team)].FTHG.sum() - df[(df.HomeTeam==team)].FTAG.sum(),
        }
        for team in df.HomeTeam.unique()
    }
    
    df_home = pd.DataFrame.from_dict(dic, orient='index')
    
    df_home.sort_values(['Points', 'Goal Average'], ascending=False, inplace=True)
    df_home = create_classement_col(df_home)
    data_table_domicile, columns_table_domicile = df_to_datatable(df_home)

    #Classement extérieur
    dic = {
        team:{'Club':team,
            'Points': df[(df.AwayTeam == team)]['FTR'].apply(get_ranking_away).sum(),
            'Joués':len(df[(df.AwayTeam == team)]),
            'Gagnés':len(df[((df.AwayTeam == team)&(df.FTR=='A'))]),
            'Nul':len(df[((df.AwayTeam == team)&(df.FTR=='D'))]),
            'Perdus':len(df[((df.AwayTeam == team)&(df.FTR=='H'))]),
            'Pour':df[(df.AwayTeam==team)].FTAG.sum(),
            'Contre':df[(df.AwayTeam==team)].FTHG.sum(),
            'Goal Average':df[(df.AwayTeam==team)].FTAG.sum() - df[(df.AwayTeam==team)].FTHG.sum(),
        }
        for team in df.HomeTeam.unique()
    }
    
    df_ext = pd.DataFrame.from_dict(dic, orient='index')
    
    df_ext.sort_values(['Points', 'Goal Average'], ascending=False, inplace=True)
    df_ext = create_classement_col(df_ext)
    data_table_exterieur, columns_table_exterieur = df_to_datatable(df_ext)

    return data_table_general, columns_table_general, data_table_domicile, columns_table_domicile, data_table_exterieur, columns_table_exterieur



stat_championnat_layout = html.Div(
    [
        html.Br(),
        html.Div(
            [
                html.H1('Répartition des résultats', style={"text-align":"center"}),
                dcc.Graph(id='two-results-fig')
            ]
        ),
        html.Hr(),
        html.H1("Classements divers", style={"text-align":"center"}),
        dbc.Col(
            dbc.CardDeck(
                [
                    dbc.Card(
                        [
                        html.H4('Meilleure attaque', className='card-title'),

                        html.Div(id='meilleure-attaque')
                        ],
                        color="primary",
                        inverse=True,
                        className='pretty-container'
                    ),
                    dbc.Card(
                        [
                        html.H4('Meilleure defense', className='card-title'),

                        html.Div(id='meilleure-defense')
                        ],
                        color="primary",
                        inverse=True,
                        className='pretty-container'
                    )
                ]

            )
        ),
        html.Hr(),
        html.Div(
            [
                html.H1('Répartition des buts marqués', style={"text-align":"center"}),
                dcc.Graph(id='two-goals-fig')
            ]
        ),
    ],
    className='page'
)

@app.callback(
    Output('meilleure-attaque', 'children'),
    Output('meilleure-defense', 'children'),
    Input('path-csv', 'children'),
)
def update_cards(path_csv):
    df = pd.read_csv(path_csv)
    dic = {
        team:{'Club':team,
            'Points': df[(df.HomeTeam == team)]['FTR'].apply(get_ranking_home).sum() + df[(df.AwayTeam == team)]['FTR'].apply(get_ranking_away).sum(),
            'Domicile':df[(df.HomeTeam == team)]['FTR'].apply(get_ranking_home).sum(),
            'Extérieur':df[(df.AwayTeam == team)]['FTR'].apply(get_ranking_away).sum(),
            'Joués':len(df[(df.HomeTeam==team)|(df.AwayTeam == team)]),
            'Gagnés':len(df[((df.HomeTeam==team) & (df.FTR=='H'))|((df.AwayTeam == team)&(df.FTR=='A'))]),
            'Nul':len(df[((df.HomeTeam==team) & (df.FTR=='D'))|((df.AwayTeam == team)&(df.FTR=='D'))]),
            'Perdus':len(df[((df.HomeTeam==team) & (df.FTR=='A'))|((df.AwayTeam == team)&(df.FTR=='H'))]),
            'Pour':df[(df.HomeTeam==team)].FTHG.sum() + df[(df.AwayTeam==team)].FTAG.sum(),
            'Contre':df[(df.HomeTeam==team)].FTAG.sum() + df[(df.AwayTeam==team)].FTHG.sum(),
            'Goal Average':df[(df.HomeTeam==team)].FTHG.sum() + df[(df.AwayTeam==team)].FTAG.sum() - df[(df.HomeTeam==team)].FTAG.sum() - df[(df.AwayTeam==team)].FTHG.sum(),
        }
        for team in df.HomeTeam.unique()
    }
    n=3
    sep = [dbc.ListGroupItem("...",  style={"background-color":'black'})]
    df_ranking = pd.DataFrame.from_dict(dic, orient='index')
    attaque_head = [dbc.ListGroupItem("{}. {} : {} buts marqués".format(index+1, item[0], item[1]), style={"background-color":'black'}) for index, item in enumerate(df_ranking.sort_values('Pour', ascending=False)[['Club', 'Pour']].head(n).values)]
    défense_head = [dbc.ListGroupItem("{}. {} : {} buts encaissés".format(index+1, item[0], item[1]), style={"background-color":'black'}) for index, item in enumerate(df_ranking.sort_values('Contre')[['Club', 'Contre']].head(n).values)]
    attaque_tail = sep +[dbc.ListGroupItem("{}. {} : {} buts marqués".format(len(df_ranking)-(n-1)+index, item[0], item[1]), style={"background-color":'black'}) for index, item in enumerate(df_ranking.sort_values('Pour', ascending=False)[['Club', 'Pour']].tail(n).values)]
    défense_tail = sep + [dbc.ListGroupItem("{}. {} : {} buts encaissés".format(len(df_ranking)-(n-1)+index, item[0], item[1]), style={"background-color":'black'}) for index, item in enumerate(df_ranking.sort_values('Contre')[['Club', 'Contre']].tail(n).values)]
    return attaque_head+attaque_tail, défense_head+défense_tail


@app.callback(
    Output('two-goals-fig', 'figure'),
    Input('path-csv', 'children'),
)
def update_pie_charts(path_csv):
    df = pd.read_csv(path_csv)
    labels_half = ['1ère mi-temps', '2nde mi-temps']
    values_half = [df['HTHG'].sum() + df['HTAG'].sum(), df['FTHG'].sum() + df['FTAG'].sum() - df['HTHG'].sum() - df['HTAG'].sum()]
    labels_home_away = ['A domicile', "A l'extérieur"]
    values_home_away = [df['FTHG'].sum(), df['FTAG'].sum()]

    fig = make_subplots(1, 2, specs=[[{'type':'domain'}, {'type':'domain'}]],
                    subplot_titles=['Buts par mi-temps', "Buts à domicile ou à l'extérieur"])
    fig.add_trace(go.Pie(labels=labels_half, values=values_half, scalegroup='one',
                     name="Buts marqués"), 1, 1)
    fig.add_trace(go.Pie(labels=labels_home_away, values=values_home_away, scalegroup='one',
                     name="Buts marqués"), 1, 2)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

@app.callback(
    Output('two-results-fig', 'figure'),
    Input('path-csv', 'children'),
)
def update_pie_charts(path_csv):
    df = pd.read_csv(path_csv)
    labels = ['Domicile', 'Match Nul', 'Extérieur']
    values = [len(df[df.FTR=='H']), len(df[df.FTR=='D']), len(df[df.FTR=='A'])]
    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig


stat_par_equipe_layout = html.Div(
    [
        html.Br(),
        html.Div(
            [
                html.H1('Tirs/Tirs cadrés/Buts : ', style={"text-align":"center"}),
                dbc.Col(
                    dbc.CardDeck(
                        [
                            dbc.Card(
                                [
                                html.H4('Total des tirs', className='card-title', style={'color':'white'}),
                                dbc.ListGroup(id='classement-tirs', className='cart-text', flush=True)
                                ],
                                className='pretty-container',
                                inverse=True,
                                color="primary",
                            ),
                            dbc.Card(
                                [
                                html.H4("Tirs cadrés", className='card-title'),
                                dbc.ListGroup(id='classement-tirs-cadrés', className='cart-text', flush=True)
                                ],
                                color="primary",
                                inverse=True,
                                className='pretty-container'
                            ),
                            dbc.Card(
                                [
                                html.H4('But marqués', className='card-title'),
                                html.Div(id='classement-buts')
                                ],
                                color="primary",
                                inverse=True,
                                className='pretty-container'
                            )
                        ]

                    ),
                ),
                dcc.Graph(id='shots-goals-fig')
            ]
        ),
        html.Hr(),
        html.Div(
            [
                html.H1('Cartons Jaunes/Rouges', style={"text-align":"center"}),
                dbc.Col(
                    dbc.CardDeck(
                        [
                            dbc.Card(
                                [
                                html.H4('Fautes', className='card-title', style={'color':'white'}),
                                dbc.ListGroup(id='classement-fautes', className='cart-text', flush=True)
                                ],
                                className='pretty-container',
                                inverse=True,
                                color="primary",
                            ),
                            dbc.Card(
                                [
                                html.H4("Cartons Jaunes", className='card-title'),
                                dbc.ListGroup(id='classement-jaunes', className='cart-text', flush=True)
                                ],
                                color="primary",
                                inverse=True,
                                className='pretty-container'
                            ),
                            dbc.Card(
                                [
                                html.H4('Cartons Rouges', className='card-title'),
                                html.Div(id='classement-rouges')
                                ],
                                color="primary",
                                inverse=True,
                                className='pretty-container'
                            )
                        ]

                    ),
                ),
                dcc.Graph(id='yellow-red-cards-fig')
            ]
        )
    ],
    className='page'
)

@app.callback(
    Output('classement-tirs', 'children'),
    Output('classement-tirs-cadrés', 'children'),
    Output('classement-buts', 'children'),
    Output('classement-fautes', 'children'),
    Output('classement-jaunes', 'children'),
    Output('classement-rouges', 'children'),
    Input('path-csv', 'children'),
)
def update_cards(path_csv):
    df = pd.read_csv(path_csv)
    dic = {
        team:{'Club':team,
            'Pour':df[(df.HomeTeam==team)].FTHG.sum() + df[(df.AwayTeam==team)].FTAG.sum(),
            'Tirs':df[(df.HomeTeam==team)].HS.sum() + df[(df.AwayTeam==team)].AS.sum(),
            'Tirs Cadrés':df[(df.HomeTeam==team)].HST.sum() + df[(df.AwayTeam==team)].AST.sum(),
            'Fautes':df[(df.HomeTeam==team)].HF.sum() + df[(df.AwayTeam==team)].AF.sum(),
            'Jaunes':df[(df.HomeTeam==team)].HY.sum() + df[(df.AwayTeam==team)].AY.sum(),
            'Rouges':df[(df.HomeTeam==team)].HR.sum() + df[(df.AwayTeam==team)].AR.sum(),
        }
        for team in df.HomeTeam.unique()
    }
    n=3
    sep = [dbc.ListGroupItem("...",  style={"background-color":'black'})]
    df_ranking = pd.DataFrame.from_dict(dic, orient='index')
    tirs_head = [dbc.ListGroupItem("{}. {} : {} tirs".format(index+1, item[0], int(item[1])), style={"background-color":'black'}) for index, item in enumerate(df_ranking.sort_values('Tirs', ascending=False)[['Club', 'Tirs']].head(n).values)]
    tirs_cadres_head = [dbc.ListGroupItem("{}. {} : {} tirs cadrés".format(index+1, item[0], int(item[1])), style={"background-color":'black'}) for index, item in enumerate(df_ranking.sort_values('Tirs Cadrés', ascending=False)[['Club', 'Tirs Cadrés']].head(n).values)]
    buts_head = [dbc.ListGroupItem("{}. {} : {} buts marqués".format(index+1, item[0], int(item[1])), style={"background-color":'black'}) for index, item in enumerate(df_ranking.sort_values('Pour', ascending=False)[['Club', 'Pour']].head(n).values)]
    fautes_head = [dbc.ListGroupItem("{}. {} : {} fautes commises".format(index+1, item[0], int(item[1])), style={"background-color":'black'}) for index, item in enumerate(df_ranking.sort_values('Fautes', ascending=False)[['Club', 'Fautes']].head(n).values)]
    jaunes_head = [dbc.ListGroupItem("{}. {} : {} cartons jaunes".format(index+1, item[0], int(item[1])), style={"background-color":'black'}) for index, item in enumerate(df_ranking.sort_values('Jaunes', ascending=False)[['Club', 'Jaunes']].head(n).values)]
    rouges_head = [dbc.ListGroupItem("{}. {} : {} cartons rouges".format(index+1, item[0], int(item[1])), style={"background-color":'black'}) for index, item in enumerate(df_ranking.sort_values('Rouges', ascending=False)[['Club', 'Rouges']].head(n).values)]
    tirs_tail = sep + [dbc.ListGroupItem("{}. {} : {} tirs".format(len(df_ranking)-(n-1)+index, item[0], int(item[1])), style={"background-color":'black'}) for index, item in enumerate(df_ranking.sort_values('Tirs', ascending=False)[['Club', 'Tirs']].tail(n).values)]
    tirs_cadres_tail = sep + [dbc.ListGroupItem("{}. {} : {} tirs cadrés".format(len(df_ranking)-(n-1)+index, item[0], int(item[1])), style={"background-color":'black'}) for index, item in enumerate(df_ranking.sort_values('Tirs Cadrés', ascending=False)[['Club', 'Tirs Cadrés']].tail(n).values)]
    buts_tail = sep + [dbc.ListGroupItem("{}. {} : {} buts marqués".format(len(df_ranking)-(n-1)+index, item[0], int(item[1])), style={"background-color":'black'}) for index, item in enumerate(df_ranking.sort_values('Pour', ascending=False)[['Club', 'Pour']].tail(n).values)]
    fautes_tail = sep + [dbc.ListGroupItem("{}. {} : {} fautes commises".format(len(df_ranking)-(n-1)+index, item[0], int(item[1])), style={"background-color":'black'}) for index, item in enumerate(df_ranking.sort_values('Fautes', ascending=False)[['Club', 'Fautes']].tail(n).values)]
    jaunes_tail = sep + [dbc.ListGroupItem("{}. {} : {} cartons jaunes".format(len(df_ranking)-(n-1)+index, item[0], int(item[1])), style={"background-color":'black'}) for index, item in enumerate(df_ranking.sort_values('Jaunes', ascending=False)[['Club', 'Jaunes']].tail(n).values)]
    rouges_tail = sep + [dbc.ListGroupItem("{}. {} : {} cartons rouges".format(len(df_ranking)-(n-1)+index, item[0], int(item[1])), style={"background-color":'black'}) for index, item in enumerate(df_ranking.sort_values('Rouges', ascending=False)[['Club', 'Rouges']].tail(n).values)]
   
    return tirs_head+tirs_tail, tirs_cadres_head+tirs_cadres_tail, buts_head+buts_tail,fautes_head+fautes_tail, jaunes_head+jaunes_tail, rouges_head+rouges_tail

@app.callback(
    Output('shots-goals-fig', 'figure'),
    Input('path-csv', 'children'),
)
def update_teams_plot(path_csv):
    df = pd.read_csv(path_csv)
    clubs = df['HomeTeam'].unique().tolist()
    values_shots= [df[df.HomeTeam == club].HS.sum() + df[df.AwayTeam == club].AS.sum() for club in clubs]
    values_shots_on_target=[df[(df.HomeTeam == club)].HST.sum() + df[df.AwayTeam == club].AST.sum() for club in clubs]
    values_goals = [df[(df.HomeTeam == club)].FTHG.sum() + df[df.AwayTeam == club].FTAG.sum() for club in clubs]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=clubs,
                    y=values_shots,
                    name='Nombre de tirs',
                    marker_color='rgb(55, 83, 109)'
                    ))
    fig.add_trace(go.Bar(x=clubs,
                    y=values_shots_on_target,
                    name='Nombre de tirs cadrés',
                    marker_color='rgb(26, 118, 255)'
                    ))
    fig.add_trace(go.Bar(x=clubs,
                    y=values_goals,
                    name='Nombre de buts',
                    marker_color='rgb(12, 100, 201)'
                    ))

    fig.update_layout(
        xaxis_tickfont_size=14,
        legend=dict(
            x=0,
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)'
        ),
        barmode='group',
        bargap=0.15, # gap between bars of adjacent location coordinates.
        bargroupgap=0.1 # gap between bars of the same location coordinate.
    )
    return fig

@app.callback(
    Output('yellow-red-cards-fig', 'figure'),
    Input('path-csv', 'children'),
)
def update_teams_plot(path_csv):
    df = pd.read_csv(path_csv)
    clubs = df['HomeTeam'].unique().tolist()
    values_yellow= [df[(df.HomeTeam == club)].HY.sum() + df[df.AwayTeam == club].AY.sum() for club in clubs]
    values_red=[df[(df.HomeTeam == club)].HR.sum() + df[df.AwayTeam == club].AR.sum() for club in clubs]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=clubs,
                    y=values_yellow,
                    name='Cartons jaunes',
                    marker_color='rgb(255,215,0)'
                    ))
    fig.add_trace(go.Bar(x=clubs,
                    y=values_red,
                    name='Cartons rouges',
                    marker_color='rgb(139,0,0)'
                    ))

    fig.update_layout(
        xaxis_tickfont_size=14,
        legend=dict(
            x=0,
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)'
        ),
        barmode='group',
        bargap=0.15, # gap between bars of adjacent location coordinates.
        bargroupgap=0.1 # gap between bars of the same location coordinate.
    )
    return fig


face_a_face_layout = html.Div(
    [
        html.Br(),
        html.Div(
            [
                html.H2('Choisis 2 clubs :', style={"text-align":"center"}),
                dbc.Row(
                    [
                        dbc.Col(dcc.Dropdown(
                            id='dropdown-club', 
                            clearable=False,
                        ), width={'size':4, 'offset':1}
                        ),
                        dbc.Col(dcc.Dropdown(
                        id='dropdown-club-1', 
                        clearable=False,
                        ),
                        width={'size':4, 'offset':2}
                        )
                    ]
                ),
                html.Br(),
                html.Div(id='div-progress-bar-face-a-face'),
            ],
        ),
        html.Br(),
        html.Div(id='alerte-table-vide'),

        dbc.Col(
            [
                html.Div(id='card-face-a-face'
                )
            ],
            width={'size':6, 'offset':3}
        ),
        html.Div(id="3-confrontations"),
        html.Div(
            [
                html.Div(
                    [
                        html.Hr(),
                        dbc.Button(
                            "Voir toutes les confrontations",
                            id="collapse-button",
                            className="mb-3",
                            color="primary",
                        ),        
                        dbc.Collapse(
                            html.Div(id='all-confrontations'),
                            id='collapse'
                        )
                    ],
                    id='div-to-hide',
                    style={"display":'block'}
                )
            ]
        )
    ],
    className='page'
)

@app.callback(
    Output("collapse", "is_open"),
    [Input("collapse-button", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    [Output('dropdown-club', 'options'),Output('dropdown-club', 'value'),Output('dropdown-club-1', 'options'), Output('dropdown-club-1', 'value')],
    Input('path-csv', 'children'),
)
def get_club_list(path_csv):
    liste_csv = os.listdir(os.path.dirname(path_csv))
    liste_df = [pd.read_csv(os.path.dirname(path_csv) + '/' + file, engine='python') for file in liste_csv]
    df = pd.concat(liste_df)
    df.dropna(subset=['HomeTeam', 'AwayTeam'],inplace=True)
    teams = list(set(pd.unique(df['AwayTeam']).tolist()+pd.unique(df['HomeTeam']).tolist()))
    options_teams = [{"label": str(item), "value": str(item)} for item in sorted(teams)]
    return options_teams, teams[0], options_teams, teams[1]


@app.callback(
    [Output('div-progress-bar-face-a-face', 'children'),
        Output('alerte-table-vide', 'children'),
        Output('card-face-a-face', 'children'),
        Output('3-confrontations', 'children'), 
        Output('all-confrontations', 'children'), 
        Output('div-to-hide', 'style')],
    [Input('path-csv', 'children'), Input('dropdown-club', 'value'), Input('dropdown-club-1', 'value'), Input('clubs-bugs', 'children')]
)
def update_face_to_face_table(path_csv, club1, club2, *bugs):
    liste_csv = os.listdir(os.path.dirname(path_csv))
    liste_df = [pd.read_csv(os.path.dirname(path_csv) + '/'+ file, engine='python') for file in liste_csv]
    full_df = pd.concat(liste_df)
    df = full_df[((full_df.HomeTeam==club1)&(full_df.AwayTeam==club2))|((full_df.HomeTeam==club2)&(full_df.AwayTeam==club1))]
    if df.empty:
        alert = dbc.Alert("Il n'y a pas eu de confrontations entre ces deux clubs depuis la saison 2010/2011.", color="danger", style={"text-align":"center"})
        display_collapse = {'display': 'none'}
        return None, alert, None, None, None, display_collapse
    else:
        df_table = df[['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'HTHG', 'HTAG', 'B365H', 'B365D', 'B365A', 'HS', 'AS','HST', 'AST', 'HY', 'AY', 'HR', 'AR']]
        df_table[['FTHG', 'FTAG']] = df_table[['FTHG', 'FTAG']].astype(int).astype(str)
        df_table.loc[:,'FT'] = df_table[['FTHG', 'FTAG']].agg('-'.join, axis=1)
        if (club1 in bugs[0]) & (club2 in bugs[0]):
            df_table.loc[:,'Score Final (mi-temps)'] = df_table['FT']
        else:
            df_table[['HTHG', 'HTAG']] = df_table[['HTHG', 'HTAG']].astype(int).astype(str)
            df_table.loc[:,'HT'] = df_table[['HTHG', 'HTAG']].agg('-'.join, axis=1)
            df_table.loc[:,'Score Final (mi-temps)'] = create_score(df_table['FT'].astype(str), df_table['HT'].astype(str))
            
        df_table.loc[:,'Resultat'] = np.where(df_table.FTHG>df_table.FTAG, df.HomeTeam, np.where(df_table.FTHG==df_table.FTAG, 'Match Nul', df.AwayTeam))
        #PROGRESS BAR : 
        winclub1 = round(100*len(df_table[club1==df_table.Resultat])/len(df_table))
        draw = round(100*len(df_table[df_table.Resultat=='Match Nul'])/len(df_table))
        winclub2 = round(100*len(df_table[club2==df_table.Resultat])/len(df_table))
        child_winclub1 = f"{club1} : {len(df_table[club1==df_table.Resultat])}" if winclub1 >= 15 else ""
        child_draw = f"Matchs Nuls : {len(df_table[df_table.Resultat=='Match Nul'])}" if draw >= 15 else ""
        child_winclub2 = f"{club2} : {len(df_table[club2==df_table.Resultat])}" if winclub2 >= 15 else ""

        progress_bar = html.Div(
            [
                dbc.Row(dbc.Col("Nombre de matchs joués : {}".format(len(df_table)), width={'size':5, 'offset':5})),
                dbc.Row(
                    dbc.Col(dbc.Progress(
                        [
                            dbc.Progress(child_winclub1, value=winclub1,color="success", bar=True),
                            dbc.Progress(child_draw, value=draw, color="warning", bar=True),
                            dbc.Progress(child_winclub2, value=winclub2,color="danger", bar=True),
                        ],
                        multi=True,
                    ), width={'size':10, 'offset':1})
                )
            ]
        ),



        #Table description
        dic_descr = {'Victoires':[len(df_table[df_table['Resultat']==club]) for club in [club1, club2]],
            'Buts':[df_table[(df_table['HomeTeam']==club)].FTHG.astype(int).sum() + df_table[(df_table.AwayTeam == club)].FTAG.astype(int).sum() for club in [club1, club2]],
            'Tirs' : [df_table[(df_table['HomeTeam']==club)].HS.sum() + df_table[(df_table.AwayTeam == club)].AS.sum() for club in [club1, club2]],
            'Tirs Cadrés':[df_table[(df_table['HomeTeam']==club)].HST.sum() + df_table[(df_table.AwayTeam == club)].AST.sum() for club in [club1, club2]],
            'Cartons Jaunes' : [df_table[(df_table['HomeTeam']==club)].HY.sum() + df_table[(df_table.AwayTeam == club)].AY.sum() for club in [club1, club2]],
            'Cartons Rouges' : [df_table[(df_table['HomeTeam']==club)].HR.sum() + df_table[(df_table.AwayTeam == club)].AR.sum() for club in [club1, club2]],
        }
        df_descr = pd.DataFrame(dic_descr, index=[club1, club2]).T
        df_descr[''] = df_descr.index
        data_descr = df_descr.to_dict('records')
        columns_descr=[{'name': col, 'id': col} for col in [club1,'', club2]]

        card_face_to_face = html.Div(
                    [
                        html.H1("Statistiques", className='card-title', style={"text-align":"center"}),
                        dash_table.DataTable(
                            data=data_descr,
                            columns=columns_descr,
                            style_cell={'textAlign': 'center'},
                            style_header={
                            'backgroundColor': 'rgb(230, 230, 230)',
                            'fontWeight': 'bold'
                            },
                            style_cell_conditional=[
                                {
                                    'if': {'column_id': ''},
                                    'fontWeight': 'bold'
                                }
                            ],
                            style_as_list_view=True,
                        ),
                    ]
                )

        #DATATABLE
        #df_table.drop(['FTHG', 'FTAG', 'HTHG', 'HTAG', 'Resultat', 'B365H', 'B365D', 'B365A', 'FT', 'HT'], axis=1, inplace=True)
        df_table.rename(columns={'HomeTeam':'Equipe à Domicile', 'AwayTeam':"Equipe à l'extérieur"}, inplace=True)
        df_table['sort'] = pd.to_datetime(df_table.Date, dayfirst=True)
        df_table.sort_values('sort', ascending=False, inplace=True)
        df_table.drop('sort', axis=1, inplace=True)
        df_table['Date'] = df_table.Date.apply(lambda x: dateutil.parser.parse(str(x), dayfirst=True).strftime("%A %d %B %Y"))
        #data_table = df_table.to_dict('records')
        #columns_table=[{'name': col, 'id': col} for col in ['Date', 'Equipe à Domicile', 'Score Final (mi-temps)', "Equipe à l'extérieur"]]
        titre=[html.Div([html.Br(),html.H2('Dernières confrontations', style={"text-align":"center"})])]
        div_confrontations=[html.Div(
            [
                html.Hr(),
                dbc.ListGroup([
                    dbc.ListGroupItem(dbc.Row(dbc.Col(html.P(row['Date']), width={"size": 4, "offset": 4}), align="left", style={"margin-left":"19mm"})),
                    dbc.Row([
                        dbc.Col(html.H4(row['Equipe à Domicile']), width={"size": 3, "offset": 2}, style={"margin-top":"4mm", "text-align":"right",}),
                        dbc.Col(html.Div(
                            [
                                html.P(row['FTHG'], className='bloc-score'),
                                html.Span(html.P("({})".format(row['HTHG'])), id='tooltip-mitempsH', style={"text-align":"center","cursor": "pointer"}),
                                dbc.Tooltip("Score à la mi-temps", target = 'tooltip-mitempsH', placement='left'),
                            ]), width={"size": 1, "offset": 0},),
                        dbc.Col(html.Div(
                            [
                                html.P(row['FTAG'], className='bloc-score'),
                                html.Span(html.P("({})".format(row['HTAG'])), id='tooltip-mitempsA', style={"text-align":"center", "cursor": "pointer"}),
                                dbc.Tooltip("Score à la mi-temps", target = 'tooltip-mitempsA', placement='right'),
                                ]), width={"size": 1, "offset": 0}),
                        dbc.Col(html.H4(row["Equipe à l'extérieur"]), width={"size": 3, "offset": 0}, style={"margin-top":"4mm", "text-align":"left",}),
                        ]
                    ),
                ]),
            ]
        )
         for index, row in df_table.head(3).iterrows()]
        
        collapse_confrontations=[html.Div(
            [
                html.Hr(),
                dbc.ListGroup([
                    dbc.ListGroupItem(dbc.Row(dbc.Col(html.P(row['Date']), width={"size": 4, "offset": 4}), align="left", style={"margin-left":"19mm"})),
                    dbc.Row([
                        dbc.Col(html.H4(row['Equipe à Domicile']), width={"size": 3, "offset": 2}, style={"margin-top":"4mm", "text-align":"right",}),
                        dbc.Col(html.Div(
                            [
                                html.P(row['FTHG'], className='bloc-score'),
                                html.Span(html.P("({})".format(row['HTHG'])), id='tooltip-mitempsH', style={"text-align":"center","cursor": "pointer"}),
                                dbc.Tooltip("Score à la mi-temps", target = 'tooltip-mitempsH', placement='left'),
                            ]), width={"size": 1, "offset": 0},),
                        dbc.Col(html.Div(
                            [
                                html.P(row['FTAG'], className='bloc-score'),
                                html.Span(html.P("({})".format(row['HTAG'])), id='tooltip-mitempsA', style={"text-align":"center", "cursor": "pointer"}),
                                dbc.Tooltip("Score à la mi-temps", target = 'tooltip-mitempsA', placement='right'),
                                ]), width={"size": 1, "offset": 0}),
                        dbc.Col(html.H4(row["Equipe à l'extérieur"]), width={"size": 3, "offset": 0}, style={"margin-top":"4mm", "text-align":"left",}),
                        ]
                    ),
                ]),
            ]
        )
         for index, row in df_table.tail(len(df_table)-3).iterrows()]
        
        display_collapse = {'display': 'block'}
        return progress_bar, "", card_face_to_face,titre+div_confrontations,collapse_confrontations, display_collapse



# Update page
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def display_page(pathname):
    if pathname == "/Stats-championnats":
        return stat_championnat_layout
    elif pathname == "/Stats-par-equipes":
        return stat_par_equipe_layout
    elif pathname == "/face-to-face":
        return face_a_face_layout    
    else:
        return home_layout

if __name__ == "__main__":
    app.run_server(debug=True)