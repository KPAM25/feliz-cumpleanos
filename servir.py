# -*- coding: utf-8 -*-
"""Sirve la tarjeta en la red local y prepara el código QR."""

import socket
import sys
import threading
import time
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import qrcode
import qrcode.image.svg

PORT = 8765
ROOT = Path(__file__).resolve().parent

sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
sys.stderr.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)


def ip_local():
    prueba = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        prueba.connect(("8.8.8.8", 80))
        return prueba.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        prueba.close()


def crear_qr(url):
    codigo = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=12,
        border=2,
    )
    codigo.add_data(url)
    codigo.make(fit=True)
    imagen = codigo.make_image(image_factory=qrcode.image.svg.SvgPathImage)
    imagen.save(ROOT / "qr.svg")


def crear_pagina_qr(url):
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light">
  <title>QR de la tarjeta</title>
  <style>
    :root {{ color-scheme: light; }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100dvh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 28px 16px;
      font-family: "Segoe UI", sans-serif;
      color: #3a2924;
      background: #f6d7c6 url("assets/fondo.jpg") center / 540px repeat;
    }}
    .panel {{
      width: min(460px, 100%);
      background: #fffaf6;
      border-radius: 28px;
      padding: 28px 24px 24px;
      box-shadow: 0 22px 50px rgba(92, 42, 36, 0.16);
      text-align: center;
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: 1.55rem;
      line-height: 1.2;
    }}
    p {{ margin: 0; line-height: 1.45; }}
    ol {{
      margin: 16px auto 0;
      padding: 0 0 0 18px;
      text-align: left;
      max-width: 340px;
    }}
    li + li {{ margin-top: 8px; }}
    .codigo {{
      display: inline-block;
      margin-top: 18px;
      padding: 14px;
      background: #fff;
      border-radius: 16px;
      line-height: 0;
    }}
    .codigo img {{ width: min(280px, 72vw); height: auto; }}
    .url {{
      margin-top: 14px;
      font-size: 0.95rem;
      word-break: break-all;
    }}
    a {{ color: #9d3048; }}
    .aviso {{
      margin-top: 16px;
      font-size: 0.92rem;
      color: #6a3e32;
    }}
  </style>
</head>
<body>
  <main class="panel">
    <h1>Escanea para abrir la tarjeta</h1>
    <p>Deja esta pantalla visible y usa la cámara del celular.</p>
    <ol>
      <li>Conecta el celular a la misma red Wi-Fi que esta computadora.</li>
      <li>Abre la cámara y apunta al código.</li>
      <li>Toca el enlace que aparece.</li>
    </ol>
    <div class="codigo">
      <img src="qr.svg" alt="Código QR de la tarjeta de cumpleaños">
    </div>
    <p class="url">Si la cámara no lo lee, abre en el celular:<br><strong>{url}</strong></p>
    <p class="aviso">Si Windows pregunta si permite el acceso de Python, elige redes privadas. La computadora debe seguir encendida, con esta ventana abierta.</p>
    <p class="aviso"><a href="/">Ver la tarjeta en esta computadora</a></p>
  </main>
</body>
</html>
"""
    (ROOT / "qr.html").write_text(html, encoding="utf-8")


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, formato, *args):
        sys.stdout.write("%s - %s\n" % (self.address_string(), formato % args))


def abrir_navegador():
    time.sleep(0.6)
    webbrowser.open(f"http://127.0.0.1:{PORT}/qr.html")


def main():
    ip = ip_local()
    url = f"http://{ip}:{PORT}/"
    crear_qr(url)
    crear_pagina_qr(url)

    print()
    print("Tarjeta lista.")
    print(f"En esta computadora: http://127.0.0.1:{PORT}/")
    print(f"En el celular, escanea el QR o abre: {url}")
    print("Deja esta ventana abierta. Para cerrar, presiona Ctrl+C.")
    print()

    threading.Thread(target=abrir_navegador, daemon=True).start()
    ThreadingHTTPServer.allow_reuse_address = True
    servidor = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
    finally:
        servidor.server_close()


if __name__ == "__main__":
    main()
