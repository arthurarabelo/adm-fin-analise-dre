import streamlit as st
import pandas as pd
from dataclasses import dataclass
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from datetime import datetime
import time

st.title("Análise Financeira")
st.text("📋 Forneça alguns dados de sua DRE e de seu Balanço Patrimonial e gere a sua análise automaticamente, \
        de maneira rápida, fácil, visual e com a garantia da privacidade de sua empresa. ")

@dataclass
class SheetInformation:
    gross_operating_income: float # receita operacional bruta
    liquid_profit: float # lucro líquido
    operational_profit: float # lucro operacional
    sales: float # vendas
    asset: float # ativo
    liabilities: float # passivo
    fix_asset: float # ativo não circulante
    current_asset: float  # ativo circulante
    fix_liabilities: float # passivo não circulante
    current_liabilities: float # passivo circulante
    net_worth: float # patrimônio líquido
    inventory: float #estoque

@dataclass
class ComputedInformation:
    # ========== Índices de Fleuriet ==========
    floating_capital: float # capital de giro
    floating_capital_need: float # necessidade de capital de giro
    treasury: float # tesouraria
    # =========================================
    general_liquidity: float # liquidez geral
    current_liquidity: float # liquidez corrente
    dry_liquidity: float # liquidez seca
    general_indebtedness: float # endividamento geral
    debt_composition: float # composicao_do_endividamento
    liquid_margin: float # margem líquida
    operational_margin: float # margem operacional
    liquid_profit_margin: float # margem de lucro líquido
    roa: float # Retorno Sobre o Ativo
    roe: float # Retorno Sobre o PL
    assets_turnover: float # giro dos ativos
    fix_assets_turnover: float # giro dos ativos fixos
    inventory_turnover: float # giro do estoque

def read_sheet():
    dre_uploaded_file = st.session_state["dre_file"]
    balanco_uploaded_file = st.session_state["balanco_file"]

    if dre_uploaded_file and balanco_uploaded_file is not None:
        dre_filename = dre_uploaded_file.name.lower()
        balanco_filename = balanco_uploaded_file.name.lower()

        if dre_filename.endswith(".xlsx") and balanco_filename.endswith(".xlsx"):
            dre_df = pd.read_excel(dre_uploaded_file)
            balanco_df = pd.read_excel(balanco_uploaded_file)

            try:
                analysis = generate_dre_analysis(dre_df, balanco_df)
                return analysis
            except ValueError:
                st.error("Forneça dados válidos. Verifique se não esqueceu nenhuma célula em branco ou se os valores estão corretos.")
                del st.session_state["dre_file"]
                del st.session_state["balanco_file"]
        else:
            st.error("A extensão do arquivo deve ser .xlsx")

def get_sheets_data(dre_df: pd.DataFrame, balanco_df: pd.DataFrame) -> SheetInformation:
    return SheetInformation(
        gross_operating_income = dre_df.loc[dre_df['Dados'] == "Receita Operacional Bruta", "Valor"].values,
        liquid_profit = dre_df.loc[dre_df['Dados'] == "Lucro Líquido", "Valor"].values,
        sales = dre_df.loc[dre_df['Dados'] == "Vendas", "Valor"].values,
        operational_profit = dre_df.loc[dre_df['Dados'] == "Lucro Operacional", "Valor"].values,
        asset = balanco_df.loc[balanco_df['Dados'] == "Ativo (total)", "Valor"].values,
        current_asset = balanco_df.loc[balanco_df['Dados'] == "Ativo Não Circulante", "Valor"].values,
        fix_asset = balanco_df.loc[balanco_df['Dados'] == "Ativo Circulante", "Valor"].values,
        liabilities = balanco_df.loc[balanco_df['Dados'] == "Passivo (total)", "Valor"].values,
        fix_liabilities = balanco_df.loc[balanco_df['Dados'] == "Passivo Não Circulante", "Valor"].values,
        current_liabilities = balanco_df.loc[balanco_df['Dados'] == "Passivo Circulante", "Valor"].values,
        inventory = balanco_df.loc[balanco_df['Dados'] == "Estoque", "Valor"].values,
        net_worth = balanco_df.loc[balanco_df['Dados'] == "Patrimônio Líquido", "Valor"].values
    )

def get_computed_info(sheetInfo: SheetInformation) -> ComputedInformation:
    return ComputedInformation(
        floating_capital=sheetInfo.fix_liabilities - sheetInfo.fix_asset,
        floating_capital_need=sheetInfo.current_asset - sheetInfo.current_liabilities,
        treasury = (sheetInfo.fix_liabilities - sheetInfo.fix_asset) - (sheetInfo.current_asset - sheetInfo.current_liabilities),
        general_liquidity=(sheetInfo.current_asset + sheetInfo.fix_asset) / (sheetInfo.current_liabilities + sheetInfo.fix_liabilities),
        current_liquidity=sheetInfo.current_asset / sheetInfo.current_liabilities,
        dry_liquidity=(sheetInfo.current_asset - sheetInfo.inventory) / sheetInfo.current_liabilities,
        general_indebtedness=(sheetInfo.current_liabilities + sheetInfo.fix_liabilities) / sheetInfo.asset,
        debt_composition=sheetInfo.fix_liabilities / (sheetInfo.current_liabilities + sheetInfo.fix_liabilities),
        liquid_margin=sheetInfo.liquid_profit / sheetInfo.sales,
        operational_margin=sheetInfo.operational_profit / sheetInfo.sales,
        liquid_profit_margin=sheetInfo.liquid_profit / sheetInfo.sales,
        roa=sheetInfo.liquid_profit / sheetInfo.asset,
        roe=sheetInfo.liquid_profit / sheetInfo.net_worth,
        assets_turnover=sheetInfo.sales / sheetInfo.asset,
        fix_assets_turnover=sheetInfo.sales / sheetInfo.fix_asset,
        inventory_turnover=sheetInfo.sales / sheetInfo.inventory
    )


