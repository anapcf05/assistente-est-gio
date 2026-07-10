import streamlit as st
import google.generativeai as genai

# 1. Configuração visual da página
st.set_page_config(page_title="Assistente de Extensão", page_icon="🎓")

# Esconder o menu do Streamlit, o cabeçalho e o ícone do GitHub
esconder_menu = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
[data-testid="stToolbar"] {visibility: hidden;}
</style>
"""
st.markdown(esconder_menu, unsafe_allow_html=True)

st.title("🎓 Assistente Virtual - Setor de Extensão")
st.write("Olá! Sou o assistente da extensão. Pergunta-me sobre editais, horas e regulamentos.")

# 2. Conectando a IA com a chave de segurança
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error("Chave de API não configurada corretamente nos Secrets.")

# 3. Lendo o vosso regulamento
@st.cache_data
def carregar_documento():
    try:
        with open("regulamento.txt", "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        return "Erro: Arquivo regulamento.txt não encontrado."

documento = carregar_documento()

# 4. Configurando as regras da IA (A restrição para não alucinar)
modelo = genai.GenerativeModel(
    model_name="models/gemini-1.5-flash",
    system_instruction=f"""Você é o assistente oficial do Setor de Extensão da Universidade. 
    Responda as dúvidas dos alunos baseando-se ESTRITAMENTE e APENAS no seguinte texto:
    ---
    {documento}
    ---
    Se a resposta não estiver no texto acima, diga exatamente: 'Desculpe, não encontrei essa informação no regulamento. Por favor, entre em contato direto com a secretaria.'"""
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
        try:
            resposta = modelo.generate_content(pergunta)
            st.markdown(resposta.text)
            st.session_state.mensagens.append({"role": "assistant", "content": resposta.text})
        except Exception as e:
            st.error(f"Ocorreu um erro ao processar a resposta. Por favor, tente novamente em alguns segundos.")
