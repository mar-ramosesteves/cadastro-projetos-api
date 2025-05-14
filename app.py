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

@app.route("/criar-pastas", methods=["POST"])
def criar_pastas():

print("🚨 ENTROU NA FUNÇÃO /criar-pastas 🚨", flush=True)


    try:
        ...

    try:
        dados = request.get_json()
        empresa = dados.get("empresa")
        periodo_de = dados.get("periodo_de")
        periodo_ate = dados.get("periodo_ate")
        data_limite = dados.get("data_limite")
        nomes_lideres = dados.get("nome_lider", [])
        emails_lideres = dados.get("email_lider", [])

        if not empresa or not periodo_de or not periodo_ate or not data_limite:
            return jsonify({"erro": "Campos obrigatórios ausentes."}), 400

        data_inicio = datetime.strptime(periodo_de, "%Y-%m-%d")
        pasta_periodo = data_inicio.strftime("%m-%Y")

        base_dir = "dados_projetos"
        pasta_empresa = os.path.join(base_dir, empresa.replace(" ", "_"))
        pasta_periodo_completa = os.path.join(pasta_empresa, pasta_periodo)
        os.makedirs(pasta_periodo_completa, exist_ok=True)

        for nome, email in zip(nomes_lideres, emails_lideres):
            pasta_local = os.path.join(pasta_periodo_completa, email)
            os.makedirs(pasta_local, exist_ok=True)

            auto_path = os.path.join(pasta_local, "autoavaliacao.csv")
            equipe_path = os.path.join(pasta_local, "equipe.csv")

            with open(auto_path, "w") as f:
                f.write("Aguardando envio da autoavaliacao...\n")
            with open(equipe_path, "w") as f:
                f.write("Aguardando respostas da equipe...\n")

            # 📁 Criar pasta no Drive
            nome_pasta_drive = f"{empresa}_{pasta_periodo}_{email}"
            folder_metadata = {
                'name': nome_pasta_drive,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            folder = drive_service.files().create(
                body=folder_metadata, fields='id'
            ).execute()
            pasta_id = folder.get('id')

            # 👥 Compartilhar com seu e-mail
            compartilhar_pasta_com_email(pasta_id, "mar.ramosesteves@gmail.com")

print(f"❌ Erro ao compartilhar pasta: {e}", flush=True)

            # ⬆️ Upload dos arquivos
            upload_para_drive(auto_path, "autoavaliacao.csv", pasta_id)
            upload_para_drive(equipe_path, "equipe.csv", pasta_id)

        return jsonify({"mensagem": "Pastas criadas com sucesso e arquivos enviados ao Google Drive."})

    except Exception as e:
        print("❌ Erro ao criar pastas:", str(e))
        return jsonify({"erro": str(e)}), 500

@app.route("/")
def home():
    return "API de criação de pastas ativa!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

