from flask import Flask, request, jsonify
import os
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route("/criar-pastas", methods=["POST"])
def criar_pastas():
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
            pasta_lider = os.path.join(pasta_periodo_completa, email)
            os.makedirs(pasta_lider, exist_ok=True)

            with open(os.path.join(pasta_lider, "autoavaliacao.csv"), "w") as f:
                f.write("Aguardando envio da autoavaliacao...\n")

            with open(os.path.join(pasta_lider, "equipe.csv"), "w") as f:
                f.write("Aguardando respostas da equipe...\n")

        return jsonify({"mensagem": "Pastas criadas com sucesso."})

    except Exception as e:
        print("Erro ao criar pastas:", str(e))
        return jsonify({"erro": str(e)}), 500

@app.route("/listar-pastas", methods=["GET"])
def listar_pastas():
    estrutura = []
    base_dir = "dados_projetos"

    for root, dirs, files in os.walk(base_dir):
        nivel = root.replace(base_dir, "").lstrip(os.sep)
        estrutura.append({
            "caminho": nivel if nivel else base_dir,
            "arquivos": files
        })

    return jsonify(estrutura)

@app.route("/")
def home():
    return "API de criação de pastas ativa!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
