import requests
from PIL import Image
from io import BytesIO

url = "https://novelfire.net/server-1/chrysalis.jpg"

# Definimos cabeceras para simular un navegador Chrome en Windows
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Referer": "https://novelfire.net/" # A veces también verifican desde qué página vienes
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status() # Lanza una excepción si hay un error (403, 404, etc.)

    img = Image.open(BytesIO(response.content))
    img.show()

except requests.exceptions.HTTPError as e:
    print(f"Error HTTP: {e}")
except Exception as e:
    print(f"Ocurrió un error: {e}")