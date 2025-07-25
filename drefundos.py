import streamlit as st
import pandas as pd



# ========= SISTEMA DE LOGIN =========
usuarios = {
    "Joao": "LibraJP",
    "Estevan": "LibraDRE2025",
    "Breno": "LibraDRE2025",
    "Juan": "LibraJM"
}

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    with st.form("login_form"):
        st.subheader("🔐 Área Restrita")
        usuario = st.text_input("Usuário:")
        senha = st.text_input("Senha:", type="password")
        submit = st.form_submit_button("Entrar")

        if submit:
            if usuario in usuarios and usuarios[usuario] == senha:
                st.session_state.autenticado = True
                st.success("Login realizado com sucesso!")
                st.rerun()  # recarrega a página sem os campos
            else:
                st.error("Usuário ou senha inválidos.")
    st.stop()  # bloqueia o restante do app se não autenticado




# =================== CORES ===================
SPACE_CADET = "#272846"
HARVEST_GOLD = "#e5a125"
HONEYDEW = "#f0f8ea"
SLATE_GRAY = "#717c89"
VERDE = "#a4f4b8"
VERMELHO = "#f4b4b4"

# ========== CSS VISUAL PREMIUM ========== 
st.markdown(f"""
<style>
    html, body, .stApp, .block-container {{
        background-color: {SPACE_CADET} !important;
        color: {HARVEST_GOLD} !important;
    }}
    h1, h2, h3, h4, h5, h6, p, span, div {{
        color: {HARVEST_GOLD} !important;
    }}
    .stDataFrame thead tr th {{
        background: {HARVEST_GOLD} !important;
        color: {SPACE_CADET} !important;
        font-weight:800 !important;
        font-size:1.05em !important;
        border-bottom:2px solid {HONEYDEW}25 !important;
    }}
    .stDataFrame tbody tr td {{
        background: {SPACE_CADET} !important;
        color: {HONEYDEW} !important;
        font-size:0.95em !important;
        border-color: {SLATE_GRAY}30 !important;
    }}
    .stDataFrame {{
        border:1.5px solid {SLATE_GRAY}!important;
        border-radius:8px!important;
    }}
    .card {{
        background-color: {HONEYDEW};
        padding: 1rem;
        border-radius: 18px;
        box-shadow: 1px 1px 10px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
        text-align: center;
    }}
    .card h4 {{
        margin: 0.1rem 0;
        font-size: 1rem;
        color: {SLATE_GRAY} !important;
    }}
    .card p {{
        font-size: 1.3rem;
        font-weight: bold;
        color: {SPACE_CADET} !important;
    }}
</style>
""", unsafe_allow_html=True)

# ========== FUNÇÃO PARA LER PLANILHA ==========
def ler_google_sheet(sheet_id: str, aba: str) -> pd.DataFrame:
    aba_formatada = aba.replace(" ", "%20")
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={aba_formatada}"
    df = pd.read_csv(url)
    return df

# ========== FUNÇÃO DE FORMATAÇÃO ==========
colunas_percentuais = [
    "Rentabilidade Dia",
    "Rentabilidade Mês",
    "Subordinação Mezanino",
    "Subordinação Senior"
]

colunas_cor_condicional = ["Rentabilidade Dia", "Rentabilidade Mês"]

linhas_destaque = [
    "PL JR INICIAL", "QTD COTAS", "VALOR COTA", "ATIVOS", "DC", "SUPERIORES",
    "Valores a Liquidar / Receber", "PDD DC", "Resultado", "Total do Patrimônio",
    "QTD COTAS", "Valor Cota", "Rentabilidade Dia", "Rentabilidade Mês"
]

def formatar_valor(coluna, valor):
    if coluna in colunas_percentuais:
        return f"{valor:.2f}%".replace(".", ",")
    else:
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# ========== CÓDIGO DO SHEET ==========
SHEET_ID = "1F4ziJnyxpLr9VuksbSvL21cjmGzoV0mDPSk7XzX72iQ"

# === SELETOR DE FUNDO ===
fundo_sel = st.sidebar.selectbox("Selecione o fundo", ["Apuama", "Bristol"])
aba_map = {
    "Apuama": "Dre_Apuama",
    "Bristol": "Dre_Bristol"
}
aba_original_map = {
    "Apuama": "Dre_Apuama_Original",
    "Bristol": "Dre_Bristol_Original"
}
ABA = aba_map[fundo_sel]
ABA_ORIGINAL = aba_original_map[fundo_sel]

# ========== CARREGA DADOS ==========
df = ler_google_sheet(SHEET_ID, ABA)
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
df["Data"] = pd.to_datetime(df["Data"], dayfirst=True, errors="coerce")
df = df.dropna(subset=["Data"]).sort_values("Data")

colunas_numericas = df.columns.drop("Data")
for col in colunas_numericas:
    df[col] = (
        df[col]
        .astype(str)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .str.replace("%", "", regex=False)
        .astype(float)
    )

st.set_page_config(page_title=f"DRE - Fundo {fundo_sel}", layout="wide")
st.title(f"DRE - Fundo {fundo_sel}")

# === SIDEBAR: FILTRO DE DATA ===
st.sidebar.title("Filtro de Data")
datas_unicas = df["Data"].dropna().unique()
data_sel = st.sidebar.date_input(
    "Selecione a data para os cartões:",
    value=max(datas_unicas),
    min_value=min(datas_unicas),
    max_value=max(datas_unicas),
    format="DD/MM/YYYY"
)

