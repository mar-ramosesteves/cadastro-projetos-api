from flask import Flask, request, jsonify
import os
from datetime import datetime
from flask_cors import CORS
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

app = Flask(__name__)
CORS(app, supports_credentials=True)

# 🔐 Carregar credenciais da variável de ambiente
SCOPES = ['https://www.googleapis.com/auth/drive']
credencial_texto = os.environ.get("GOOGLE_DRIVE_CREDENTIALS")
os.makedirs("credenciais", exist_ok=True)
caminho_temp = os.path.join("credenciais", "temp_chave.json")
with open(caminho_temp, "w") as f:
    f.write(credencial_texto)

creds = service_account.Credentials.from_service_account_file(
    caminho_temp, scopes=SCOPES
)
drive_service = build('drive', 'v3', credentials=creds)

# 📁 Função para upload com pasta destino
def upload_para_drive(caminho_local, nome_destino_drive, pasta_id=None):
    try:
        file_metadata = {'name': nome_destino_drive}
        if pasta_id:
            file_metadata['parents'] = [pasta_id]
        media = MediaFileUpload(caminho_local, resumable=True)
        file = drive_service.files().create(
            body=file_metadata, media_body=media, fields='id'
        ).execute()
        print(f"✅ Enviado: {nome_destino_drive} (ID: {file.get('id')})", flush=True)
    except Exception as e:
        print(f"❌ Erro no upload {nome_destino_drive}: {e}", flush=True)

# 👥 Compartilhar pasta com e-mail
def compartilhar_pasta_com_email(pasta_id, email):
    try:
        permission = {
            'type': 'user',
            'role': 'writer',
            'emailAddress': email
        }
        drive_service.permissions().create(
            fileId=pasta_id,
            body=permission,
            fields='id',
            sendNotificationEmail=False
        ).execute()
        print(f"👥 Pasta compartilhada com: {email}")
    except Exception as e:
        print(f"❌ Erro ao compartilhar pasta: {e}", flush=True)

@@app.route("/criar-pastas", methods=["POST"])
def criar_pastas():
    print("🚨 ENTROU NA FUNÇÃO /criar-pastas 🚨", flush=True)
    try:
        return jsonify({"mensagem": "FUNÇÃO FOI EXECUTADA!"})
    except Exception as e:
        print("❌ Erro ao criar pastas:", str(e), flush=True)
        return jsonify({"erro": str(e)}), 500


@app.route("/")
def home():
    return "API de criação de pastas ativa!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

