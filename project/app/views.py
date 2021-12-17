from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.core.paginator import Paginator
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
def home(request, page=None):
    df['country'] = df['country'].apply(replaceCountries)
    #data['dados'] = df[(df['release_year'] > 2009) & (df['country'] == 'Brasil')]\
    counter = 0
    list = []
    rows = len(df.index)

    # Botão de detalhes
    while (counter < rows):
        list.append("<a href='/detalhes/" + str(counter) + "'>Detalhes</a>")
        counter += 1
    df['links'] = list

    # Paginação
    registers = 10
    if ((page is None) | (page == 1)):
        page_number = 1
        start = 0
        end = registers
    else:
        page_number = int(page)
        start = registers * page_number - registers
        end = start + registers
    paginator = Paginator(df.dropna(), registers)
    data['paginator'] = paginator.get_page(page_number)

    # Plotagem de gráficos
    trace = go.Bar(
        x=df.sort_values(by='release_year')['release_year'].unique(),
        y=df.groupby('release_year')['title'].count()
    )
    datas = [trace]
    data['grafico'] = py.plot(datas, output_type='div')
    datas = [trace]
    data['grafico'] = py.plot(datas, output_type='div')

    # Exibição dos dados
    data['dados'] = df[['title', 'country', 'links']] \
                        .dropna() \
                        .iloc[start:end] \
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

        data['grafico']={
            'x':df2[(df2['country'].str.contains(search))&(df2['title'].str.contains(title,flags=re.IGNORECASE))].sort_values(by='release_year')['release_year'].unique().tolist(),
            'y':df2[(df2['country'].str.contains(search))&(df2['title'].str.contains(title,flags=re.IGNORECASE))].groupby('release_year')['title'].count().to_list()
        }

        data['dados']=df2[(df2['country'].str.contains(search))&(df2['title'].str.contains(title,flags=re.IGNORECASE))]\
        .to_html(index=False,classes=['table','table-striped','mt-5'])
        return JsonResponse({'data':data['dados'],'graph':data['grafico']})

def detalhes(request,pk):
    data['pk']=pk
    data['dados']=df.iloc[pk].values
    return render(request, 'detalhes.html', data)

def replaceCountries(x):
    if(x == 'Brazil'):
        return x.replace('Brazil', 'Brasil')
    else:
        return x
