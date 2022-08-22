# Carregando pacotes necessários

import geobr # Para visualização georeferenciada. Shapefiles do Brasil. ipeagit.github.io/geobr/articles/python-intro/py-intro-to-geobr.html
from matplotlib import use as m_use
m_use('TkAgg')
import matplotlib.pyplot as plt
import basedosdados as bd
import pandas as pd
import numpy as np

# Baixando a base de dados
# Juntando com informações de populaçao
df = bd.read_sql(
    '''
    SELECT ano, sigla_uf AS State, id_municipio, producao_cafe AS CoffeeProduction, area_cafe AS CoffeeArea,
    valor_total_producao_cafe AS CoffeeProdValue, Population
    FROM basedosdados.br_ibge_censo_agropecuario.municipio AS cagro
    LEFT JOIN (SELECT id_municipio as muni, populacao as Population, ano as year
    FROM basedosdados.br_ibge_populacao.municipio) as pop
    ON (cagro.id_municipio = pop.muni AND cagro.ano = pop.year)
    ''',
    billing_project_id='coffeebr'
)

df.info() # Entendendo a base, formatos...
#idMunicipio e state precisam ser transformados...

df['id_municipio'] = df['id_municipio'].astype('float64')
df['State'] = df['State'].astype('str')
df['Prodpercapita'] = (df['CoffeeProduction'].fillna(0) / (df['Population'])).astype('float64') # Produção per capita

muni = geobr.read_municipality(code_muni='all', year=2010) # Shapefiles de municípios
state = geobr.read_state(code_state='all', year=2010) # Shapefiles de estados

# Shapefiles + Dados
joined = muni.merge(df[['Prodpercapita', 'id_municipio', 'ano', 'State']], how = 'left', right_on='id_municipio', left_on='code_muni')

import matplotlib.colors as mplc # para corrigir assimetria da distribuição dos valores

filt = joined[(joined['ano'] == 2017) & (joined['State'].isin(['ES', 'RJ', 'MG', 'SP']))].fillna(0) # Dados e Shapefiles apenas do SE

fig, ax = plt.subplots(figsize=(35, 25), dpi=200)

plt.ylim([-25.5, -14])
plt.xlim([-54, -39])

state.plot(facecolor = '#cfcfcf', edgecolor="black", ax=ax, linewidth=1) # Camada de fundo (estados não-SE)
ax.set_facecolor("#9dbdcc") # Mar

filt.plot(# Camada principal: municípios coloridos de acordo com prod per capita
    edgecolor=None,
    norm=mplc.PowerNorm(gamma=0.25, vmin = 0, vmax=max(filt['Prodpercapita'])), #parâmetro gamma para contornar assimetria da distribuição
    column='Prodpercapita',
    cmap=mplc.LinearSegmentedColormap.from_list('brrown', ['#E6D2AA','#42032C'], N=256), #escala de cores
    legend=True,
    legend_kwds={
        "orientation": "vertical",
        "shrink": 0.6,
    },
    ax=ax,
)

state.plot(facecolor = 'none', edgecolor="black", ax=ax, linewidth=1) # Contornos dos limites territoriais

ax.set_title("Per capita coffee production in Brazilian Southeast", fontsize=48, loc='left', color = '#42032C')
plt.figtext(0.9, 0.1,
            "Johann Freitas\nData: Brazilian Institute of Geography and Statistics",
            wrap=True, horizontalalignment='right', fontsize=32, color = '#42032C')
ax.set_xticklabels([])
ax.set_yticklabels([])
ax.set_xticks([])
ax.set_yticks([])
ax.figure.axes[1].tick_params(labelsize=32)
ax.figure.axes[1].set_ylabel("Per capita coffee production (Tons)", fontsize=32)

plt.savefig('brown_coffee_pc.png')