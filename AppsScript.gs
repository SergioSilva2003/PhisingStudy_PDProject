function enviarParaWebhook(e) {
  var webhookUrl = "https://estudo.nexodigitalweb.pt/webhook";

  var email = "";
  var nome = "";
  var horarioEnvio = "";

  if (e && e.response) {
    var itemResponses = e.response.getItemResponses();

    for (var i = 0; i < itemResponses.length; i++) {
      var rawTitle = itemResponses[i].getItem().getTitle();
      var title = rawTitle.toLowerCase()
                          .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
                          .replace(/-/g, "");
      var response = itemResponses[i].getResponse();

      // 1. Pergunta do E-mail (procura por "pretende receber" ou "endereco")
      if (title.indexOf("pretende receber") !== -1 || title.indexOf("endereco") !== -1) {
        email = response;
      } 
      // 2. Pergunta do Horário (procura por "horario" ou "preferencial")
      else if (title.indexOf("horario") !== -1 || title.indexOf("preferencial") !== -1) {
        horarioEnvio = response;
      } 
      // 3. Pergunta do Nome (se existir no formulário)
      else if (title.indexOf("nome") !== -1) {
        nome = response;
      }
    }

    // Fallback: se o e-mail for recolhido automaticamente nas definições do Forms
    if (!email && typeof e.response.getRespondentEmail === "function") {
      email = e.response.getRespondentEmail();
    }
  }

  // Formatação e tratamento rigoroso da Data/Hora para YYYY-MM-DD HH:MM:SS
  var dataFormatada = "";
  if (horarioEnvio) {
    var d = new Date(horarioEnvio);
    if (!isNaN(d.getTime())) {
      dataFormatada = Utilities.formatDate(d, Session.getScriptTimeZone(), "yyyy-MM-dd HH:mm:ss");
    } else {
      // Se vier como string limpa do Forms (ex: "2026-11-04 23:36")
      var strData = horarioEnvio.toString().trim();
      if (strData.length === 16) { 
        dataFormatada = strData + ":00"; // Adiciona segundos ":00" se faltarem
      } else {
        dataFormatada = strData;
      }
    }
  }

  var payload = {
    "email": email ? email.toString().trim() : "",
    "nome": nome ? nome.toString().trim() : "Colaborador",
    "horario_envio": dataFormatada
  };

  Logger.log("Payload correto a enviar ao Flask: " + JSON.stringify(payload));

  if (!payload.email || !payload.horario_envio) {
    Logger.log("ERRO LOCAL: Email ou horario_envio estao vazios.");
    return;
  }

  var options = {
    "method": "post",
    "contentType": "application/json",
    "payload": JSON.stringify(payload),
    "muteHttpExceptions": true
  };

  try {
    var response = UrlFetchApp.fetch(webhookUrl, options);
    Logger.log("Resposta do Servidor: " + response.getContentText());
  } catch (err) {
    Logger.log("Erro na ligacao ao Webhook: " + err.toString());
  }
}