import streamlit as st
from openai import OpenAI
import base64
import json

# ========= Configuração =========
st.set_page_config(page_title="🌱 Verificador de Impacto Ambiental", page_icon="🌱")
st.title("🌱 Verificador de Impacto Ambiental")
st.markdown("Tire uma foto do material e veja sua análise ambiental.")

# ========= Função para exibir o item =========
def mostrar_item(nome, dados):
    st.subheader(f"🔎 {nome.capitalize()}")

    c1, c2 = st.columns(2)
    c1.info(f"**🌍 Emissão de carbono na produção ou queima:** {dados.get('carbono','Não informado')}")
    c1.success(f"**🌿 Orgânico:** {'Sim' if dados.get('organico') else 'Não'}")
    c2.warning(f"**♻️ Reciclável:** {'Sim' if dados.get('reciclavel') else 'Não'}")
    c2.info(f"**⏳ Tempo de decomposição:** {dados.get('decomposicao','Não informado')}")

    try:
        carbono_valor = float(dados["carbono"].split()[0].replace(",", "."))
    except:
        carbono_valor = 0.0

    # Entrada: quantidade usada
    quantidade = st.number_input("📦 Quantidade usada (kg):", min_value=1, value=1)
    impacto_total = carbono_valor * quantidade

    # Barra de impacto
    if carbono_valor <= 1.0:
        impacto, cor, largura = "Baixo", "#00FF00", 30
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
        arvores = impacto_total * 5
        km_carro = impacto_total * 5
        gelo = impacto_total * 0.5

        st.markdown(f"### 🔥 Emissão total de {impacto_total:.2f} kg CO₂ na atmosfera: ")
        st.write(f"🌳 Seriam necessárias **{arvores:.0f} árvores** para absorver essa emissão em um ano.")
        st.write(f"🚗 Equivale a dirigir **{km_carro:.0f} km** de carro comum.")
        st.write(f"❄️ Essa quantidade de CO₂ contribui para o **derretimento de {gelo:.1f} kg de gelo polar**.")

    # ========= Selo de classificação =========
    selo = ""
    if impacto == "Baixo" and dados.get("reciclavel"):
        selo = "♻️ Sustentável"
    elif impacto == "Alto" and not dados.get("reciclavel"):
        selo = "⚠️ Crítico"
    elif dados.get("organico"):
        selo = "🌱 Neutro"
    if selo:
        st.success(f"**🏷️ Classificação: {selo}**")

    # ========= Formas de reutilização =========
    st.markdown("### **♻** Formas de reutilização:")
    st.success(f"♻  {dados.get('formas_de_reutilizacao','Não informado')}")

# ========= Captura da câmera =========
img_file = st.camera_input("📷 Tire uma foto do objeto")

if img_file:
    st.image(img_file, caption="Imagem capturada", use_column_width=True)

    # Converte a imagem em base64
    bytes_data = img_file.getvalue()
    img_base64 = base64.b64encode(bytes_data).decode()

    # Cliente OpenAI
    client = OpenAI()

    with st.spinner("🔎 Analisando imagem..."):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": (
                            "Analise a imagem e retorne em JSON com os campos: "
                            "carbono (em kg CO₂/kg), organico (true/false), reciclavel (true/false), "
                            "decomposicao (texto), formas_de_reutilizacao (texto), "
                            "e nome (nome do material identificado)."
                        )},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}}
                    ],
                }
            ],
        )

    try:
        dados = json.loads(response.choices[0].message.content)
        mostrar_item(dados.get("nome","Material"), dados)
    except Exception as e:
        st.error("❌ Erro ao interpretar a resposta do modelo. Conteúdo retornado:")
        st.write(response.choices[0].message.content)
