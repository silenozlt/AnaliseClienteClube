import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Upload dos arquivos
st.title("Análise de Convites e Sócios")
uploaded_socio = st.file_uploader("Carregar Mapeamento de Sócios", type=["xls", "xlsx"])
uploaded_convites = st.file_uploader("Carregar Convites Emitidos", type=["xls", "xlsx"])
uploaded_consumo = st.file_uploader("Carregar Consumo de Sócios", type=["xls", "xlsx"])

if uploaded_socio and uploaded_convites and uploaded_consumo:
    df_socio = pd.read_excel(uploaded_socio)
    df_convites = pd.read_excel(uploaded_convites)
    df_consumo = pd.read_excel(uploaded_consumo)

    # Exibir colunas para debug
    st.write("Colunas de df_convites:", df_convites.columns.tolist())

    # Verificar se a coluna "TIPO_CONVITE" existe antes de usá-la
    if "TIPO_CONVITE" not in df_convites.columns:
        st.warning("A coluna 'TIPO_CONVITE' não foi encontrada! Criando com valores padrão...")
        df_convites["TIPO_CONVITE"] = "Desconhecido"

    # Criar a coluna categorizada para "PAGO" e "GRATUITO"
    df_convites["TIPO_CONVITE"] = df_convites["TIPO_CONVITE"].astype(str).apply(
        lambda x: "GRATUITO" if any(word in x.upper() for word in ["GRATUITO", "GRÁTIS"]) else "PAGO"
    )

    # Contar convites pagos e gratuitos por sócio
    convites_pagos = df_convites[df_convites["TIPO_CONVITE"] == "PAGO"].groupby("IDENTIFICACAO").size().reset_index(name="CONVITES_PAGOS")
    convites_gratuitos = df_convites[df_convites["TIPO_CONVITE"] == "GRATUITO"].groupby("IDENTIFICACAO").size().reset_index(name="CONVITES_GRATUITOS")

    # Juntar os dados e preencher valores nulos
    convites_totais = convites_pagos.merge(convites_gratuitos, on="IDENTIFICACAO", how="outer").fillna(0)
    convites_totais["TOTAL_CONVITES"] = convites_totais["CONVITES_PAGOS"] + convites_totais["CONVITES_GRATUITOS"]

    # Ordenar os top 10 sócios com mais convites
    st.subheader("Top 10 Sócios que mais geraram convites")
    st.dataframe(convites_totais.sort_values(by="TOTAL_CONVITES", ascending=False).head(10))

    # Criar gráfico de pizza
    total_pagos = convites_totais["CONVITES_PAGOS"].sum()
    total_gratuitos = convites_totais["CONVITES_GRATUITOS"].sum()
    fig, ax = plt.subplots(figsize=(4, 4))  # Reduzindo o tamanho
    ax.pie(
        [total_pagos, total_gratuitos],
        labels=["Pagos", "Gratuitos"],
        autopct="%1.1f%%",
        colors=["#ff9999", "#66b3ff"],
        startangle=90,
        wedgeprops={"edgecolor": "black"}
    )
    ax.set_title("Distribuição de Convites")
    st.pyplot(fig)

    # Contar convidados que se tornaram sócios
    if "TORNOU_SÓCIO" in df_convites.columns:
        total_socios = df_convites[df_convites["TORNOU_SÓCIO"] == "SIM"].shape[0]
        total_nao_socios = df_convites[df_convites["TORNOU_SÓCIO"] == "NÃO"].shape[0]

        fig, ax = plt.subplots(figsize=(4, 4))  # Reduzindo tamanho
        ax.pie(
            [total_socios, total_nao_socios],
            labels=["Tornaram-se Sócios", "Não se Tornaram Sócios"],
            autopct="%1.1f%%",
            colors=["#66b3ff", "#ff9999"],
            startangle=90,
            wedgeprops={"edgecolor": "black"}
        )
        ax.set_title("Percentual de Convidados que se Tornaram Sócios")
        st.pyplot(fig)
    else:
        st.warning("A coluna 'TORNOU_SÓCIO' não foi encontrada no DataFrame de convites!")

else:
    st.info("Por favor, carregue todos os arquivos para continuar.")

