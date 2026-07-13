import streamlit as st
import google.generativeai as genai
import PyPDF2

# 1. Configuração visual da página
st.set_page_config(page_title="Assistente de Estágios", page_icon="🎓")

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
st.write("Olá! Sou o assistente da extensão. Pergunte-me sobre editais, horas e regulamentos.")

# 2. Conectando a IA com a chave de segurança
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error(f"Erro na chave de API: {e}")

# 3. Lendo o vosso arquivo PDF
@st.cache_data
def carregar_pdf():
    try:
        texto = ""
        # Abre o arquivo PDF no modo leitura binária (rb)
        with open("regulamento.pdf", "rb") as file:
            leitor = PyPDF2.PdfReader(file)
            # Lê todas as páginas do PDF e junta o texto
            for pagina in leitor.pages:
                texto += pagina.extract_text() + "\n"
        return texto
    except Exception as e:
        return f"Erro interno ao ler o PDF: {e}"

documento = carregar_pdf()

# 4. Configurando as regras da IA
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
            # Exibe o erro técnico exato conforme você solicitou
            st.error(f"Erro detalhado: {e}")
