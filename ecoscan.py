import streamlit as st
import pandas as pd
import json
import difflib
import unicodedata

# ========= Utilidades =========
def normalizar(s: str) -> str:
    if not isinstance(s, str):
        return ""
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn').lower().strip()

def mostrar_item(nome, dados, df):
    st.subheader(f"🔎 {nome.capitalize()}")

    c1, c2 = st.columns(2)
    c1.info(f"**🌍 Emissão de carbono na produção ou queima:** {dados['carbono']}")
    c1.success(f"**🌿 Orgânico:** {'Sim' if dados['organico'] else 'Não'}")
    c2.warning(f"**♻️ Reciclável:** {'Sim' if dados['reciclavel'] else 'Não'}")
    c2.info(f"**⏳ Tempo de decomposição:** {dados['decomposicao']}")

    try:
        carbono_valor = float(dados['carbono'].split()[0].replace(",", "."))
    except:
        carbono_valor = 0.0

    # Entrada: quantidade usada
    quantidade = st.number_input("📦 Quantidade usada (kg):", min_value=1, value=1)
    impacto_total = carbono_valor * quantidade

    # Barra de impacto
    if carbono_valor <= 1.0:
        impacto, cor, largura = "Baixo", "#03d5ff", 30
    elif carbono_valor <= 3.0:
        impacto, cor, largura = "Médio", "#FFFF00", 60
    else:
        impacto, cor, largura = "Alto", "red", 90

    st.markdown(f"**💥 Impacto ambiental estimado: {impacto}**")
    st.markdown(
        f"<div style='background:#e0e0e0;border-radius:5px;width:100%;height:20px;margin-bottom:20px;'>"
        f"<div style='background:{cor};width:{largura}%;height:100%;border-radius:5px;'></div>"
        f"</div>", unsafe_allow_html=True
    )

    # ========= Analogias palpáveis =========
    if impacto_total > 0:
        arvores = impacto_total * 5      # 1 kg CO2 ~ absorção de 5 árvores/ano
        km_carro = impacto_total * 5     # 1 kg CO2 ~ 5 km rodados de carro
        gelo = impacto_total * 0.5       # efeito simbólico

        st.markdown(f"### 🔥 Emissão total de {impacto_total:.2f} kg CO₂ na atmosfera: ")
        st.write(f"🌳 Seriam necessárias **{arvores:.0f} árvores** para absorver essa emissão em um ano.")
        st.write(f"🚗 Equivale a dirigir **{km_carro:.0f} km** de carro comum.")
        st.write(f"❄️ Essa quantidade de CO₂ contribui para o **derretimento de {gelo:.1f} kg de gelo polar**.")

    # ========= Selo de classificação =========
    selo = ""
    if impacto == "Baixo" and dados['reciclavel']:
        selo = "♻️ Sustentável"
    elif impacto == "Alto" and not dados['reciclavel']:
        selo = "⚠️ Crítico"
    elif dados['organico']:
        selo = "🌱 Neutro"
    if selo:
        st.success(f"**🏷️ Classificação: {selo}**")

    # ========= Comparação com média =========
    try:
        medias = df["carbono"].str.split().str[0].str.replace(",", ".").astype(float).mean()
    except:
        medias = 0

    if carbono_valor > medias:
        st.info(f"⚠️ Este item emite **mais CO₂ que a média da base** ({medias:.2f} kg CO₂/kg).")
    else:
        st.info(f"✅ Este item emite **menos CO₂ que a média da base** ({medias:.2f} kg CO₂/kg).")

    # ========= Formas de reutilização =========
    st.markdown("### **♻** Formas de reutilização:")
    st.success(f"♻  {dados['formas_de_reutilizacao']}")

def resetar_selecao():
    st.session_state.pop("selected_item", None)
    st.session_state.pop("selectbox_choice", None)

def aplicar_escolha():
    escolha = st.session_state.get("selectbox_choice")
    if escolha and escolha != "-- Selecione um item --":
        st.session_state["selected_item"] = escolha

# ========= Dados =========
try:
    with open("banco_dados.json", "r", encoding="utf-8") as f:
        banco_dados = json.load(f)
except FileNotFoundError:
    st.error("Arquivo 'banco_dados.json' não encontrado.")
    st.stop()

df = pd.DataFrame.from_dict(banco_dados, orient="index")
norm_to_original = {normalizar(k): k for k in banco_dados.keys()}
todas_norm = list(norm_to_original.keys())

# ========= UI =========
st.title("🌱 Verificador de Impacto Ambiental")
st.markdown("Digite um material, escolha um parecido (se necessário) e veja os dados.")

busca = st.text_input("✏️ Pesquisar item:", placeholder="Ex: plastico", key="search_text", on_change=resetar_selecao)

if st.session_state.get("selected_item"):
    nome = st.session_state["selected_item"]
    if nome in banco_dados:
        mostrar_item(nome, banco_dados[nome], df)
    else:
        st.warning("⚠️ Item selecionado não encontrado.")
elif busca:
    busca_norm = normalizar(busca)

    # sempre sugere lista, nunca seleciona automaticamente
    similares_norm = difflib.get_close_matches(busca_norm, todas_norm, n=8, cutoff=0.3)
    substring_norm = [n for n in todas_norm if busca_norm in n]
    candidatos_norm = list(dict.fromkeys(substring_norm + similares_norm))
    candidatos = [norm_to_original[n] for n in candidatos_norm]

    if candidatos:
        st.selectbox(
            "Itens encontrados:",
            options=["-- Selecione um item --"] + candidatos,
            key="selectbox_choice",
            on_change=aplicar_escolha
        )
        if st.session_state.get("selected_item"):
            mostrar_item(
                st.session_state["selected_item"],
                banco_dados[st.session_state["selected_item"]],
                df
            )
    else:
        st.warning("⚠️ Nenhum item parecido encontrado.")

with st.expander("📊 Mostrar base de dados completa"):
    st.dataframe(df)
