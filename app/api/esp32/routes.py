from rebar import registry
from flask import request, jsonify
import requests
import socket
import ipaddress
import concurrent.futures


def get_local_subnet():
    """
    Detecta la IP local del servidor y deduce la subred /24 correspondiente.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # No necesita conectarse realmente, solo fuerza a tomar la IP local usada para salir
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
    finally:
        s.close()

    subnet = ipaddress.ip_network(local_ip + '/24', strict=False)
    print(f"🔍 Escaneando red: {subnet}")
    return subnet


def check_esp32(ip):
    try:
        print(f"🔎 Revisando IP: {ip}")
        r = requests.get(f"http://{ip}/status", timeout=3)
        if r.ok:
            print(f"✅ Respuesta de {ip}: {r.text}")
        if r.ok and "esp" in r.text.lower():
            return ip
    except Exception as e:
        print(f"❌ {ip} falló: {e}")
    return None


def find_esp32():
    subnet = get_local_subnet()
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(check_esp32, str(ip)) for ip in subnet.hosts()]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                return result
    return None


@registry.handles(rule="/esp32-ip", method="GET")
def get_esp32_ip():
    ip = find_esp32()
    if ip:
        return jsonify({"ip": ip})
    else:
        return jsonify({"error": "ESP32 no encontrado"}), 404
