import requests
import os
import json

API_URL = "https://www.solvia.es/api/inmuebles/v2/buscarInmuebles"
HEADERS = {"Content-Type": "application/json"}

# Configura aquí tu payload (p.ej. pisos en venta, viviendas)
payload = {
    "tipoOperacion": "COMPRA",
    "idCategoriaTipoVivienda": "1",  # viviendas
    "paginacion": {"numeroPagina": 0, "tamanoPagina": 20}
}

DATA_FILE = "pisos_guardados.json"

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

def cargar_pisos_guardados():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return set(json.load(f))
    return set()

def guardar_pisos(pisos):
    with open(DATA_FILE, "w") as f:
        json.dump(list(pisos), f)

def obtener_pisos():
    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        lista = data.get("listaResultados", [])
        pisos = {str(inmueble["id"]) for inmueble in lista}
        return pisos, lista
    except Exception as e:
        enviar_mensaje(f"⚠️ Error al consultar Solvia: {e}")
        return set(), []

def enviar_mensaje(texto):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": texto
    }
    requests.post(url, data=payload)

def main():
    pisos_guardados = cargar_pisos_guardados()
    pisos_actuales_ids, pisos_actuales_data = obtener_pisos()
    nuevos = pisos_actuales_ids - pisos_guardados

    if nuevos:
        for piso in pisos_actuales_data:
            if str(piso["id"]) in nuevos:
                msg = (
                    f"🏠 *Nuevo piso detectado*\n\n"
                    f"ID: {piso['id']}\n"
                    f"Precio: {piso.get('precio', 'No disponible')} €\n"
                    f"Dirección: {piso.get('direccion', 'No disponible')}\n"
                    f"Más info: https://www.solvia.es/inmueble/{piso['id']}"
                )
                enviar_mensaje(msg)
        pisos_guardados.update(nuevos)
        guardar_pisos(pisos_guardados)
    else:
        print("No hay pisos nuevos.")

if __name__ == "__main__":
    main()

