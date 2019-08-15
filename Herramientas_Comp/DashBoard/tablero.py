import pandas as pd
import os
os.chdir("D:/DashBoard")
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from Funciones import *
import plotly.graph_objs as go
import dash_table_experiments as dt

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config.supress_callback_exceptions=True
app.layout = html.Div([ html.Div([
                            html.Div([
                                html.Img(src="assets/logo.png", style={'height': '100px', 'float':'center'})
                                ], className="six columns", style = {'display': 'inline-block', 'width': '0.4%', 'align':'left'}),
                            html.Div([
                                html.H1('Encuesta de Movilidad de Bogotá 2015', style={'textAlign': 'center'})
                                ], className="six columns", style = {'display': 'inline-block', 'width': '92%', 'align':'center'})
                            ], className="row"),
                        #_________________________________________________________________________________________
                        html.Div([
                            html.Div([
                                html.H5('Medio de transporte:', style={'textAlign': 'center'})
                                ], style = {'display': 'inline-block', 'width': '100%', 'align':'center'} ),
                            html.Div([
                                dcc.Dropdown(
                                            id='filtro',
                                            options=[{'label': i, 'value': i} for i in filtros],
                                            value=filtro
                                            )
                                ], style = {'display': 'inline-block', 'width': '100%', 'align':'center'})
                            ], style = {'display': 'inline-block', 'width': '20%', 'align':'center'}),
                        #_________________________________________________________________________________________
                        html.Div([
                            html.Div([
                                html.H5('Motivo de viaje:', style={'textAlign': 'center'})
                                ], style = {'display': 'inline-block', 'width': '100%', 'align':'center'} ),
                            html.Div([
                                dcc.Dropdown(
                                            id='motivo',
                                            options=[{'label': i, 'value': i} for i in motivos],
                                            multi=True,
                                            value=motivo
                                            )
                                ], style = {'display': 'inline-block', 'width': '100%', 'align':'center'})
                            ], style = {'display': 'inline-block', 'width': '20%', 'align':'center'}),
                        #_________________________________________________________________________________________
                        html.Div([
                            html.Div([
                                html.H5('Estrato:', style={'textAlign': 'center'})
                                ], style = {'display': 'inline-block', 'width': '100%', 'align':'center'}),
                            html.Div([
                                dcc.Dropdown(
                                            id='estrato',
                                            options=[{'label': i, 'value': i} for i in estratos],
                                            multi=True,
                                            value=estrato
                                            )
                                ], style = {'display': 'inline-block', 'width': '100%', 'align':'center'})
                            ], style = {'display': 'inline-block', 'width': '20%', 'align':'center'}),
                        #_________________________________________________________________________________________
                        html.Div([
                            html.Div([
                                html.H5('Hora Valle:', style={'textAlign': 'center'})
                                ], style = {'display': 'inline-block', 'width': '100%', 'align':'center'} ),
                            html.Div([
                                dcc.Dropdown(
                                            id='habil',
                                            options=[{'label': i, 'value': i} for i in ["S", "N"]],
                                            value="N"
                                            )
                                ], style = {'display': 'inline-block', 'width': '100%', 'align':'left'})
                            ], style = {'display': 'inline-block', 'width': '20%', 'align':'center'}),
                        #_________________________________________________________________________________________
                        html.Div([
                            html.Div([
                                html.H5('Día habil:', style={'textAlign': 'center'})
                                ], style = {'display': 'inline-block', 'width': '100%', 'align':'center'} ),
                            html.Div([
                                dcc.Dropdown(
                                            id='dia',
                                            options=[{'label': i, 'value': i} for i in ["S", "N"]],
                                            value="S"
                                            )
                                ], style = {'display': 'inline-block', 'width': '100%', 'align':'left'})
                            ], style = {'display': 'inline-block', 'width': '20%', 'align':'center'}),
                        #_________________________________________________________________________________________
                        html.Div([
                            html.H5('Edad:', style={'textAlign': 'center'})
                            ], style = {'display': 'inline-block', 'width': '100%', 'align':'center'} ),
                        html.Div([
                            dcc.RangeSlider(
                                        id='edad',
                                        marks={i*5: i*5 for i in range(20)},
                                        min=min(edades),
                                        max=max(edades)+1,
                                        value=edad
                                        )
                            ], style = {'display': 'inline-block', 'width': '100%', 'align':'center'} ),
                        #_________________________________________________________________________________________
                        html.Hr(),
                        #_________________________________________________________________________________________
                        html.Div([
                            html.Div([
                                html.H5('Franja de inicio de viaje:', style={'textAlign': 'center'})
                                ], style = {'display': 'inline-block', 'width': '100%', 'align':'center'}),
                            html.Div([
                                dcc.Dropdown(
                                            id='horita',
                                            options=[{'label': i, 'value': i} for i in hora],
                                            multi=True,
                                            value=horita
                                            )
                                ], style = {'display': 'inline-block', 'width': '100%', 'align':'center'})
                            ], style = {'display': 'inline-block', 'width': '100%', 'align':'center'}),
                        #_________________________________________________________________________________________
                        html.Div([
                        html.Div([
                            html.H5('Radio de frecuencia de viajes Origen-Destino', style={'textAlign': 'center'})
                            ], style = {'display': 'inline-block', 'width': '100%', 'align':'center'} ),
                        html.Div([
                            html.Iframe(
                                id= 'mapita', srcDoc = abrir_jugarmapas(), width='100%', height='500')], 
                                style = {'display': 'inline-block', 'width': '100%', 'align':'center'})], 
                                style = {'display': 'inline-block', 'width': '100%', 'align':'center'} ), 
                        #_____________________________________________________________________________________________
                        html.Hr(),
                        #_____________________________________________________________________________________________
                        html.Div([
                            html.Div([
                                dcc.Graph(
                                    id= 'power_law1', figure = abrir_entrada()
                                    )
                                ], style = {'display': 'inline-block', 'width': '50%', 'align':'center'} ),
                            #_________________________________________________________________________________________
                            html.Div([
                                dcc.Graph(
                                    id= 'power_law2', figure = abrir_salida()
                                    )
                                ], style = {'display': 'inline-block', 'width': '50%', 'align':'center'} )
                        ],style = {'display': 'inline-block', 'width': '100%', 'align':'center'}  ),
                        #_____________________________________________________________________________________________
                        html.Hr(),
                        #_____________________________________________________________________________________________
                        html.Div([
                            html.Div([
                                dcc.Graph(id="dens", figure=abrirdens())
                                ],style={'display': 'inline-block', 'width': '50%', 'align':'center'}),
                        #_____________________________________________________________________________________________
                            html.Div([
                                dcc.Graph(id="histogram", figure=abrirhist())
                                ],style={'display': 'inline-block', 'width': '50%', 'align':'center'}),
                        ], style={'display': 'inline-block', 'width': '100%', 'align':'center'}),
                        #_____________________________________________________________________________________________
                        html.Hr(),
                        #_____________________________________________________________________________________________
                        html.Div([
                            html.Div([
                            html.Iframe(
                                id= 'mapa2', srcDoc = abrir_mapa(), width='100%', height='475')], 
                                style = {'display': 'inline-block', 'width': '45%', 'align':'center'}),
                        #_____________________________________________________________________________________________
                            html.Div([html.Hr()],style = {'display': 'inline-block', 'width': '5%', 'align':'center'}),
                        #_____________________________________________________________________________________________
                            html.Div(
                                dt.DataTable(rows=top_viajes.to_dict('records'),
                                columns=top_viajes.columns,
                                row_selectable=True,
                                filterable=True,
                                sortable=True,
                                selected_row_indices=[],
                                id='horitas'),
                                style={'display': 'inline-block', 'width': '50%', 'align':'center'})
                        ], style={'display': 'inline-block', 'width': '100%', 'align':'center'}),
                        #_____________________________________________________________________________________________
                            html.Div(
                                dt.DataTable(rows=trip_counts.to_dict('records'),
                                columns=trip_counts.columns,
                                row_selectable=False,
                                filterable=True,
                                sortable=True,
                                selected_row_indices=[],
                                id='datatable'),
                                style={'display': 'inline-block', 'width': '100%', 'align':'center'}),
                        #_____________________________________________________________________________________________
                        html.Hr(),
                        #_____________________________________________________________________________________________
                        html.Div( [ html.H6('Desarrolado por: Ana Milena Rodriguez - Nicolas Hernandez - Luis Francisco Ortiz - Daniel Rojas', style={'textAlign': 'center'})])
                        #_________________________________________________________________________________________
                        ], style = {'width': '99%', 'align':'center'} )
