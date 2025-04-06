import os
import requests

from vars import LINKS

DIRETORIO = "data"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

def download_data():
    if not os.path.exists(DIRETORIO):
        os.makedirs(DIRETORIO)

    for nome_arquivo, url in LINKS.items():
        try:
            print(f"Baixando: {url}")
            resposta = requests.get(url, headers=HEADERS)
            resposta.encoding = resposta.apparent_encoding

            if resposta.status_code == 200:
                caminho = os.path.join(DIRETORIO,  f"{nome_arquivo}.html")
                with open(caminho, "w", encoding="utf-8") as f:
                    f.write(resposta.text)
                print(f"✔️ Salvo em: {caminho}")
            else:
                print(f"❌ Erro ao acessar {url}: {resposta.status_code}")

        except Exception as e:
            print(f"❌ Erro ao baixar {url}: {e}")

def read_file(name):
    try:
        path = os.path.join("data", name)
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"[Arquivo {name} não encontrado]"
    
download_data()