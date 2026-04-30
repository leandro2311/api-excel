from flask import Flask, jsonify, make_response
import pandas as pd

app = Flask(__name__)

# Caminho do arquivo
CAMINHO_ARQUIVO = r"C:\Users\Leandro\Documents\python-projetos\Comparativo.xlsx"

# Função base para carregar e tratar dados
def carregar_dados():
    df = pd.read_excel(CAMINHO_ARQUIVO)

    # Padronizar nomes das colunas
    df.columns = df.columns.str.upper()

    # Converter data
    df['DATA'] = pd.to_datetime(df['DATA'], errors='coerce')

    # Remover linhas inválidas
    df = df.dropna(subset=['DATA', 'VALOR'])

    return df

# Função para evitar cache
def resposta_sem_cache(data):
    response = make_response(jsonify(data))
    response.headers['Cache-Control'] = 'no-store'
    return response

# 🔹 Rota inicial
@app.route('/')
def home():
    return "API Financeira 🚀 - endpoints: /dados, /faturamento-mensal, /faturamento-cliente, /classificacao, /top-clientes, /indicadores"

# 🔹 Dados brutos
@app.route('/dados')
def dados():
    df = carregar_dados()
    df['DATA'] = df['DATA'].astype(str)

    return resposta_sem_cache(df.to_dict(orient='records'))

# 🔹 Faturamento por mês
@app.route('/faturamento-mensal')
def faturamento_mensal():
    df = carregar_dados()

    df['MES'] = df['DATA'].dt.to_period('M').astype(str)
    resultado = df.groupby('MES')['VALOR'].sum().reset_index()

    return resposta_sem_cache(resultado.to_dict(orient='records'))

# 🔹 Faturamento por cliente
@app.route('/faturamento-cliente')
def faturamento_cliente():
    df = carregar_dados()

    resultado = df.groupby('CLIENTE')['VALOR'].sum().reset_index()

    return resposta_sem_cache(resultado.to_dict(orient='records'))

# 🔹 Faturamento por classificação
@app.route('/classificacao')
def classificacao():
    df = carregar_dados()

    resultado = df.groupby('CLASSIFICAÇÃO')['VALOR'].sum().reset_index()

    return resposta_sem_cache(resultado.to_dict(orient='records'))

# 🔹 Top clientes
@app.route('/top-clientes')
def top_clientes():
    df = carregar_dados()

    resultado = (
        df.groupby('CLIENTE')['VALOR']
        .sum()
        .reset_index()
        .sort_values(by='VALOR', ascending=False)
        .head(10)
    )

    return resposta_sem_cache(resultado.to_dict(orient='records'))

# 🔹 Indicadores gerais
@app.route('/indicadores')
def indicadores():
    df = carregar_dados()

    total = df['VALOR'].sum()
    media = df['VALOR'].mean()
    quantidade = len(df)
    clientes = df['CLIENTE'].nunique()

    resultado = {
        "faturamento_total": total,
        "media": media,
        "quantidade_registros": quantidade,
        "clientes_unicos": clientes
    }

    return resposta_sem_cache(resultado)

# Rodar servidor
if __name__ == '__main__':
    app.run(debug=True)