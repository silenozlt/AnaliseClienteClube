import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Título do aplicativo
st.title("Análise de Sócios e Convites")

# Upload dos arquivos
st.sidebar.header("Upload de Arquivos")
uploaded_socio = st.sidebar.file_uploader("Carregar MapeamentoSocios.xls", type="xls")
uploaded_convites = st.sidebar.file_uploader("Carregar ConvitesEmitidos.xls", type="xls")
uploaded_consumo = st.sidebar.file_uploader("Carregar ConsumoSocio.xls", type="xls")

if uploaded_socio and uploaded_convites and uploaded_consumo:
    # Carregar os dados
    df_socio = pd.read_excel(uploaded_socio)
    df_convites = pd.read_excel(uploaded_convites)
    df_consumo = pd.read_excel(uploaded_consumo)

    # Mesclar os datasets pelo campo IDENTIFICACAO
    df_merged = df_socio.merge(df_convites, on="IDENTIFICACAO", how="left")\
                         .merge(df_consumo, on="IDENTIFICACAO", how="left")

    # Exibir as primeiras linhas
    st.subheader("Dados Mesclados")
    st.write(df_merged.head(5))

    # Socio com maior Consumo
    st.subheader("Top 10 Consumidores")
    top_consumidores = df_merged.groupby(["IDENTIFICACAO", "SOCIO"])["TOTAL"].sum().reset_index()
    top_consumidores = top_consumidores.sort_values(by="TOTAL", ascending=False).head(10)
    st.write(top_consumidores)

    # Socio com mais convites gerados
    st.subheader("Top 10 Sócios com Mais Convites Gerados")
    convites_por_socio = df_convites.groupby("IDENTIFICACAO").size().reset_index(name="QUANTIDADE_CONVITES")
    top_convites = convites_por_socio.sort_values(by="QUANTIDADE_CONVITES", ascending=False).head(10)
    st.write(top_convites)

    # Criar uma coluna categorizada para "PAGO" e "GRATUITO"
    df_convites["TIPO_CONVITE"] = df_convites["TIPO_CONVITE"].apply(
        lambda x: "GRATUITO" if any(word in str(x).upper() for word in ["GRATUITO", "GRÁTIS"]) else "PAGO"
    )

    # Contar convites pagos e gratuitos por sócio
    convites_pagos = df_convites[df_convites["TIPO_CONVITE"] == "PAGO"].groupby("IDENTIFICACAO").size().reset_index(name="CONVITES_PAGOS")
    convites_gratuitos = df_convites[df_convites["TIPO_CONVITE"] == "GRATUITO"].groupby("IDENTIFICACAO").size().reset_index(name="CONVITES_GRATUITOS")

    # Juntar os dados
    convites_totais = convites_pagos.merge(convites_gratuitos, on="IDENTIFICACAO", how="outer").fillna(0)

    # Criar coluna total de convites
    convites_totais["TOTAL_CONVITES"] = convites_totais["CONVITES_PAGOS"] + convites_totais["CONVITES_GRATUITOS"]

    # Ordenar pelos que mais emitiram convites
    convites_totais = convites_totais.sort_values(by="TOTAL_CONVITES", ascending=False)

    # Exibir os top 10 sócios que mais geraram convites
    st.subheader("Top 10 Sócios que Mais Geraram Convites")
    st.write(convites_totais.head(10))

    # Calcular o total de cada tipo de convite
    total_pagos = convites_totais["CONVITES_PAGOS"].sum()
    total_gratuitos = convites_totais["CONVITES_GRATUITOS"].sum()

    # Criar dicionário com os valores
    dados = {"Pagos": total_pagos, "Gratuitos": total_gratuitos}

    # Criar gráfico de pizza
    st.subheader("Distribuição de Convites (Pagos vs Gratuitos)")
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(
        dados.values(),
        labels=dados.keys(),
        autopct="%1.1f%%",
        colors=["#ff9999", "#66b3ff"],
        startangle=90,
        wedgeprops={"edgecolor": "black"}
    )
    ax.set_title("Distribuição de Convites (Pagos vs Gratuitos)")
    st.pyplot(fig)

    # Contar os convidados que se tornaram sócios e os que não se tornaram
    total_socios = df_convites[df_convites["TORNOU_SÓCIO"] == "SIM"].shape[0]
    total_nao_socios = df_convites[df_convites["TORNOU_SÓCIO"] == "NÃO"].shape[0]

    # Criar dicionário de dados
    dados_socios = {"Tornaram-se Sócios": total_socios, "Não se Tornaram Sócios": total_nao_socios}

    # Criar gráfico de pizza
    st.subheader("Percentual de Convidados que se Tornaram Sócios")
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(
        dados_socios.values(),
        labels=dados_socios.keys(),
        autopct="%1.1f%%",
        colors=["#66b3ff", "#ff9999"],
        startangle=90,
        wedgeprops={"edgecolor": "black"}
    )
    ax.set_title("Percentual de Convidados que se Tornaram Sócios")
    st.pyplot(fig)

    # Filtrar apenas os convites que resultaram em novos sócios
    socios_que_trouxeram = df_convites[df_convites["TORNOU_SÓCIO"] == "SIM"]

    # Contar quantos novos sócios cada sócio trouxe
    socios_top = socios_que_trouxeram.groupby("IDENTIFICACAO")["TORNOU_SÓCIO"].count().reset_index()
    socios_top.columns = ["IDENTIFICACAO", "NOVOS_SOCIOS"]

    # Ordenar pelos que mais trouxeram novos sócios
    socios_top = socios_top.sort_values(by="NOVOS_SOCIOS", ascending=False)

    # Exibir os top 10
    st.subheader("Top 10 Sócios que Trouxeram Mais Novos Sócios")
    st.write(socios_top.head(10))

else:
    st.warning("Por favor, carregue todos os arquivos necessários para continuar.")