import streamlit as st
import google.generativeai as genai

# 1. Configuração visual da página
st.set_page_config(page_title="Assistente de Extensão", page_icon="🎓")
st.title("🎓 Assistente Virtual - Setor de Estágios")
# Esconder o menu do Streamlit e o ícone do GitHub
esconder_menu = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
[data-testid="stToolbar"] {visibility: hidden;}
</style>
"""
st.markdown(esconder_menu, unsafe_allow_html=True)
st.write("Olá! Sou o assistente de estágios. Pergunte-me sobre editais, regulamentos, o que tiver dúvida sobre o setor.")

# 2. Conectando a IA com a chave de segurança
# O Streamlit vai buscar a sua chave escondida nas configurações dele
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.error("Chave de API não configurada.")

# 3. Lendo o seu regulamento
@st.cache_data
def carregar_documento():
    try:
        with open("regulamento.txt", "r", encoding="utf-8") as file:
            return file.read()
    except:
        return "Erro: Arquivo regulamento.txt não encontrado."

documento = carregar_documento()

# 4. Configurando as regras da IA (A restrição para não alucinar)
modelo = genai.GenerativeModel(
    mmodel_name="gemini-1.5-flash-latest",
    system_instruction=f"""Você é o assistente oficial do Setor de Extensão da Universidade. 
    Responda as dúvidas dos alunos baseando-se ESTRITAMENTE e APENAS no seguinte texto:
    ---
    {documento}
    ---
    Se a resposta não estiver no texto acima, diga exatamente: 'Desculpe, não encontrei essa informação no regulamento. Por favor, entre em contato direto com a secretaria de estágio.'"""
)

# 5. Criando a memória do chat
if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

for msg in st.session_state.mensagens:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 6. A caixa onde o aluno digita a pergunta
pergunta = st.chat_input("Digite sua dúvida aqui...")

if pergunta:
    # Mostra a pergunta do aluno na tela
    with st.chat_message("user"):
        st.markdown(pergunta)
    st.session_state.mensagens.append({"role": "user", "content": pergunta})

    # Pede a resposta para o Gemini e mostra na tela
    with st.chat_message("assistant"):
        resposta = modelo.generate_content(pergunta)
        st.markdown(resposta.text)
    st.session_state.mensagens.append({"role": "assistant", "content": resposta.text})
