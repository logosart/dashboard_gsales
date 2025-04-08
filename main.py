import pandas as pd
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px

# Carregar dados
df = pd.read_csv('vgsales.csv')

# Limpar e tratar dados
df.dropna(subset=['Year'], inplace=True)
df['Year'] = df['Year'].astype(int)

# Inicializar o aplicativo Dash
app = dash.Dash(__name__)
app.title = 'Painel de Vendas de Games'

# Layout da aplicação
app.layout = html.Div([
    html.H1("Painel de Vendas de Games", style={'textAlign': 'center'}),

    html.Div([
        html.Label("Plataforma:"),
        dcc.Dropdown(
            options=[{'label': plat, 'value': plat} for plat in sorted(df['Platform'].unique())],
            id='platform-filter',
            multi=True
        ),
    ], style={'width': '30%', 'display': 'inline-block'}),

    html.Div([
        html.Label("Gênero:"),
        dcc.Dropdown(
            options=[{'label': genre, 'value': genre} for genre in sorted(df['Genre'].unique())],
            id='genre-filter',
            multi=True
        ),
    ], style={'width': '30%', 'display': 'inline-block', 'marginLeft': '2%'}),

    html.Div([
        html.Label("Ano:"),
        dcc.Dropdown(
            options=[{'label': str(year), 'value': year} for year in sorted(df['Year'].unique())],
            id='year-filter',
            multi=True
        ),
    ], style={'width': '30%', 'display': 'inline-block', 'marginLeft': '2%'}),

    dcc.Graph(id='grafico-top-jogos'),

    dcc.Graph(id='grafico-vendas-regionais'),

    html.H3("Tabela de Jogos Filtrados"),
    dash_table.DataTable(
        id='tabela-filtrada',
        columns=[{"name": i, "id": i} for i in df.columns],
        page_size=10,
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left'},
    )
])

# Callback para atualizar os gráficos e a tabela com base nos filtros
@app.callback(
    [Output('grafico-top-jogos', 'figure'),
     Output('grafico-vendas-regionais', 'figure'),
     Output('tabela-filtrada', 'data')],
    [Input('platform-filter', 'value'),
     Input('genre-filter', 'value'),
     Input('year-filter', 'value')]
)
def atualizar_painel(plataformas, generos, anos):
    df_filtrado = df.copy()
    if plataformas:
        df_filtrado = df_filtrado[df_filtrado['Platform'].isin(plataformas)]
    if generos:
        df_filtrado = df_filtrado[df_filtrado['Genre'].isin(generos)]
    if anos:
        df_filtrado = df_filtrado[df_filtrado['Year'].isin(anos)]

    top_jogos = df_filtrado.nlargest(10, 'Global_Sales')

    grafico_barra = px.bar(
        top_jogos,
        x='Name',
        y='Global_Sales',
        color='Platform',
        title='Top 10 Jogos Mais Vendidos (Filtrados)',
        labels={'Global_Sales': 'Vendas Globais (milhões)'}
    )

    vendas_regionais = df_filtrado[['NA_Sales', 'EU_Sales', 'JP_Sales', 'Other_Sales']].sum()
    grafico_pizza = px.pie(
        names=vendas_regionais.index,
        values=vendas_regionais.values,
        title='Distribuição de Vendas por Região'
    )

    return grafico_barra, grafico_pizza, df_filtrado.to_dict('records')


# Rodar o servidor
if __name__ == '__main__':
    app.run(debug=True)