def generate_dre_analysis(dre_df: pd.DataFrame, balanco_df: pd.DataFrame):
    sheet_info = get_sheets_data(dre_df, balanco_df)
    return get_computed_info(sheet_info)

def gerar_pdf(indices, explicacoes, filename="relatorio.pdf"):
    doc = SimpleDocTemplate(filename, pagesize=A4, title="Relatório Financeiro")
    styles = getSampleStyleSheet()
    normal_style = styles["Normal"]

    elementos = []

    # 🔹 Título
    titulo_style = ParagraphStyle(
        'titulo',
        parent=styles['Title'],
        fontSize=20,
        textColor=colors.HexColor("#2E86C1"),
        alignment=1
    )
    elementos.append(Paragraph("Relatório Financeiro", titulo_style))
    elementos.append(Spacer(1, 20))

    # 🔹 Montando a tabela
    data = [
        [Paragraph("<b>Índice</b>", normal_style),
         Paragraph("<b>Valor</b>", normal_style),
         Paragraph("<b>Explicação</b>", normal_style)]
    ]

    for nome, valor in indices.items():
        data.append([
            Paragraph(nome, normal_style),
            Paragraph(str(valor), normal_style),
            Paragraph(explicacoes.get(nome, ""), normal_style)
        ])

    tabela = Table(data, colWidths=[100, 80, 280])  # colWidths fixos
    tabela.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2E86C1")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elementos.append(tabela)
    elementos.append(Spacer(1, 20))

    # 🔹 Rodapé
    data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
    rodape_style = ParagraphStyle(
        'rodape',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=2
    )
    elementos.append(Paragraph(f"Gerado em {data_atual}", rodape_style))

    doc.build(elementos)

with open("DADOS_DRE.xlsx", "rb") as file:
    st.download_button(
        label="Baixar o modelo de DRE",
        data=file,
        file_name="dados_dre.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        icon="📥",
        help="Este deve ser o modelo anexado para realização dos cálculos. Caso adicione outro modelo, os cálculos não funcionarão corretamente."
    )

with open("DADOS_Balanco_Patrimonial.xlsx", "rb") as file:
    st.download_button(
        label="Baixar o modelo de Balanço Patrimonial",
        data=file,
        file_name="dados_balanco.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        icon="📥",
        help="Este deve ser o modelo anexado para realização dos cálculos. Caso adicione outro modelo, os cálculos não funcionarão corretamente."
    )

st.text("Após baixar os modelos acima e preenchê-los, anexe-os abaixo 👇")
st.warning("Nos valores, forneça apenas dados numéricos (sem letras ou outros caracteres). Se o valor for 'R$ 1000,50' - por exemplo - apenas preencha '1000,50'.")

st.file_uploader(
    label="Anexe aqui a sua DRE preenchida",
    type= "xlsx",
    key="dre_file",
    label_visibility="visible",
)

st.file_uploader(
    label="Anexe aqui o seu Balanço Patrimonial preenchido",
    type= "xlsx",
    key="balanco_file",
    label_visibility="visible",
)

dre_uploaded_file = st.session_state["dre_file"]
balanco_uploaded_file = st.session_state["balanco_file"]

if st.button("Gerar análise"):
    if dre_uploaded_file and balanco_uploaded_file is not None:
        metricas = read_sheet()
        indices = {
            "Margem Líquida": "12%",
            "Capital de Giro": "R$ 150.000",
            "Liquidez Corrente": "1,8"
        }

        explicacoes = {
            "Margem Líquida": "Mostra quanto a empresa lucra para cada R$1 de receita líquida.",
            "Capital de Giro": "Indica se a empresa consegue pagar dívidas de curto prazo.",
            "Liquidez Corrente": "Mostra a relação entre ativos e passivos de curto prazo."
        }

        try:
            progress_text = "Gerando sua análise..."
            my_bar = st.progress(0, text=progress_text)

            for percent_complete in range(100):
                time.sleep(0.01)
                my_bar.progress(percent_complete + 1, text=progress_text)
            time.sleep(1)
            my_bar.empty()

            gerar_pdf(indices, explicacoes, "relatorio.pdf")
            with open("relatorio.pdf", "rb") as f:
                st.download_button("📥 Baixar Relatório", f,  file_name="relatorio.pdf")
        except:
            st.error("Erro ao gerar a análise. Verifique se seguiu todos os passos corretamente.")
    else:
        st.error("Anexe primeiro as planilhas.")
