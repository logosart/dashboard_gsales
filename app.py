import pandas as pd
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import os 





# Planilha
df = pd.read_csv('vgsales.csv')

# Limpar e tratar dados
df.dropna(subset=['Year'], inplace=True)
df['Year'] = df['Year'].astype(int)

# Top 10 jogos mais vendidos de todos os tempos (sem filtro)
top_vendas_geral = df.nlargest(10, 'Global_Sales')

# App
app = dash.Dash(__name__)
app.title = 'Painel de Vendas de Games'

# Layout com estilo
app.layout = html.Div(style={'fontFamily': 'Arial, sans-serif', 'padding': '20px', 'backgroundColor': '#f9f9f9'}, children=[
    html.H1("Painel de Vendas de Games", style={'textAlign': 'center', 'color': '#333'}),

    html.Div([
        html.Div([
            html.Label("Plataforma:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                options=[{'label': plat, 'value': plat} for plat in sorted(df['Platform'].unique())],
                id='platform-filter',
                multi=True,
                placeholder="Selecione plataforma(s)"
            ),
        ], style={'width': '32%', 'display': 'inline-block', 'paddingRight': '1%'}),

        html.Div([
            html.Label("Gênero:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                options=[{'label': genre, 'value': genre} for genre in sorted(df['Genre'].unique())],
                id='genre-filter',
                multi=True,
                placeholder="Selecione gênero(s)"
            ),
        ], style={'width': '32%', 'display': 'inline-block', 'paddingRight': '1%'}),

        html.Div([
            html.Label("Ano:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                options=[{'label': str(year), 'value': year} for year in sorted(df['Year'].unique())],
                id='year-filter',
                multi=True,
                placeholder="Selecione ano(s)"
            ),
        ], style={'width': '32%', 'display': 'inline-block'}),
    ], style={'marginBottom': '30px'}),

    dcc.Graph(id='grafico-top-jogos', style={'marginBottom': '40px'}),

    dcc.Graph(id='grafico-vendas-regionais', style={'marginBottom': '40px'}),

    html.H3("Tabela de Jogos Filtrados", style={'color': '#333'}),
    dash_table.DataTable(
    id='tabela-filtrada',
    columns=[{"name": i, "id": i} for i in df.columns],
    page_size=10,
    filter_action='native',  # <- Aqui está a mágica!
    style_table={'overflowX': 'auto', 'border': '1px solid #ccc'},
    style_cell={
        'textAlign': 'left',
        'padding': '8px',
        'backgroundColor': 'white',
        'color': '#333',
        'fontSize': '14px',
    },
    style_header={
        'backgroundColor': '#f2f2f2',
        'fontWeight': 'bold'
    },
    style_data_conditional=[
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': '#fafafa'
        }
    ]
)
,

    html.H3("Top 10 Jogos Mais Vendidos de Todos os Tempos", style={'marginTop': '50px', 'color': '#333'}),
    dash_table.DataTable(
        id='tabela-top-geral',
        columns=[{"name": i, "id": i} for i in top_vendas_geral.columns],
        data=top_vendas_geral.to_dict('records'),
        page_size=10,
        style_table={'overflowX': 'auto', 'border': '1px solid #ccc'},
        style_cell={
            'textAlign': 'left',
            'padding': '8px',
            'backgroundColor': 'white',
            'color': '#333',
            'fontSize': '14px',
        },
        style_header={
            'backgroundColor': '#f2f2f2',
            'fontWeight': 'bold'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': '#fafafa'
            }
        ]
    )
])

# Callback
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


# Rodar servidor
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))
    app.run(host="0.0.0.0", port=port, debug=False)
