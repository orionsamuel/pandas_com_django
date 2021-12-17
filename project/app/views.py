from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
import plotly.offline as py
import plotly.graph_objs as go
import numpy as np
import pandas as pd
import json
import re

# Create your views here.
df = pd.read_csv('app/static/data/netflix_titles.csv')
data = {}

#Template da Home
def home(request):
    df['country'] = df['country'].apply(replaceCountries)
    #data['dados'] = df[(df['release_year'] > 2009) & (df['country'] == 'Brasil')]\
    counter = 0
    list = []
    rows = len(df.index)

    while counter < rows:
        list.append("<a href='/detalhes/"+str(counter)+"'>Detalhes</a>")
        counter += 1
    df['links'] = list

    trace = go.Bar(
        x=df.sort_values(by='release_year')['release_year'].unique(),
        y=df.groupby('release_year')['title'].count()
    )
    datas=[trace]
    data['grafico']=py.plot(datas,output_type='div')
    """trace = go.Pie(
        labels=df['type'].unique(),
        values=df.groupby('type')['title'].count()
    )"""
    datas = [trace]
    data['grafico'] = py.plot(datas, output_type='div')

    data['dados']=df[['title','country','links']] \
        .dropna() \
        .head(20) \
        .to_html(render_links=True, escape=False, classes=['table', 'table-striped', 'mt-5'])
    data['countryFilter'] = df['country'].sort_values().unique()
    return render(request, 'index.html', data)

#Requisição para filtro de país
def countryFilter(request):
    if request.body:
        field = json.loads(request.body.decode('utf-8'))
        search = field['country']
        title = field['title']
        df2=df.dropna()
        data['dados']=df2[(df2['country'].str.contains(search))&(df2['title'].str.contains(title,flags=re.IGNORECASE))]\
        .to_html(index=False,classes=['table','table-striped','mt-5'])
        return JsonResponse({'data':data['dados']})

def detalhes(request,pk):
    data['pk']=pk
    data['dados']=df.iloc[pk].values
    return render(request, 'detalhes.html', data)

def replaceCountries(x):
    if(x == 'Brazil'):
        return x.replace('Brazil', 'Brasil')
    else:
        return x
