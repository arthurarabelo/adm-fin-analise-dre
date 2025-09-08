import streamlit as st
import pandas as pd
from dataclasses import dataclass

st.title("Análise de Demonstração de Resultados")
st.text("📋 Gere a análise de sua DRE automaticamente, de maneira rápida, fácil e visual.")

@dataclass
class SheetInformation:
    year: int
    operational_profit: float
    liquid_profit: float
    total_sales: float
    total_assets: float
    fix_assets: float
    bill_to_receive: float
    daily_sales_mean: float
    inventory: float
    liquid_net_worth_accountable_value: float
    actions_price: float
    profit_per_action: float

@dataclass
class ComputedInformation:
    operational_margin: float
    liquid_profit_margin: float
    assets_turnover: float
    fix_assets_turnover: float
    days_deadline_receipt: float
    inventory_turnover: float
    liquid_net_worth_return: float
    pe_index: float

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

def get_sheet_data(df: pd.DataFrame) -> SheetInformation:
    return SheetInformation(
        year = round(df['Ano'].tolist()[0]),
        operational_profit = df.loc[df['Dados'] == "Lucro operacional", "Ano"].values,
        liquid_profit = df.loc[df['Dados'] == "Lucro líquido", "Ano"].values,
        total_sales = df.loc[df['Dados'] == "Total de Vendas", "Ano"].values,
        total_assets = df.loc[df['Dados'] == "Total de ativos", "Ano"].values,
        fix_assets = df.loc[df['Dados'] == "Ativos fixos", "Ano"].values,
        bill_to_receive = df.loc[df['Dados'] == "Contas a receber", "Ano"].values,
        daily_sales_mean = df.loc[df['Dados'] == "Vendas médias diárias", "Ano"].values,
        inventory = df.loc[df['Dados'] == "Estoque", "Ano"].values,
        liquid_net_worth_accountable_value = df.loc[df['Dados'] == "Valor contábil do patrimônio líquido", "Ano"].values,
        actions_price = df.loc[df['Dados'] == "Preço das ações", "Ano"].values,
        profit_per_action = df.loc[df['Dados'] == "Lucros por ação", "Ano"].values
    )

def get_computed_info(sheetInfo: SheetInformation) -> ComputedInformation:
    return ComputedInformation(
        operational_margin = sheetInfo.operational_profit / sheetInfo.total_sales,
        liquid_profit_margin = sheetInfo.liquid_profit / sheetInfo.total_sales,
        assets_turnover = sheetInfo.total_sales / sheetInfo.total_assets,
        fix_assets_turnover = sheetInfo.total_sales / sheetInfo.fix_assets,
        days_deadline_receipt = sheetInfo.bill_to_receive / sheetInfo.daily_sales_mean,
        inventory_turnover = sheetInfo.total_sales / sheetInfo.inventory,
        liquid_net_worth_return = sheetInfo.liquid_profit / sheetInfo.liquid_net_worth_accountable_value,
        pe_index = sheetInfo.actions_price / sheetInfo.profit_per_action
    )


def generate_dre_analysis(df: pd.DataFrame):
    sheet_info = get_sheet_data(df)
    computed_info = get_computed_info(sheet_info)

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
