from flask import Flask, jsonify, make_response, request
import pandas as pd

app = Flask(__name__)

# Caminho do arquivo (na mesma pasta do projeto)
CAMINHO_ARQUIVO = "Comparativo.xlsx"

# -----------------------------
# FUNÇÃO: carregar dados
# -----------------------------
def carregar_dados():
    df = pd.read_excel(CAMINHO_ARQUIVO)

    # Padronizar colunas
    df.columns = df.columns.str.upper()

    # Converter data
    df['DATA'] = pd.to_datetime(df['DATA'], errors='coerce')

    # Remover linhas inválidas
    df = df.dropna(subset=['DATA', 'VALOR'])

    return df


# -----------------------------
# FUNÇÃO: aplicar filtro de data
# -----------------------------
def aplicar_filtro_data(df):
    try:
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')

        if data_inicio:
            df = df[df['DATA'] >= pd.to_datetime(data_inicio)]

        if data_fim:
            df = df[df['DATA'] <= pd.to_datetime(data_fim)]

    except Exception as e:
        print("Erro no filtro de data:", e)

    return df


# -----------------------------
# FUNÇÃO: resposta sem cache
# -----------------------------
def resposta_sem_cache(data):
    response = make_response(jsonify(data))
    response.headers['Cache-Control'] = 'no-store'
    return response


# -----------------------------
# ROTA: HOME
# -----------------------------
@app.route('/')
def home():
    return "API Financeira rodando 🚀"


# -----------------------------
# ROTA: DADOS BRUTOS
# -----------------------------
@app.route('/dados')
def dados():
    df = carregar_dados()
    df = aplicar_filtro_data(df)

    df['DATA'] = df['DATA'].astype(str)

    return resposta_sem_cache(df.to_dict(orient='records'))


# -----------------------------
# ROTA: FATURAMENTO MENSAL
# -----------------------------
@app.route('/faturamento-mensal')
def faturamento_mensal():
    df = carregar_dados()
    df = aplicar_filtro_data(df)

    df['MES'] = df['DATA'].dt.to_period('M').astype(str)
    resultado = df.groupby('MES')['VALOR'].sum().reset_index()

    return resposta_sem_cache(resultado.to_dict(orient='records'))


# -----------------------------
# ROTA: FATURAMENTO POR CLIENTE
# -----------------------------
@app.route('/faturamento-cliente')
def faturamento_cliente():
    df = carregar_dados()
    df = aplicar_filtro_data(df)

    resultado = df.groupby('CLIENTE')['VALOR'].sum().reset_index()

    return resposta_sem_cache(resultado.to_dict(orient='records'))


# -----------------------------
# ROTA: CLASSIFICAÇÃO
# -----------------------------
@app.route('/classificacao')
def classificacao():
    df = carregar_dados()
    df = aplicar_filtro_data(df)

    resultado = df.groupby('CLASSIFICAÇÃO')['VALOR'].sum().reset_index()

    return resposta_sem_cache(resultado.to_dict(orient='records'))


# -----------------------------
# ROTA: TOP CLIENTES
# -----------------------------
@app.route('/top-clientes')
def top_clientes():
    df = carregar_dados()
    df = aplicar_filtro_data(df)

    resultado = (
        df.groupby('CLIENTE')['VALOR']
        .sum()
        .reset_index()
        .sort_values(by='VALOR', ascending=False)
        .head(10)
    )

    return resposta_sem_cache(resultado.to_dict(orient='records'))


# -----------------------------
# ROTA: INDICADORES
# -----------------------------
@app.route('/indicadores')
def indicadores():
    df = carregar_dados()
    df = aplicar_filtro_data(df)

    resultado = {
        "faturamento_total": float(df['VALOR'].sum()),
        "media": float(df['VALOR'].mean()),
        "quantidade_registros": int(len(df)),
        "clientes_unicos": int(df['CLIENTE'].nunique())
    }

    return resposta_sem_cache(resultado)


# -----------------------------
# START APP
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True)