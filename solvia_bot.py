import requests
import json
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

API_URL = "https://www.solvia.es/api/inmuebles/v2/buscarInmuebles"

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}

# Payload para la consulta, ajusta según necesites
PAYLOAD = {
    "tipoOperacion": "COMPRA",
    "idCategoriaTipoVivienda": "1",
    "paginacion": {"numeroPagina": 0, "tamanoPagina": 20},
}

def enviar_mensaje(texto):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    params = {"chat_id": CHAT_ID, "text": texto}
    try:
        r = requests.get(url, params=params)
        r.raise_for_status()
    except Exception as e:
        print(f"Error enviando mensaje a Telegram: {e}")

def cargar_pisos_guardados():
    if not os.path.exists("pisos_guardados.json"):
        return set()
    with open("pisos_guardados.json", "r") as f:
        try:
            data = json.load(f)
            return set(data)
        except:
            return set()

def guardar_pisos_guardados(pisos_ids):
    with open("pisos_guardados.json", "w") as f:
        json.dump(list(pisos_ids), f)

def main():
    # Aviso inicial
    enviar_mensaje("🚀 Arrancando servicio automático de búsqueda de pisos.")

    pisos_guardados = cargar_pisos_guardados()

    try:
        response = requests.post(API_URL, headers=HEADERS, json=PAYLOAD)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Error al llamar API de Solvia: {e}")
        enviar_mensaje(f"❌ Error al consultar Solvia: {e}")
        return

    pisos = data.get("datos", {}).get("resultados", [])

    pisos_actuales_ids = set()
    nuevos = []

    for piso in pisos:
        id_piso = piso.get("idInmueble")
        pisos_actuales_ids.add(id_piso)
        if id_piso not in pisos_guardados:
            nuevos.append(piso)

    if not nuevos:
        mensaje = "🔎 No se encontraron pisos nuevos esta vez."
        print(mensaje)
        enviar_mensaje(mensaje)
    else:
        for piso in nuevos:
            id_piso = piso.get("idInmueble")
            precio = piso.get("precioVenta", "N/A")
            direccion = piso.get("direccion", {}).get("direccion", "Sin dirección")
            url_piso = f"https://www.solvia.es/inmueble/{id_piso}"
            mensaje = (
                f"🏠 Nuevo piso detectado\n\n"
                f"ID: {id_piso}\n"
                f"Precio: {precio} €\n"
                f"Dirección: {direccion}\n"
                f"Más info: {url_piso}"
            )
            print(mensaje)
            enviar_mensaje(mensaje)

    # Actualiza lista de pisos guardados
    pisos_guardados.update(pisos_actuales_ids)
    guardar_pisos_guardados(pisos_guardados)


if __name__ == "__main__":
    main()
