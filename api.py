import requests

URL_API = "https://brasilapi.com.br/api/banks/v1"

def buscar_bancos_api():
    """Consulta a BrasilAPI e retorna uma lista de dicionários com os bancos."""
    try:
        response = requests.get(URL_API, timeout=10)
        response.raise_for_status()
        return response.json()  # Retorna a lista de dicionários
    except requests.RequestException as e:
        print(f"Erro ao acessar a API: {e}")
        return []