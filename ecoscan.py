import streamlit as st
from openai import OpenAI
import json
import base64
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente de um arquivo .env (ótimo para desenvolvimento local)
load_dotenv()

# --- Configurações Iniciais ---
st.set_page_config(page_title="🌱 EcoScan", page_icon="🌱")
st.title("🌱 EcoScan: Verificador de Impacto Ambiental")
st.markdown("Tire uma foto do material e veja sua análise ambiental.")

# --- Carregamento Seguro da Chave da API ---
# Tenta carregar a chave do ambiente (funciona para .env local e Secrets do Streamlit)
api_key = os.getenv("OPENAI_API_KEY")
print("api key: ", api_key)

# Se a chave não for encontrada, exibe um erro claro e para a execução.
if not api_key:
    st.error("❌ ERRO: Chave da API da OpenAI não encontrada.")
    st.warning("Verifique seu arquivo .env ou as configurações de 'Secrets' no Streamlit Cloud.")
    st.stop()

# --- Inicialização do Cliente da API ---
try:
    client = OpenAI(api_key=api_key)
except Exception as e:
    st.error(f"Falha ao inicializar o cliente da OpenAI: {e}")
    st.stop()

# --- Funções de Exibição (Componentes da UI) ---

def exibir_detalhes_basicos(nome: str, dados: dict):
    """Exibe o nome, e os cards de informações básicas do material."""
    nome_final = nome.capitalize() if nome else "Material não identificado"
    st.subheader(f"🔎 {nome_final}")

    c1, c2 = st.columns(2)
    c1.info(f"**🌍 Emissão de carbono:** {dados.get('carbono', 'N/A')} kg CO₂/kg")
    c1.success(f"**🌿 Orgânico:** {'Sim' if dados.get('organico') else 'Não'}")
    c2.warning(f"**♻️ Reciclável:** {'Sim' if dados.get('reciclavel') else 'Não'}")
    c2.info(f"**⏳ Decomposição:** {dados.get('decomposicao', 'N/A')}")


def exibir_barra_impacto(carbono_valor: float):
    """Calcula e exibe a barra de impacto ambiental."""
    if carbono_valor <= 1.0:
        impacto, cor, largura = "Baixo", "#00FF00", 30
    elif carbono_valor <= 3.0:
        impacto, cor, largura = "Médio", "#FFFF00", 60
    else:
        impacto, cor, largura = "Alto", "red", 90

    st.markdown(f"**💥 Impacto ambiental estimado: {impacto}**")
    st.markdown(
        f"<div style='background:#e0e0e0;border-radius:5px;height:20px;'>"
        f"<div style='background:{cor};width:{largura}%;height:100%;border-radius:5px;'></div>"
        f"</div>", unsafe_allow_html=True
    )


def exibir_analogias(impacto_total: float):
    """Exibe analogias para o impacto total de CO₂."""
    if impacto_total <= 0:
        return

    arvores = impacto_total / 10
    km_carro = (impacto_total * 1000) / 120
    gelo = impacto_total * 0.5

    st.markdown(f"### 🔥 Emissão total de {impacto_total:.2f} kg CO₂ na atmosfera equivale a:")
    st.write(f"🌳 **{arvores:.1f} árvores** necessárias para absorver isso em um ano.")
    st.write(f"🚗 **{km_carro:.1f} km** dirigidos em um carro comum.")
    st.write(f"❄️ **{gelo:.1f} kg de gelo polar** derretido.")


def exibir_formas_reutilizacao(dados: dict):
    """Exibe as formas de reutilização em um formato limpo."""
    st.markdown("### **♻️ Formas de reutilização**")
    reutilizacoes = dados.get('formas_de_reutilizacao', [])
    if isinstance(reutilizacoes, list) and reutilizacoes:
        texto_reutilizacao = ", ".join(reutilizacoes)
        st.success(texto_reutilizacao)
    else:
        st.info("Nenhuma sugestão de reutilização encontrada.")


# --- Função Principal de Lógica e Renderização ---

def processar_e_exibir_resultado(dados_item: dict):
    """Função principal que orquestra a exibição dos resultados."""
    if not dados_item:
        st.error("❌ Não foi possível extrair dados da resposta da IA.")
        return

    nome = dados_item.get("nome")
    exibir_detalhes_basicos(nome, dados_item)

    try:
        carbono_valor = float(dados_item.get("carbono", 0))
    except (ValueError, TypeError):
        carbono_valor = 0.0

    quantidade = st.number_input("📦 Quantidade usada (kg):", min_value=1, value=1, key="quantidade_input")

    exibir_barra_impacto(carbono_valor)
    exibir_analogias(carbono_valor * quantidade)
    exibir_formas_reutilizacao(dados_item)


def extrair_json(response_text: str) -> dict:
    """Extrai um objeto JSON de uma string de texto."""
    try:
        inicio = response_text.find("{")
        fim = response_text.rfind("}") + 1
        if inicio == -1 or fim == 0:
            return {}
        return json.loads(response_text[inicio:fim])
    except (json.JSONDecodeError, AttributeError, IndexError, TypeError):
        return {}


# --- Fluxo Principal da Aplicação ---

img_file = st.camera_input("📷 Tire uma foto do objeto para análise")

if img_file:
    st.image(img_file, caption="Imagem capturada", use_container_width=True)

    with st.spinner("🔎 Analisando imagem..."):
        try:
            bytes_data = img_file.getvalue()
            base64_image = base64.b64encode(bytes_data).decode('utf-8')

            prompt_text = (
                "Analise a imagem e identifique o objeto principal. Ignore pessoas. "
                "Retorne APENAS UM JSON VÁLIDO com as chaves: "
                "`nome` (string), `carbono` (float), `reciclavel` (boolean), "
                "`decomposicao` (string), e `formas_de_reutilizacao` (lista de strings). "
                "Se não souber um valor, retorne null. Seja objetivo."
            )

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_text},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
                    ]
                }],
                max_tokens=300
            )

            dados_ia = extrair_json(response.choices[0].message.content)
            processar_e_exibir_resultado(dados_ia)

        except Exception as e:
            st.error("❌ Ocorreu um erro durante a análise.")
            st.exception(e)

