import streamlit as st
import os
from openai import OpenAI
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração da página
st.set_page_config(page_title="Transcritor de Áudio", page_icon="🎤")

# Título e descrição
st.title("🎤 Transcritor de Áudio")
st.markdown("Faça upload de um arquivo de áudio e obtenha sua transcrição.")

# Obter a chave API do ambiente ou permitir entrada manual
default_api_key = os.getenv("OPENAI_API_KEY", "")

# Se estiver no modo produção e a chave existir no ambiente, use-a diretamente
if default_api_key and os.getenv("STREAMLIT_DEPLOYMENT", "") == "production":
    api_key = default_api_key
    st.success("Chave API configurada via variável de ambiente.")
else:
    # Caso contrário, permita que o usuário insira
    api_key = st.text_input("Insira sua chave API OpenAI", 
                           value=default_api_key,
                           type="password")

# Upload de arquivo
uploaded_file = st.file_uploader("Escolha um arquivo de áudio", type=["mp3", "wav", "m4a", "ogg"])

# Opções para idioma de transcrição
idioma = st.selectbox(
    "Selecione o idioma da transcrição",
    options=["pt", "en", "es", "fr", "de", "it", "ja", "ko", "zh"],
    index=0
)


# Quando o usuário clicar no botão de transcrição
if st.button("Transcrever") and uploaded_file is not None:
    with st.spinner("Transcrevendo o áudio..."):
        try:
            # Salvar o arquivo temporariamente
            temp_file_path = f"temp_audio_file{os.path.splitext(uploaded_file.name)[1]}"
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Configurar cliente OpenAI
            client = OpenAI(api_key=api_key)
            
            # Abrir o arquivo para enviar para a API
            audio_file = open(temp_file_path, "rb")
            
            # Fazer a transcrição
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=idioma
            )
            
            # Fechar o arquivo
            audio_file.close()
            
            # Remover o arquivo temporário
            os.remove(temp_file_path)
            
            # Exibir resultado
            st.success("Transcrição concluída!")
            st.subheader("Resultado da transcrição:")
            st.text_area("Texto transcrito", transcript.text, height=300)
            
            # Opção para baixar a transcrição
            st.download_button(
                label="Baixar transcrição como arquivo TXT",
                data=transcript.text,
                file_name=f"{os.path.splitext(uploaded_file.name)[0]}_transcricao.txt",
                mime="text/plain"
            )
            
        except Exception as e:
            st.error(f"Ocorreu um erro durante a transcrição: {str(e)}")

# Instruções e informações adicionais
st.markdown("---")
st.markdown("""
### Como usar:
1. Faça upload de um arquivo de áudio
2. Selecione o idioma do áudio
3. Clique em "Transcrever"
4. Baixe o resultado como arquivo TXT

### Observações:
- Formatos suportados: MP3, WAV, M4A, OGG
- A qualidade da transcrição depende da clareza do áudio
- Tamanho máximo recomendado: 25MB
""")

# Rodapé
st.markdown("---")
st.markdown("Desenvolvido com Streamlit e OpenAI Whisper API")
