# gera_pop_rain.py
import pandas as pd
import sys
import math

# ------------------------------------------------------
# COMO USAR:
# python gera_pop_rain.py "Curitiba,BR"
# ------------------------------------------------------

arquivo = "weather.csv"

# Verifica se o usuário passou a cidade
if len(sys.argv) < 2:
    print("❌ Uso correto:")
    print("   python gera_pop_rain.py \"Curitiba,BR\"")
    sys.exit(1)

cidade = sys.argv[1].strip()

# Lê o CSV
try:
    df = pd.read_csv(arquivo)
except FileNotFoundError:
    sys.exit(f"❌ Arquivo {arquivo} não encontrado. Gere-o primeiro com busca_clima.py.")

if "city_query" not in df.columns:
    sys.exit("❌ O arquivo CSV não contém a coluna 'city_query' esperada.")

# Filtra cidade
df_cidade = df[df["city_query"].str.strip().str.lower() == cidade.lower()]
if df_cidade.empty:
    sys.exit(f"⚠️ Nenhum dado encontrado para {cidade}. Verifique o nome exatamente como aparece no weather.csv.")

# Exibe últimas 5 linhas
print(f"\n📍 Cidade selecionada: {cidade}")
print("🧾 Últimas 5 linhas encontradas:\n")
print(df_cidade.tail(5)[["ts", "temp_c", "humidity", "rain_3h", "pop", "weather_desc"]])

# Pega a linha mais recente
linha = df_cidade.iloc[-1]

# Extrai valores
pop = linha.get("pop", 0)
rain = linha.get("rain_3h", 0)

# Converte e trata
try:
    pop = float(pop) * 100 if float(pop) < 1 else float(pop)
except:
    pop = 0.0

try:
    rain = float(rain)
    if math.isnan(rain):
        rain = 0.0
except:
    rain = 0.0

# Interpretação
if pop >= 60 or rain >= 1.0:
    situacao = "💧 Condição de chuva detectada → bomba deve ser DESLIGADA (OFF)."
else:
    situacao = "☀️ Clima seco → irrigação PERMITIDA (bomba ON)."

# Mostra análise
print(f"\n{situacao}")

# Último print: linha única e fácil de copiar
print(f"\n💬 Comando para o Wokwi: POP={pop:.1f} RAIN3H={rain:.1f}")
