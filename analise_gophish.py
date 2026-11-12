import requests
from datetime import datetime
import urllib3

# Ignorar avisos de certificados SSL auto-assinados da porta 3333
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- CONFIGURAÇÕES ---
API_KEY = "My api key"
GOPHISH_URL = "https://127.0.0.1:3333"
# ---------------------

def main():
    url_todas = f"{GOPHISH_URL}/api/campaigns/?api_key={API_KEY}"
    resposta = requests.get(url_todas, verify=False)

    if resposta.status_code != 200:
        print("Erro ao ligar à API do GoPhish. Verifica a tua API Key.")
        return

    campanhas = resposta.json()

    historico_cliques = {}
    todos_alvos = set()

    for camp in campanhas:
        nome_campanha = camp.get("name", "")

        tipo_campanha = None
        if "Campanha_E-mail_1" in nome_campanha:
            tipo_campanha = 1
        elif "Campanha_E-mail_2" in nome_campanha:
            tipo_campanha = 2
        elif "Campanha_E-mail_3" in nome_campanha:
            tipo_campanha = 3

        if tipo_campanha is None:
            continue

        for evento in camp.get("timeline", []):
            email = evento.get("email")
            if email:
                todos_alvos.add(email)

            if evento["message"] == "Clicked Link":
                tempo_str = evento["time"].split(".")[0].replace("Z", "")
                tempo_clique = datetime.strptime(tempo_str, "%Y-%m-%dT%H:%M:%S")

                if email not in historico_cliques:
                    historico_cliques[email] = []

                historico_cliques[email].append((tempo_clique, tipo_campanha))

    print("-" * 60)
    print("RESULTADO FINAL POR PARTICIPANTE (Baseado no 1º Clique)")
    print("-" * 60)

    estatistica_final = {1: 0, 2: 0, 3: 0}
    clicaram = set()

    for email, lista_cliques in historico_cliques.items():
        clicaram.add(email)
        lista_cliques.sort(key=lambda x: x[0])

        primeiro_clique_tempo = lista_cliques[0][0]
        primeira_campanha_clicada = lista_cliques[0][1]

        estatistica_final[primeira_campanha_clicada] += 1
        tempo_formatado = primeiro_clique_tempo.strftime("%d/%m/%Y às %H:%M:%S")
        print(f"Participante: {email}")

        # AQUI ESTÁ A CORREÇÃO DA LÓGICA DE TEXTO
        if primeira_campanha_clicada == 1:
            print(f" -> Resultado: ACERTOU - Interagiu com o e-mail Legítimo (Campanha 1)")
        else:
            print(f" -> Resultado: CAIU NO PHISHING - Escolheu a Campanha {primeira_campanha_clicada}")

        print(f" -> Hora exata: {tempo_formatado}\n")

    nao_clicaram = todos_alvos - clicaram

    print("-" * 60)
    print("RESUMO DO ESTUDO: Qual foi a primeira escolha?")
    print("-" * 60)

    for camp in [1, 2, 3]:
        if camp == 1:
            nome = "1 (Legítima - Ação Correta)"
        elif camp == 2:
            nome = "2 (Phishing Difícil - Enganados)"
        else:
            nome = "3 (Phishing Óbvio - Enganados)"

        total = estatistica_final[camp]
        print(f"Campanha {nome}: {total} pessoas.")

    print(f"\nParticipantes que NÃO clicaram em nenhum link: {len(nao_clicaram)}")
    if len(nao_clicaram) > 0:
        print("Lista de quem não clicou (os mais cautelosos):")
        for email in nao_clicaram:
            print(f" -> {email}")

if __name__ == "__main__":
    main()