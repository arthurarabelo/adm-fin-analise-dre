import streamlit as st
import pandas as pd

st.title("Análise de Demonstração de Resultados")
st.text("📋 Gere a análise de sua DRE automaticamente, de maneira rápida, fácil e visual.")

def read_sheet():
    uploaded_file = st.session_state["dre_file"]
    if uploaded_file is not None:
        filename = uploaded_file.name.lower()

        if filename.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
            generate_dre_analysis(df)
        elif filename.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file)
            generate_dre_analysis(df)
        else:
            st.error("Unsupported file type")

def generate_dre_analysis(df: pd.DataFrame):
    year = round(df['Ano'].tolist()[0])
    operational_profit = df.loc[df['Dados'] == "Lucro operacional", "Ano"].values
    liquid_profit = df.loc[df['Dados'] == "Lucro líquido", "Ano"].values
    total_sales = df.loc[df['Dados'] == "Total de Vendas", "Ano"].values
    total_assets = df.loc[df['Dados'] == "Total de ativos", "Ano"].values
    fix_assets = df.loc[df['Dados'] == "Ativos fixos", "Ano"].values


with open("modelo_dre.xlsx", "rb") as file:
    st.download_button(
        label="Baixar o modelo de planilha",
        data=file,
        file_name="modelo_dre.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        icon="📥",
        help="Este deve ser o modelo anexado para realização dos cálculos. Caso adicione outro modelo, os cálculos não funcionarão corretamente."
    )

st.text("Após baixar o modelo acima e preenchê-lo, anexe-o abaixo 👇")

st.file_uploader(
    label="Anexe aqui sua planilha preenchida",
    type= ["csv", "xlsx"],
    key="dre_file",
    label_visibility="hidden",
    on_change=read_sheet
)

uploaded_file = st.session_state["dre_file"]
if uploaded_file is not None:
    st.info("📊 Planilha carregada com sucesso! A análise de sua DRE está sendo gerada...")
