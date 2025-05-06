import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from io import BytesIO

st.set_page_config(page_title="Simulador de Fluxo de Caixa", layout="wide")
st.title("💸 Simulador de Fluxo de Caixa")

# Entradas de simulação
st.sidebar.header("⚙️ Parâmetros de Simulação")
incluir_saldo = st.sidebar.checkbox("Incluir saldo inicial de R$25.000?", value=True)
comprar_maquina = st.sidebar.checkbox("Comprar máquina em Fevereiro (R$25.000)?", value=True)
pagar_emprestimo = st.sidebar.checkbox("Pagar empréstimo em Março (R$29.000)?", value=True)

duplicatas_receber = st.sidebar.number_input("📥 Duplicatas a receber em Janeiro", value=10000)
duplicatas_pagar = st.sidebar.number_input("📤 Duplicatas a pagar em Janeiro", value=8000)

# Dados base
meses = ['Janeiro', 'Fevereiro', 'Março']
vendas = [50000, 55000, 60000]
compras = [20000, 25000, 30000]
mod = [10000, 12000, 13000]
cif = [5000, 5000, 5000]
despesas = [4000, 4000, 4000]
comissoes = [0.05 * v for v in vendas]
impostos = [0, 0.1 * vendas[0], 0.1 * vendas[1]]

df = pd.DataFrame(index=meses)

# Entradas
df['Saldo Inicial'] = 25000 if incluir_saldo else 0
df.iloc[1:, df.columns.get_loc('Saldo Inicial')] = None
df['Recebimento 60%'] = [0.6 * v for v in vendas]
df['Recebimento 40%'] = [0, 0.4 * vendas[0], 0.4 * vendas[1]]
df['Duplicatas Receber'] = [duplicatas_receber, 0, 0]
df['Total Entradas'] = df['Recebimento 60%'] + df['Recebimento 40%'] + df['Duplicatas Receber']

# Saídas
df['Compras à vista'] = [0.5 * c for c in compras]
df['Compras mês anterior'] = [duplicatas_pagar, 0.5 * compras[0], 0.5 * compras[1]]
df['MOD'] = mod
df['CIF'] = cif
df['Despesas Adm.'] = despesas
df['Comissões'] = comissoes
df['Impostos'] = impostos
df['Máquina'] = [0, 25000 if comprar_maquina else 0, 0]
df['Empréstimo'] = [0, 0, 29000 if pagar_emprestimo else 0]

df['Total Saídas'] = df[['Compras à vista', 'Compras mês anterior', 'MOD', 'CIF',
                         'Despesas Adm.', 'Comissões', 'Impostos', 'Máquina', 'Empréstimo']].sum(axis=1)

# Saldo final
df['Saldo Final'] = 0.0
for i in range(len(df)):
    if i > 0:
        df.loc[meses[i], 'Saldo Inicial'] = df.loc[meses[i-1], 'Saldo Final']
    df.loc[meses[i], 'Saldo Final'] = df.loc[meses[i], 'Saldo Inicial'] + df.loc[meses[i], 'Total Entradas'] - df.loc[meses[i], 'Total Saídas']

# Mostrar resultado
st.subheader("📊 Resultado do Fluxo de Caixa")
st.dataframe(df.style.format("R$ {:,.2f}"))

# Gráfico interativo
st.subheader("📈 Saldo Final por Mês")
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df.index,
    y=df['Saldo Final'],
    mode='lines+markers',
    line=dict(color='royalblue', width=3),
    marker=dict(size=10),
    name="Saldo Final"
))
fig.update_layout(
    yaxis_title="Saldo (R$)",
    xaxis_title="Mês",
    template="plotly_dark",
    height=400
)
st.plotly_chart(fig, use_container_width=True)

# Análise de viabilidade
st.subheader("🚦 Análise de Viabilidade")
ultimo_saldo = df['Saldo Final'].iloc[-1]
if ultimo_saldo < 2000:
    st.error(f"🔴 Atenção: sua empresa pode entrar no vermelho em {df.index[-1]}! Saldo final: R$ {ultimo_saldo:,.2f}")
elif 2000 <= ultimo_saldo <= 10000:
    st.warning(f"🟡 Alerta: saldo apertado no final de {df.index[-1]}. Saldo final: R$ {ultimo_saldo:,.2f}")
else:
    st.success(f"🟢 Financeiramente viável! Saldo final de {df.index[-1]}: R$ {ultimo_saldo:,.2f}")

# Download Excel
output = BytesIO()
with pd.ExcelWriter(output, engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name='Fluxo de Caixa')

st.download_button("📥 Baixar Excel", data=output.getvalue(), file_name="fluxo_caixa_simulado.xlsx")
