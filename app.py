import streamlit as st
import emoji

st.title("Análise de Demonstração de Resultados")
st.text("📋 Gere a análise de sua DRE automaticamente, de maneira rápida, fácil e visual.")

with open("dre_modelo.xlsx", "rb") as file:
    st.download_button(
        label="Baixar o modelo de planilha",
        data=file,
        file_name="modelo_dre.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        icon="📥",
        help="Este deve ser o modelo anexado para realização dos cálculos. Caso adicione outro modelo, os cálculos não funcionarão corretamente."
    )