@app.callback(
    dash.dependencies.Output(component_id='mapa2', component_property='srcDoc'),
    [dash.dependencies.Input(component_id='filtro', component_property='value'),
    dash.dependencies.Input(component_id='edad', component_property='value'),
    dash.dependencies.Input(component_id='motivo', component_property='value'),
    dash.dependencies.Input(component_id='estrato', component_property='value'),
    dash.dependencies.Input(component_id='dia', component_property='value'),
    dash.dependencies.Input(component_id='habil', component_property='value'),
    dash.dependencies.Input(component_id='horita', component_property='value'),
    dash.dependencies.Input(component_id='horitas', component_property='rows'),
    dash.dependencies.Input(component_id='horitas', component_property='selected_row_indices')])
def tablerito(filtro, edad, motivo, estrato, dia, habil, horita, rows, selected_row_indices):
    count = pd.DataFrame(rows) 
    if selected_row_indices:
        count = count.loc[selected_row_indices] 
    return update_mapa(filtro, viajes, edad, motivo, estrato,dia, habil, horita, count)
@app.callback(
    dash.dependencies.Output(component_id='horitas', component_property='rows'),
    [dash.dependencies.Input(component_id='filtro', component_property='value'),
    dash.dependencies.Input(component_id='edad', component_property='value'),
    dash.dependencies.Input(component_id='motivo', component_property='value'),
    dash.dependencies.Input(component_id='estrato', component_property='value'),
    dash.dependencies.Input(component_id='dia', component_property='value'),
    dash.dependencies.Input(component_id='habil', component_property='value'),
    dash.dependencies.Input(component_id='horita', component_property='value')])
