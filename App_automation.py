from flask import Flask, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import requests
import urllib3

# Desativar avisos de certificado SSL auto-assinado local
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
scheduler = BackgroundScheduler()
scheduler.start()

# Configuração da API do GoPhish
GOPHISH_API_KEY = "My API KEY"
GOPHISH_HOST = "https://127.0.0.1:3333"

headers = {
    "Authorization": f"Bearer {GOPHISH_API_KEY}",
    "Content-Type": "application/json"
}

def disparar_campanha_gophish(email_destino, nome, template_name, page_name, id_etapa):
    """Cria o grupo e lança a campanha via API REST do GoPhish com a URL estática para tracking."""
    try:
        timestamp_id = int(datetime.now().timestamp())
        group_name = f"Grupo_{email_destino}_{id_etapa}_{timestamp_id}"

        # 1. Criar Grupo de Alvo Único
        group_payload = {
            "name": group_name,
            "targets": [{"first_name": nome, "last_name": "", "email": email_destino}]
        }
        res_group = requests.post(f"{GOPHISH_HOST}/api/groups/", json=group_payload, headers=headers, verify=False)
        res_group.raise_for_status()
        group_data = res_group.json()

        # 2. Criar e Lançar Campanha
        campaign_payload = {
            "name": f"Campanha_{id_etapa}_{email_destino}_{timestamp_id}",
            "template": {"name": template_name},
            "page": {"name": page_name},  # <--- Injeta a Landing Page correta
            "smtp": {"name": "Brevo SMTP"},
            # Como a anomalia visual agora está no texto do e-mail, a URL da campanha
            # volta a ser fixa para garantir que o GoPhish regista os cliques e abre a página.
            "url": "https://estudo.nexodigitalweb.pt",
            "groups": [{"name": group_data["name"]}]
        }
        res_camp = requests.post(f"{GOPHISH_HOST}/api/campaigns/", json=campaign_payload, headers=headers, verify=False)
        res_camp.raise_for_status()

        print(f"[SUCESSO] Etapa {id_etapa} ({template_name}) enviada para {email_destino}")

    except Exception as e:
        print(f"[ERRO] Falha na etapa {id_etapa} para {email_destino}: {str(e)}")

@app.route('/webhook', methods=['POST'])
def receber_submissao():
    data = request.json or {}

    email = data.get('email')
    nome = data.get('nome', 'Colaborador')
    horario_str = data.get('horario_envio')

    if not email or not horario_str:
        return jsonify({"error": "Parâmetros 'email' e 'horario_envio' são obrigatórios"}), 400

    try:
        hora_base = datetime.strptime(horario_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return jsonify({"error": "Formato de data inválido. Use 'YYYY-MM-DD HH:MM:SS'"}), 400

    # Função executada pelo agendador na hora exata
    def disparar_sequencia_imediata():
        # Mapeamento com os nomes exatos das tuas imagens
        etapas = [
            {"id": "E-mail_1", "template": "email legitimo", "page": "Email Legitmio"},
            {"id": "E-mail_2", "template": "Phising tracoeiro", "page": "Phising tracoeiro"},
            {"id": "E-mail_3", "template": "Phising obvio", "page": "Phising obvio"}
        ]
        for etapa in etapas:
            disparar_campanha_gophish(email, nome, etapa["template"], etapa["page"], etapa["id"])

    # Agenda a execução
    scheduler.add_job(disparar_sequencia_imediata, 'date', run_date=hora_base)

    return jsonify({
        "status": "Agendamento guardado com sucesso",
        "email": email,
        "disparar_em": hora_base.strftime("%Y-%m-%d %H:%M:%S")
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)