df_filtrado = df[df["Data"] == pd.to_datetime(data_sel)]
if df_filtrado.empty:
    st.warning("Nenhum dado encontrado para a data selecionada.")
    st.stop()

# ========== EXIBE CARTÕES ========== 
st.markdown(f"### Indicadores para {data_sel.strftime('%d/%m/%Y')}")

dados = df_filtrado.iloc[0]
colunas_por_linha = 3
cards = []

largura_cartao = "220px"
espacamento_cartao = "0.5rem auto 1.5rem auto"  # topo, lateral, inferior, lateral

for i, col in enumerate(colunas_numericas):
    valor = dados[col]

    estilo_cartao = f"width: {largura_cartao}; min-height: 120px; margin: {espacamento_cartao};"

    if col in colunas_cor_condicional:
        cor_fundo = VERDE if valor > 0 else VERMELHO
        html = f"""
            <div class=\"card\" style=\"background-color:{cor_fundo}; {estilo_cartao}\">
                <h4>{col}</h4>
                <p>{formatar_valor(col, valor)}</p>
            </div>
        """
    elif col == "Subordinação Mezanino" and valor < 20:
        html = f"""
            <div class=\"card\" style=\"background-color:{VERMELHO}; {estilo_cartao}\">
                <h4>{col}</h4>
                <p>{formatar_valor(col, valor)}</p>
            </div>
        """
    elif col == "Subordinação Senior" and valor < 40:
        html = f"""
            <div class=\"card\" style=\"background-color:{VERMELHO}; {estilo_cartao}\">
                <h4>{col}</h4>
                <p>{formatar_valor(col, valor)}</p>
            </div>
        """
    else:
        html = f"""
            <div class=\"card\" style=\"{estilo_cartao}\">
                <h4>{col}</h4>
                <p>{formatar_valor(col, valor)}</p>
            </div>
        """

    cards.append(html)


for i in range(0, len(cards), colunas_por_linha):
    cols = st.columns(colunas_por_linha)
    for j, card in enumerate(cards[i:i + colunas_por_linha]):
        with cols[j]:
            st.markdown(card, unsafe_allow_html=True)

# ========== EXIBE TABELA COMPLETA ==========
st.markdown("### Histórico Completo")
st.dataframe(df, use_container_width=True, height=500)


# ========== ABA ORIGINAL (VISUAL COMPLETO) ==========
st.markdown("### Tabela Original (DRE Completa)")



#####################
# Lê a aba original com cabeçalho na primeira linha da planilha
def ler_google_sheet_original(sheet_id: str, aba: str) -> pd.DataFrame:
    aba_formatada = aba.replace(" ", "%20")
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={aba_formatada}"
    
    df_raw = pd.read_csv(url, header=None)
    new_header = df_raw.iloc[0]
    df = df_raw[1:].copy()
    df.columns = new_header
    df = df.reset_index(drop=True)
    return df

df_original = ler_google_sheet_original(SHEET_ID, ABA_ORIGINAL)

# Insere linha em branco antes das linhas de destaque (exceto as 3 últimas)
indices_destaque = [
    i for i, row in df_original.iterrows()
    if str(row.iloc[0]).strip() in linhas_destaque
]

# Remover as 3 últimas linhas de destaque do processo de inserção
indices_para_inserir = indices_destaque[:-3] if len(indices_destaque) > 3 else []

for i in reversed(indices_para_inserir):
    linha_em_branco = pd.Series([""] * len(df_original.columns), index=df_original.columns)
    df_original = pd.concat([
        df_original.iloc[:i],
        pd.DataFrame([linha_em_branco]),
        df_original.iloc[i:]
    ], ignore_index=True)

# Estiliza cabeçalho e células da tabela final
st.markdown(f"""
    <style>
        table thead th {{
            font-weight: 900 !important;
            text-align: center !important;
            color: {HONEYDEW} !important;
        }}
        table tbody td {{
            text-align: center !important;
            vertical-align: middle !important;
        }}
    </style>
""", unsafe_allow_html=True)

# Função para destacar linhas especiais
def highlight_linhas_especiais(row):
    if str(row.iloc[0]).strip() in linhas_destaque:
        return ['background-color: #4169E1; font-weight: bold'] * len(row)
    return [''] * len(row)

table_styles = [
    {"selector": "td", "props": [("text-align", "center"), ("vertical-align", "middle")]},
    {"selector": "th", "props": [("text-align", "center"), ("font-weight", "900"), ("color", HONEYDEW)]}
]

# Exibe a tabela com estilos aplicados
st.dataframe(
    df_original.style
        .apply(highlight_linhas_especiais, axis=1)
        .set_table_styles(table_styles),
    use_container_width=True,
    height=500
)
##############################



# Estiliza cabeçalho e células da tabela final
st.markdown(f"""
    <style>
        table thead th {{
            font-weight: 900 !important;
            text-align: center !important;
            color: {HONEYDEW} !important;
        }}
        table tbody td {{
            text-align: center !important;
            vertical-align: middle !important;
        }}
    </style>
""", unsafe_allow_html=True)



def highlight_linhas_especiais(row):
    if str(row[0]).strip() in linhas_destaque:
        return ['background-color: #4169E1; font-weight: bold'] * len(row)
    return [''] * len(row)

# Estilos CSS para centralizar conteúdo e cabeçalhos
table_styles = [
    {"selector": "td", "props": [("text-align", "center"), ("vertical-align", "middle")]},
    {"selector": "th", "props": [("text-align", "center"), ("font-weight", "900"), ("color", HONEYDEW)]}
]
