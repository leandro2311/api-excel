import pandas as pd

# Lê o arquivo Excel
df = pd.read_excel("Comparativo.xlsx")

# Mostra as primeiras linhas
print(df.head())
print(df.columns)