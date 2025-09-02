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

def mostrar_item(nome, dados):
    st.subheader(f"🔎 {nome.capitalize()}")

    c1, c2 = st.columns(2)
    c1.info(f"**🌍 Emissão de carbono:** {dados['carbono']}")
    c1.success(f"**🌿 Orgânico:** {'Sim' if dados['organico'] else 'Não'}")
    c2.warning(f"**♻️ Reciclável:** {'Sim' if dados['reciclavel'] else 'Não'}")
    c2.info(f"**⏳ Tempo de decomposição:** {dados['decomposicao']}")

    try:
        carbono_valor = float(dados['carbono'].split()[0].replace(",", "."))
    except:
        carbono_valor = 0.0

    if carbono_valor <= 1.0:
        impacto, cor, largura = "Baixo", "#03d5ff", 30
    elif carbono_valor <= 3.0:
        impacto, cor, largura = "Médio", "#32CD32", 60
    else:
        impacto, cor, largura = "Alto", "red", 90

    st.markdown(f"**💥 Impacto ambiental estimado: {impacto}**")
    st.markdown(
        f"<div style='background:#e0e0e0;border-radius:5px;width:100%;height:20px;margin-bottom:20px;'>"
        f"<div style='background:{cor};width:{largura}%;height:100%;border-radius:5px;'></div>"
        f"</div>", unsafe_allow_html=True
    )

def resetar_selecao():
    st.session_state.pop("selected_item", None)
    st.session_state.pop("selectbox_choice", None)

def aplicar_escolha():
    st.session_state["selected_item"] = st.session_state.get("selectbox_choice")

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
        mostrar_item(nome, banco_dados[nome])
    else:
        st.warning("⚠️ Item selecionado não encontrado.")
elif busca:
    busca_norm = normalizar(busca)
    if busca_norm in norm_to_original:
        nome = norm_to_original[busca_norm]
        st.session_state["selected_item"] = nome
        mostrar_item(nome, banco_dados[nome])
    else:
        similares_norm = difflib.get_close_matches(busca_norm, todas_norm, n=8, cutoff=0.3)
        substring_norm = [n for n in todas_norm if busca_norm in n]
        candidatos_norm = list(dict.fromkeys(substring_norm + similares_norm))
        candidatos = [norm_to_original[n] for n in candidatos_norm]

        if candidatos:
            st.selectbox("Itens similares:", options=candidatos, key="selectbox_choice", on_change=aplicar_escolha)
            if st.session_state.get("selected_item"):
                mostrar_item(st.session_state["selected_item"], banco_dados[st.session_state["selected_item"]])
        else:
            st.warning("⚠️ Nenhum item parecido encontrado.")

with st.expander("📊 Mostrar base de dados completa"):
    st.dataframe(df)