def tablerito(filtro, edad, motivo, estrato, dia, habil, horita):
    top_viajes= tviajes(filtro, viajes, edad, motivo, estrato,dia, habil, horita)
    rows = top_viajes.to_dict('records')
    return rows
@app.callback(
    dash.dependencies.Output(component_id='datatable', component_property='rows'),
    [dash.dependencies.Input(component_id='filtro', component_property='value'),
    dash.dependencies.Input(component_id='edad', component_property='value'),
    dash.dependencies.Input(component_id='motivo', component_property='value'),
    dash.dependencies.Input(component_id='estrato', component_property='value'),
    dash.dependencies.Input(component_id='dia', component_property='value'),
    dash.dependencies.Input(component_id='habil', component_property='value'),
    dash.dependencies.Input(component_id='horita', component_property='value')])
def tablerito(filtro, edad, motivo, estrato, dia, habil, horita):
    trip_counts= tablero_final(filtro, viajes, edad, motivo, estrato,dia, habil, horita)
    rows = trip_counts.to_dict('records')
    return rows
@app.callback(
    dash.dependencies.Output(component_id='histogram', component_property='figure'),
    [dash.dependencies.Input(component_id='filtro', component_property='value'),
    dash.dependencies.Input(component_id='edad', component_property='value'),
    dash.dependencies.Input(component_id='motivo', component_property='value'),
    dash.dependencies.Input(component_id='estrato', component_property='value'),
    dash.dependencies.Input(component_id='dia', component_property='value'),
    dash.dependencies.Input(component_id='habil', component_property='value'),
    dash.dependencies.Input(component_id='horita', component_property='value')])
def histog(filtro, edad, motivo, estrato, dia, habil, horita):
    return hist_hora(filtro, viajes, edad, motivo, estrato,dia, habil, horita)
@app.callback(
    dash.dependencies.Output(component_id='dens', component_property='figure'),
    [dash.dependencies.Input(component_id='filtro', component_property='value'),
    dash.dependencies.Input(component_id='edad', component_property='value'),
    dash.dependencies.Input(component_id='motivo', component_property='value'),
    dash.dependencies.Input(component_id='estrato', component_property='value'),
    dash.dependencies.Input(component_id='dia', component_property='value'),
    dash.dependencies.Input(component_id='habil', component_property='value'),
    dash.dependencies.Input(component_id='horita', component_property='value')])
def histog(filtro, edad, motivo, estrato, dia, habil, horita):
    return dens_hora(filtro, viajes, edad, motivo, estrato,dia, habil, horita)
@app.callback(
    dash.dependencies.Output(component_id='power_law1', component_property='figure'),
    [dash.dependencies.Input(component_id='filtro', component_property='value'),
    dash.dependencies.Input(component_id='edad', component_property='value'),
    dash.dependencies.Input(component_id='motivo', component_property='value'),
    dash.dependencies.Input(component_id='estrato', component_property='value'),
    dash.dependencies.Input(component_id='dia', component_property='value'),
    dash.dependencies.Input(component_id='habil', component_property='value'),
    dash.dependencies.Input(component_id='horita', component_property='value')])
def update_PW(filtro, edad, motivo, estrato, dia, habil, horita):
    direccion="Entradas"
    fig = powerlaws(filtro, viajes, edad, direccion, motivo, estrato,dia, habil, horita)
    return fig
@app.callback(
    dash.dependencies.Output(component_id='power_law2', component_property='figure'),
    [dash.dependencies.Input(component_id='filtro', component_property='value'),
    dash.dependencies.Input(component_id='edad', component_property='value'),
    dash.dependencies.Input(component_id='motivo', component_property='value'),
    dash.dependencies.Input(component_id='estrato', component_property='value'),
    dash.dependencies.Input(component_id='dia', component_property='value'),
    dash.dependencies.Input(component_id='habil', component_property='value'),
    dash.dependencies.Input(component_id='horita', component_property='value')])
def update_PW(filtro, edad, motivo, estrato, dia, habil, horita):
    direccion="Salidas"
    fig = powerlaws(filtro, viajes, edad, direccion, motivo, estrato,dia, habil, horita)
    return fig
@app.callback(
    dash.dependencies.Output(component_id='mapita', component_property='srcDoc'),
    [dash.dependencies.Input(component_id='filtro', component_property='value'),
    dash.dependencies.Input(component_id='edad', component_property='value'),
    dash.dependencies.Input(component_id='motivo', component_property='value'),
    dash.dependencies.Input(component_id='estrato', component_property='value'),
    dash.dependencies.Input(component_id='dia', component_property='value'),
    dash.dependencies.Input(component_id='habil', component_property='value'),
    dash.dependencies.Input(component_id='horita', component_property='value')])
def update_distribution2(filtro, edad, motivo, estrato, dia, habil,horita):
    fig = update_mapas(viajes, filtro, edad, motivo, estrato,dia, habil, horita)
    return fig
app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})
if __name__ == '__main__':
    app.run_server(debug = True)
