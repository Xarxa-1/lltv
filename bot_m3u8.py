import time
import json
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

print("--- INICI DEL BOT LLEIDATV DEFINITIU ---")

# 1. Configurar opcions ultra-segures per a GitHub Actions i captura de xarxa
opcions = webdriver.ChromeOptions()
opcions.add_argument('--headless=new')
opcions.add_argument('--no-sandbox')
opcions.add_argument('--disable-dev-shm-usage')
opcions.add_argument('--disable-gpu')
opcions.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

url_web = "https://ott.lleidatv.cat/ca/pl/6"
url_m3u8_trobada = None

try:
    print("Iniciant el navegador virtual Google Chrome...")
    servei = Service(ChromeDriverManager().install())
    navegador = webdriver.Chrome(service=servei, options=opcions)
    
    print(f"Navegant directament cap a la plataforma de vídeo: {url_web}")
    navegador.get(url_web)
    
    print("Esperant 20 segons per forçar que el reproductor negociï la connexió del directe...")
    time.sleep(20)
    
    print("Analitzant tot l'historial de connexions IP de la CDN corporativa...")
    registres = navegador.get_log('performance')
    
    # Bucle per escanear totes les comunicacions del navegador en segon pla
    for entrada in registres:
        missatge = json.loads(entrada['message'])['message']
        if 'method' in missatge and missatge['method'] == 'Network.requestWillBeSent':
            url_peticio = missatge['params']['request']['url']
            
            # FILTRE COMPLET PER LA CDN DE TELEVISIÓ: busquem l'enllaç de veritat que conté la transmissió en viu
            if '.m3u8' in url_peticio and ('liveingesta' in url_peticio or 'lleidatv' in url_peticio):
                url_m3u8_trobada = url_peticio
                print(f"¡ÈXIT EXTREM! URL capturada sencera: {url_m3u8_trobada}")
                break
                
    navegador.quit()

except Exception as e:
    print(f"Avís controlat durant l'escaneig: {e}")

# 2. RUTA DE CONTINGÈNCIA BLINDADA (Si el directe s'ha tallat, posem el flux matriu actiu de la TDT de LleidaTV)
if not url_m3u8_trobada or len(url_m3u8_trobada) < 30:
    print("⚠️ Avís: No s'ha interceptat cap petició a temps. Escrivint el flux matriu alternatiu de seguretat...")
    url_m3u8_trobada = "https://liveingesta318.cdnmedia.tv/lleidatvlive/smil:live.smil/playlist.m3u8?DVR"

# 3. Escriure l'arxiu de llista IPTV final definitiu (.m3u)
print("Escriu el fitxer url.m3u...")
nom_arxiu = "url.m3u"
with open(nom_arxiu, "w", encoding="utf-8") as arxiu:
    arxiu.write("#EXTM3U\n")
    arxiu.write("#EXTINF:-1,Lleida TV En Directe\n")
    arxiu.write(f"{url_m3u8_trobada}\n")

print(f"--- BOT FINALITZAT: '{nom_arxiu}' generat correctament amb la URL llarga ---")
