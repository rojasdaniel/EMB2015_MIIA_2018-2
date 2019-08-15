#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 11 18:20:27 2018

@author: danroj
"""

import pandas as pd
import pickle
import os
import numpy as np
import networkx as nx
import collections
import folium
import plotly.graph_objs as go
    
def abrir_base():
    os.chdir("D:/DashBoard")
    pkl_file = open('viajes_df.pkl', 'rb')
    viajes = pickle.load(pkl_file)
    pkl_file.close()
    filtros = viajes.MEDIO_PREDOMINANTE.unique()
    viajes["INICIO"] = viajes.apply(lambda row: row["HORA_INICIO"][0:2]+":00",axis=1)
    viajes["FIN"] = viajes.apply(lambda row: row["HORA_FIN"][0:2]+":00",axis=1)
    locations = viajes
    locations = locations.drop(locations[locations.ZAT_ORIGEN != locations.ZAT_HOGAR].index)
    locations = locations.groupby("ZAT_HOGAR").first()
    locations = locations.loc[:,["BARRIO","longitude_o", "ZAT_ORIGEN",
                                 "latitude_o"]]
    
    viajes['BARRIO_D'] = viajes['ZAT_DESTINO'].map(locations.set_index('ZAT_ORIGEN')['BARRIO'])
    viajes['BARRIO'] = viajes['ZAT_ORIGEN'].map(locations.set_index('ZAT_ORIGEN')['BARRIO'])
    viajes["FRANJA"] = np.where((viajes["INICIO"]>="00:00") & (viajes["INICIO"]<="05:00"), "Madrugada", "Hola")
    viajes["FRANJA"] = np.where((viajes["INICIO"]>="06:00") & (viajes["INICIO"]<="12:00"), "Mañana", viajes["FRANJA"])
    viajes["FRANJA"] = np.where((viajes["INICIO"]>="13:00") & (viajes["INICIO"]<="18:00"), "Tarde", viajes["FRANJA"])
    viajes["FRANJA"] = np.where((viajes["INICIO"]>="19:00") & (viajes["INICIO"]<="23:00"), "Noche", viajes["FRANJA"])
    
    return viajes, filtros
viajes, filtros = abrir_base()
edades = sorted(list(viajes.EDAD.unique()))
motivos = viajes.MOTIVOVIAJE.unique()
hora= viajes.FRANJA.unique() 
dia_habiles = viajes.DIA_HABIL.unique()
valle_habiles = viajes.VALLE_HABIL.unique()
dia = "S"
habil = "N"
estratos = sorted(list(viajes.ESTRATO.unique()))
edad= [20, 40]
horita =[hora[0], hora[2]]
motivo = [motivos[4]]
estrato = list(estratos)
filtro = filtros[2]
def filtracion(filtro, viajes, edad, motivo, estrato, dia, habil, horita):
    viajes = viajes.loc[viajes.MEDIO_PREDOMINANTE == filtro,]
    viajes = viajes.loc[viajes.MOTIVOVIAJE.isin(motivo)]
    viajes = viajes.loc[viajes.ESTRATO.isin(estrato)]
    e = str(edad[0])+" <= EDAD <= "+str(edad[1])
    viajes = viajes.query(e)
    viajes = viajes.loc[viajes.DIA_HABIL == dia,]
    viajes = viajes.loc[viajes.VALLE_HABIL == habil,]
    viajes = viajes.loc[viajes.FRANJA.isin(horita)]
    return viajes


def densidad(df):
    df = viajes.copy()
    df['ZAT_ORIGEN-ZAT_DESTINO'] = df['ZAT_ORIGEN'].astype(str) + "-" + df['ZAT_DESTINO'].astype(str)
    df = df[['ZAT_ORIGEN-ZAT_DESTINO']]
    df = df.groupby(['ZAT_ORIGEN-ZAT_DESTINO']).size().reset_index(name='CANT_VIAJES')
    df['ZAT_ORIGEN'], df['ZAT_DESTINO'] = df['ZAT_ORIGEN-ZAT_DESTINO'].str.split('-', 1).str
    G = nx.DiGraph() 
    for index, row in df.iterrows():
        G.add_edge(row["ZAT_ORIGEN"],row["ZAT_DESTINO"],weight=row["CANT_VIAJES"]) 
    all_weights = []
    for (node1,node2,data) in G.edges(data=True):
        all_weights.append(data['weight']) 
    unique_weights = list(set(all_weights))
    for weight in unique_weights:
        degree_sequence = sorted([d for n, d in G.degree()], reverse=True)  
    degreeCount = collections.Counter(degree_sequence)
    bd = list(degreeCount.items())
    bd = pd.DataFrame(bd)
    return G

def plot_station_counts(trip_counts):
    folium_map = folium.Map(location=[4.6471, -74.0906],
                            zoom_start=11,
                            tiles="CartoDB dark_matter")
    folium.TileLayer('openstreetmap').add_to(folium_map)
    for index, row in trip_counts.iterrows():


        popup_text = "Barrio: {} <br> Numero entradas: {}<br> Numero de salidas: {}<br> ZAT: {}"
        popup_text = popup_text.format(row["BARRIO"],
                          row["Arrival Count"],
                          row["Departure Count"],
                          row["ZAT_ORIGEN"])

        radius = max(row["Arrival Count"],row["Departure Count"])

        if radius==row["Arrival Count"]:

            color="#E37222" # tangerine

        else:
            color="#0A8A9F" # teal
        folium.CircleMarker(location=(row["longitude_o"],
                                      row["latitude_o"]),
                                      radius=radius,
                                      color=color,
                                      popup=popup_text,
                                      fill=True).add_to(folium_map)
        legend_html =   '''
                <div style="position: fixed; background-color: #FFFFFF;
                            bottom: 50px; left: 50px; width: 150px; height: 90px; 
                            border:2px solid grey; z-index:9999; font-size:14px;
                            ">&nbsp; Entradas:   &nbsp; <i class="fa fa-map-marker fa-2x" style="color:#E37222"></i><br>
                              &nbsp;  Salidas: &nbsp; <i class="fa fa-map-marker fa-2x" style="color:#0A8A9F"></i>
                </div>
                ''' 
        folium_map.get_root().html.add_child(folium.Element(legend_html))
    folium.LayerControl().add_to(folium_map)
    folium_map.save('mapa2.html')

def jugar_mapas(viajes, filtro, edad, motivo, estrato,dia, habil, horita):
    viajes = filtracion(filtro, viajes, edad, motivo, estrato,dia, habil, horita)
    df = viajes.copy()
    df=df[df['ZAT_ORIGEN']!=df['ZAT_DESTINO']]
    df['ZAT_ORIGEN-ZAT_DESTINO'] = df['ZAT_ORIGEN'].astype(str) + "-" + df['ZAT_DESTINO'].astype(str)
    df = df[['ZAT_ORIGEN-ZAT_DESTINO','ZAT_ORIGEN','ZAT_DESTINO','BARRIO','BARRIO_D','INICIO', 'longitude_o', 'latitude_o', 'longitude_d','latitude_d']]
    df = df.groupby(['ZAT_ORIGEN-ZAT_DESTINO', 'ZAT_ORIGEN','ZAT_DESTINO','BARRIO','BARRIO_D', 'INICIO', 'longitude_o', 'latitude_o', 'longitude_d','latitude_d']).size().reset_index(name='Cant_viajes')
    locations_o = df.groupby("ZAT_ORIGEN").first()
    locations_o = locations_o.loc[:,["BARRIO",
                              "longitude_o",
                              "latitude_o"]]
    locations_o["ZAT_ORIGEN"] = locations_o.index
    locations_d = df.groupby("ZAT_DESTINO").first()
    locations_d = locations_d.loc[:,["BARRIO_D"]]
    subset = df
    departure_counts =  subset.groupby("ZAT_ORIGEN").count()
    departure_counts = departure_counts.iloc[:,[8]]
    departure_counts.columns= ["Departure Count"]
    arrival_counts =  subset.groupby("ZAT_DESTINO").count().iloc[:,[8]]
    arrival_counts.columns= ["Arrival Count"]

    trip_counts = departure_counts.join(locations_o).join(arrival_counts).join(locations_d)
    trip_counts = trip_counts.drop([ "BARRIO_D"], axis=1)
    trip_counts = trip_counts.fillna(0)
    return plot_station_counts(trip_counts)
def update_mapas(viajes, filtro, edad, motivo, estrato,dia, habil, horita):
    jugar_mapas(viajes, filtro, edad, motivo, estrato,dia, habil, horita)
    return open('mapa2.html', 'r').read()

def abrir_jugarmapas():
    return update_mapas(viajes, filtro, edad, motivo, estrato,dia, habil, horita)
def tablero(filtro, viajes, edad, motivo, estrato,dia, habil, horita):
    viajes = filtracion(filtro, viajes, edad, motivo, estrato,dia, habil, horita)
    df = viajes.copy()
    df=df[df['ZAT_ORIGEN']!=df['ZAT_DESTINO']]
    df['ZAT_ORIGEN-ZAT_DESTINO'] = df['ZAT_ORIGEN'].astype(str) + "-" + df['ZAT_DESTINO'].astype(str)
    df = df[['ZAT_ORIGEN-ZAT_DESTINO','ZAT_ORIGEN','ZAT_DESTINO','BARRIO','BARRIO_D','INICIO', 'longitude_o', 'latitude_o', 'longitude_d','latitude_d']]
    df = df.groupby(['ZAT_ORIGEN-ZAT_DESTINO', 'ZAT_ORIGEN','ZAT_DESTINO','BARRIO','BARRIO_D', 'INICIO', 'longitude_o', 'latitude_o', 'longitude_d','latitude_d']).size().reset_index(name='Cant_viajes')
    locations_o = df.groupby("ZAT_ORIGEN").first()
    locations_o = locations_o.loc[:,["BARRIO",
                              "longitude_o",
                              "latitude_o"]]
    locations_o["ZAT_ORIGEN"] = locations_o.index
    locations_d = df.groupby("ZAT_DESTINO").first()
    locations_d = locations_d.loc[:,["BARRIO_D"]]
    subset = df
    departure_counts =  subset.groupby("ZAT_ORIGEN").count()
    departure_counts = departure_counts.iloc[:,[8]]
    departure_counts.columns= ["Departure Count"]
    arrival_counts =  subset.groupby("ZAT_DESTINO").count().iloc[:,[8]]
    arrival_counts.columns= ["Arrival Count"]
    trip_counts = departure_counts.join(locations_o).join(arrival_counts).join(locations_d)
    trip_counts = trip_counts.drop([ "BARRIO_D"], axis=1)
    trip_counts = trip_counts.fillna(0)
    trip_counts = trip_counts[["ZAT_ORIGEN", "BARRIO", "Arrival Count","Departure Count"]]
    trip_counts = trip_counts.rename(index=str, columns={"ZAT_ORIGEN":"ZAT", "Arrival Count": "Entradas", "Departure Count": "Salidas", "BARRIO":"Barrio"})
    return trip_counts
def tablero_final(filtro, viajes, edad, motivo, estrato,dia, habil, horita):
    viajes = filtracion(filtro, viajes, edad, motivo, estrato,dia, habil, horita)
    df = viajes.copy()
    df=df[df['ZAT_ORIGEN']!=df['ZAT_DESTINO']]
    df['ZAT_ORIGEN-ZAT_DESTINO'] = df['ZAT_ORIGEN'].astype(str) + "-" + df['ZAT_DESTINO'].astype(str)
    df = df[['ZAT_ORIGEN-ZAT_DESTINO','ZAT_ORIGEN','ZAT_DESTINO','BARRIO','BARRIO_D','INICIO', 'longitude_o', 'latitude_o', 'longitude_d','latitude_d']]
    df = df.groupby(['ZAT_ORIGEN-ZAT_DESTINO', 'ZAT_ORIGEN','ZAT_DESTINO','BARRIO','BARRIO_D', 'INICIO', 'longitude_o', 'latitude_o', 'longitude_d','latitude_d']).size().reset_index(name='Cant_viajes')
    G = densidad(df)
    trip_counts = tablero(filtro, viajes, edad, motivo, estrato,dia, habil, horita)
    trip_counts["Conexiones Totales"]=trip_counts["Entradas"]+trip_counts["Salidas"]

    bet_cen = nx.betweenness_centrality(G)
    bet_cen = pd.DataFrame(pd.Series(bet_cen).to_frame())
    bet_cen["ZAT"] = bet_cen.index
    bet_cen["ZAT"] = bet_cen["ZAT"].astype(int)
    bet_cen[0] = round(bet_cen[0],3)
    bet_cen = bet_cen.rename(index=str, columns={0:"Betweennes centrality"})
    trip_counts = pd.merge(trip_counts, bet_cen, on="ZAT")
    
    clo_cen = nx.closeness_centrality(G)
    clo_cen = pd.DataFrame(pd.Series(clo_cen).to_frame())
    clo_cen["ZAT"] = clo_cen.index
    clo_cen["ZAT"] = clo_cen["ZAT"].astype(int)
    clo_cen[0] = round(clo_cen[0],3)
    clo_cen = clo_cen.rename(index=str, columns={0:"Closeness centrality"})
    trip_counts = pd.merge(trip_counts, clo_cen, on="ZAT")

    eig_cen = nx.pagerank(G, alpha=0.9)
    eig_cen = pd.DataFrame(pd.Series(eig_cen).to_frame())
    eig_cen["ZAT"] = eig_cen.index
    eig_cen["ZAT"] = eig_cen["ZAT"].astype(int)
    eig_cen[0] = round(eig_cen[0],3)
    eig_cen = eig_cen.rename(index=str, columns={0:"PageRank"})
    trip_counts = pd.merge(trip_counts, eig_cen, on="ZAT")
    return trip_counts
def abrir_tablero():
    return tablero_final(filtro, viajes, edad, motivo, estrato,dia, habil, horita)
trip_counts=tablero_final(filtro, viajes, edad, motivo, estrato,dia, habil, horita)
def hist_hora(filtro, viajes, edad, motivo, estrato,dia, habil, horita):
    viajes = filtracion(filtro, viajes, edad, motivo, estrato,dia, habil, horita)
    layout = go.Layout(legend=dict(orientation="h"),
    title='Frecuencia total de viajes por hora',
    xaxis=dict(
        title='Hora',
        categoryorder = "category ascending"
    ),
    yaxis=dict(
        title='Frecuencia'
    ),
    bargap=0.2,
    bargroupgap=0.1
    )
    x = viajes['INICIO']
    x1 = viajes['FIN']
    data = [go.Histogram(x=x, name='Hora Inicio', marker=dict(color='#0A8A9F')),go.Histogram(x=x1, name='Hora Fin', marker=dict(color='#E37222'))]
    return go.Figure(data, layout=layout)
def abrirhist():
    return hist_hora(filtro, viajes, edad, motivo, estrato,dia, habil, horita)
def dens_hora(filtro, viajes, edad, motivo, estrato,dia, habil, horita):
    viajes = filtracion(filtro, viajes, edad, motivo, estrato,dia, habil, horita)
    layout = go.Layout(
    title='Top 25 de duración de recorrido del viaje',
    xaxis=dict(
        title='Hora',
        tickangle=90
    ),
    yaxis=dict(
        title='Frecuencia'
        
    ),
    bargap=0.2,
    bargroupgap=0.1
    )
    df = pd.value_counts(viajes['DIFERENCIA_HORAS']).to_frame().reset_index()
    df.columns = ['Col_value','Count']
    df = df.nlargest(25, 'Count')
 #   x = viajes['DIFERENCIA_HORAS']
    data = [go.Scatter(x=df.Col_value,y=df.Count,marker=dict(color='#11D753'))]
    return go.Figure(data, layout=layout)
def tviajes(filtro, viajes, edad, motivo, estrato,dia, habil, horita):
    viajes = filtracion(filtro, viajes, edad, motivo, estrato,dia, habil, horita)
    df = viajes.copy()
    df=viajes.groupby(['ZAT_ORIGEN','ZAT_DESTINO', 'DIFERENCIA_HORAS']).size().reset_index(name='Frecuencia de Viajes')
    df = df.rename(index=str, columns={"ZAT_ORIGEN":"ZAT Origen", "ZAT_DESTINO":"ZAT Destino", "DIFERENCIA_HORAS":"Diferencia de horas"})
    df = df.drop_duplicates(subset=["ZAT Origen", "ZAT Destino"])
    return df
top_viajes = tviajes(filtro, viajes, edad, motivo, estrato,dia, habil, horita)
def abrirdens():
    return dens_hora(filtro, viajes, edad, motivo, estrato,dia, habil, horita)
def powerlaws(filtro, viajes, edad, direccion, motivo, estrato,dia, habil, horita):
    xa = tablero(filtro, viajes, edad, motivo, estrato,dia, habil, horita)
    x = xa.index
    if direccion=="Entradas":
        titulo = "Distribución de grados de conexión de entrada"
        y = xa["Entradas"]
        color='#E37222'
        trazo2 = go.Bar( x = x, y = y, marker=go.bar.Marker(color=color), name = 'Destino')
        fig = { 'data': [trazo2],'layout': { 'title': titulo,'height': 420}}    
        return fig
    else:
        titulo="Distribución de grados de conexión de salida"
        y = xa["Salidas"]
        color='#0A8A9F'
        trazo2 = go.Bar( x = x, y = y, marker=go.bar.Marker(color=color), name = 'Destino')
        fig = { 'data': [trazo2],'layout': { 'title': titulo,'height': 420}}    
        return fig
def abrir_entrada():
    direccion="Entradas"
    return powerlaws(filtro, viajes, edad, direccion, motivo, estrato,dia, habil, horita)
def abrir_salida():
    direccion="Salidas"
    return powerlaws(filtro, viajes, edad, direccion, motivo, estrato,dia, habil, horita)
def crear_mapa(filtro, viajes, edad, motivo, estrato,dia, habil, horita, count):
    viajes = filtracion(filtro, viajes, edad, motivo, estrato,dia, habil, horita)
    df = viajes.copy()
    df=df[['ZAT_ORIGEN','ZAT_DESTINO', 'longitude_o', 'latitude_o', 'longitude_d', 'latitude_d']]
    if count.empty:
        mapa = folium.Map(location=[4.6471, -74.0906], tiles = "openstreetmap", zoom_start=11)
        folium.TileLayer('cartodbdark_matter').add_to(mapa)
    elif len(count)<=50:
        df = pd.merge(count, df,  how='inner', right_on=['ZAT_ORIGEN','ZAT_DESTINO'], left_on = ['ZAT Origen','ZAT Destino'])
        dp = pd.DataFrame(df[['ZAT_ORIGEN','ZAT_DESTINO', 'longitude_o', 'latitude_o', 'longitude_d','latitude_d', 'Frecuencia de Viajes']])
        dp = dp.drop_duplicates(['ZAT_ORIGEN', 'ZAT_DESTINO'], keep='first')
        dp['llave'] = list(zip(dp['ZAT_ORIGEN'], dp['ZAT_DESTINO']))
        dp['or'] = list(zip(dp['longitude_o'], dp['latitude_o']))
        dp['de'] = list(zip(dp['longitude_d'], dp['latitude_d']))
        dp['coords'] = list(zip(dp['or'], dp['de']))
        dp = dp[['llave', 'coords']]
        dp = dp.reset_index()
        dp = dp.set_index('llave').to_dict()
        dp = dp['coords']
        mapa = folium.Map(location=[4.6471, -74.0906], tiles = "openstreetmap", zoom_start=11)
        folium.TileLayer('cartodbdark_matter').add_to(mapa)
        for k,v in dp.items():
            popup1=str(k[0])
            popup2=str(k[1])
            popup = "Origen: {} <br> Destino: {}"
            popup = popup.format(popup1, popup2)
            icon_url="https://png.pngtree.com/svg/20170126/my_personal_page_center_area_28538.png"        
            icon = folium.features.CustomIcon(icon_url,icon_size=(38, 40))  
            folium.Marker(v[0],  popup=popup, icon=icon).add_to(mapa)
        for k,v in dp.items():
            tup = (k[1],k[0])
            if tup in dp.keys(): 
                popup1=str(k[0])
                popup2=str(k[1])
                popup = "Origen: {} <br> Destino: {}"
                popup = popup.format(popup1, popup2)
                icon_url="https://png.pngtree.com/svg/20170126/my_personal_page_center_area_28538.png"
                icon = folium.features.CustomIcon(icon_url,icon_size=(38, 40))  
                folium.Marker(v[0],  popup=popup, icon=icon).add_to(mapa)
            else:
                popup1=str(k[0])
                popup2=str(k[1])
                popup = "Origen: {} <br> Destino: {}"
                popup = popup.format(popup1, popup2)
                icon_url = 'https://cdn2.iconfinder.com/data/icons/flat-style-svg-icons-part-1/512/location_marker_pin-512.png'
                icon = folium.features.CustomIcon(icon_url,icon_size=(38, 40))  
                folium.Marker(v[1],  popup=popup, icon=icon).add_to(mapa)
        for k,v in dp.items():
            if k[1]==k[0]:
                next
            else:
                peso = (df.loc[(df['ZAT_ORIGEN'] == k[0]) & (df['ZAT_DESTINO'] == k[1]), 'Frecuencia de Viajes'])
                peso = np.mean(peso)
                folium.PolyLine((v[0],v[1]), color="green", popup=str(peso), weight=(peso),fill_opacity=1).add_to(mapa)
        for k,v in dp.items():
            tup = (k[1],k[0])
            if tup in dp.keys():
                if k[1]==k[0]:
                    next
                else:
                    peso = (df.loc[(df['ZAT_ORIGEN'] == k[0]) & (df['ZAT_DESTINO'] == k[1]), 'Frecuencia de Viajes'])
                    peso = np.mean(peso)
                    folium.PolyLine((v[0],v[1]), color="red", popup=str(peso), weight=(peso),fill_opacity=1).add_to(mapa)
            else:
                next
    else:
        next
    folium.LayerControl().add_to(mapa)
    mapa.save('mapa.html')
def abrir_mapa():
    count=pd.DataFrame()
    return update_mapa(filtro, viajes, edad, motivo, estrato,dia, habil, horita, count)
    

def update_mapa(filtro, viajes, edad, motivo, estrato,dia, habil, horita, count):
    crear_mapa(filtro, viajes, edad, motivo, estrato,dia, habil, horita, count)
    return open('mapa.html', 'r').read()

