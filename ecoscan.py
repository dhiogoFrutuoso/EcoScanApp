import streamlit as st
import pandas as pd
import json

# Lê o banco de dados do arquivo JSON
with open("banco_dados.json", "r", encoding="utf-8") as f:
    banco_dados = json.load(f)

# Cria DataFrame para exibir tabela
df = pd.DataFrame.from_dict(banco_dados, orient="index")

# Título principal
st.title("🌱 Verificador de Impacto Ambiental")
st.markdown("Consulte o impacto ambiental de materiais de forma rápida e visual.")

# Seção de seleção e entrada
with st.container():
    col1, col2 = st.columns([2, 3])
    with col1:
        item_selecionado = st.selectbox("📋 Selecione um item existente:", df.index)
        entrada = st.text_input("✏️ Ou digite outro item:")

    with col2:
        # Define o item a consultar
        item = entrada.strip().lower() if entrada else item_selecionado.lower()

        if item:
            if item in banco_dados:
                dados = banco_dados[item]

                # Informações em container separado
                with st.container():
                    st.subheader(f"🔎 {item.capitalize()}")

                    # Colunas para organizar dados
                    c1, c2 = st.columns(2)
                    c1.info(f"**🌍 Emissão de carbono:** {dados['carbono']}")
                    c1.success(f"**🌿 Orgânico:** {'Sim' if dados['organico'] else 'Não'}")
                    c2.warning(f"**♻️ Reciclável:** {'Sim' if dados['reciclavel'] else 'Não'}")
                    c2.info(f"**⏳ Tempo de decomposição:** {dados['decomposicao']}")

                    # Converte carbono para float e define impacto
                    carbono_valor = float(dados['carbono'].split()[0].replace(",", "."))

                    if carbono_valor <= 1.0:
                        impacto_texto = "Baixo"
                        cor = "#03d5ff"  # azul
                        largura = 30
                    elif carbono_valor <= 3.0:
                        impacto_texto = "Médio"
                        cor = "#32CD32"  # verde-limão
                        largura = 60
                    else:
                        impacto_texto = "Alto"
                        cor = "red"
                        largura = 90

                    # Exibe texto do impacto
                    st.markdown(f"**💥 Impacto ambiental estimado: {impacto_texto}**")

                    # Barra de impacto colorida (HTML)
                    barra_html = f"""
                    <div style='background-color: #e0e0e0; border-radius: 5px; width: 100%; height: 20px; margin-bottom:20px;'>
                        <div style='background-color: {cor}; width: {largura}%; height: 100%; border-radius: 5px;'>
                        </div>
                    </div>
                    """
                    st.markdown(barra_html, unsafe_allow_html=True)
                    st.write("")  # espaçamento extra

            else:
                st.warning("⚠️ Item não encontrado no banco de dados.")

# Exibe tabela completa do banco dentro de um expander (inicialmente oculta)
with st.expander("📊 Mostrar base de dados completa"):
    st.dataframe(df)
