from flask import Flask, jsonify, make_response, request
import pandas as pd

app = Flask(__name__)

CAMINHO_ARQUIVO = "Comparativo.xlsx"

# -----------------------------
# FUNÇÃO: carregar dados
# -----------------------------
def carregar_dados():
    df = pd.read_excel(CAMINHO_ARQUIVO)

    df.columns = (
        df.columns
        .str.strip()
        .str.upper()
        .str.replace('Ç', 'C')
        .str.replace('Ã', 'A')
        .str.replace('Á', 'A')
        .str.replace('É', 'E')
    )

    df['DATA'] = pd.to_datetime(df['DATA'], errors='coerce')
    df = df.dropna(subset=['DATA', 'VALOR'])

    return df


# -----------------------------
# FUNÇÃO: filtro de data
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
        print("Erro no filtro:", e)

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
# ROTA: DADOS
# -----------------------------
@app.route('/dados')
def dados():
    df = carregar_dados()
    df = aplicar_filtro_data(df)

    df['DATA'] = df['DATA'].astype(str)

    return resposta_sem_cache(df.to_dict(orient='records'))


# -----------------------------
# ROTA: FATURAMENTO DIÁRIO
# -----------------------------
@app.route('/faturamento-diario')
def faturamento_diario():
    df = carregar_dados()
    df = aplicar_filtro_data(df)

    df['DATA_DIA'] = df['DATA'].dt.date
    resultado = df.groupby('DATA_DIA')['VALOR'].sum().reset_index()

    return resposta_sem_cache(resultado.to_dict(orient='records'))


# -----------------------------
# ROTA: COMPATIBILIDADE (MENSAL)
# -----------------------------
@app.route('/faturamento-mensal')
def faturamento_mensal():
    df = carregar_dados()
    df = aplicar_filtro_data(df)

    df['MES'] = df['DATA'].dt.to_period('M').astype(str)
    resultado = df.groupby('MES')['VALOR'].sum().reset_index()

    return resposta_sem_cache(resultado.to_dict(orient='records'))


# -----------------------------
# ROTA: COMPARATIVO DIÁRIO
# -----------------------------
@app.route('/comparativo-diario')
def comparativo_diario():
    df = carregar_dados()
    df = aplicar_filtro_data(df)

    df['DATA_DIA'] = df['DATA'].dt.date

    resultado = df.groupby('DATA_DIA')['VALOR'].sum().reset_index()
    resultado = resultado.sort_values(by='DATA_DIA')

    resultado['VALOR_ANTERIOR'] = resultado['VALOR'].shift(1)

    resultado['VARIACAO'] = (
        (resultado['VALOR'] - resultado['VALOR_ANTERIOR']) /
        resultado['VALOR_ANTERIOR']
    ) * 100

    resultado = resultado.fillna(0)

    return resposta_sem_cache(resultado.to_dict(orient='records'))


# -----------------------------
# ROTA: FATURAMENTO CLIENTE
# -----------------------------
@app.route('/faturamento-cliente')
def faturamento_cliente():
    df = carregar_dados()
    df = aplicar_filtro_data(df)

    resultado = df.groupby('CLIENTE')['VALOR'].sum().reset_index()

    return resposta_sem_cache(resultado.to_dict(orient='records'))


# -----------------------------
# ROTA: CLASSIFICACAO
# -----------------------------
@app.route('/classificacao')
def classificacao():
    df = carregar_dados()
    df = aplicar_filtro_data(df)

    resultado = df.groupby('CLASSIFICACAO')['VALOR'].sum().reset_index()

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
        "faturamento_total": float(df['VALOR'].sum()) if not df.empty else 0,
        "media": float(df['VALOR'].mean()) if not df.empty else 0,
        "quantidade_registros": int(len(df)),
        "clientes_unicos": int(df['CLIENTE'].nunique()) if not df.empty else 0
    }

    return resposta_sem_cache(resultado)


# -----------------------------
# START
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True)