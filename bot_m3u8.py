import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# 1. Configurar opcions del navegador per activar el registre de xarxa de Chrome
opcions = webdriver.ChromeOptions()
opcions.add_argument('--headless=new')  # Mode ocult modern obligatori per a servidors
opcions.add_argument('--no-sandbox')
opcions.add_argument('--disable-dev-shm-usage')
opcions.add_argument('--disable-gpu')
opcions.add_argument('--mute-audio')

# Forçar els registres de rendiment d'estil de xarxa (Network)
opcions.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

print("Iniciant Google Chrome a GitHub Actions...")
servei = Service(ChromeDriverManager().install())
navegador = webdriver.Chrome(service=servei, options=opcions)

# CRÍTIC: Fes servir la URL de la plataforma de streaming, NO la web genèrica
url_web = "https://ott.lleidatv.cat/ca/pl/6"
url_m3u8_trobada = None

try:
    print(f"Navegant cap a: {url_web}")
    navegador.get(url_web)
    
    # Temps d'espera ampli perquè es carregui el reproductor i accepti la sessió
    print("Esperant 15 segons perquè el reproductor iniciï el flux m3u8...")
    time.sleep(15)

    # 2. Llegir el diari d'operacions internas del propi navegador Chrome
    print("Analitzant el registre de connexions de xarxa d'alta precisió...")
    registres = navegador.get_log('performance')
    
    for entrada in registres:
        missatge = json.loads(entrada['message'])['message']
        
        # Capturem tant peticions enviades com respostes de servidor rebudes
        if 'method' in missatge and missatge['method'] in ['Network.requestWillBeSent', 'Network.responseReceived']:
            params = missatge.get('params', {})
            
            # Obtenir l'enllaç depenent del tipus d'esdeveniment detectat
            url_peticio = ""
            if 'request' in params:
                url_peticio = params['request'].get('url', '')
            elif 'response' in params:
                url_peticio = params['response'].get('url', '')
            
            # Filtrem si la URL conté l'enllaç de vídeo de l'emissora (.m3u8)
            if '.m3u8' in url_peticio:
                url_m3u8_trobada = url_peticio
                print(f"¡ÈXIT! URL m3u8 interceptada de LleidaTV: {url_m3u8_trobada}")
                break

    # 3. Escriure l'arxiu definitiu al repositori de GitHub
    if url_m3u8_trobada:
        nom_arxiu = "url.m3u"
        with open(nom_arxiu, "w", encoding="utf-8") as arxiu:
            arxiu.write("#EXTM3U\n")
            arxiu.write("#EXTINF:-1,Lleida TV En Directe\n")
            arxiu.write(f"{url_m3u8_trobada}\n")
        print(f"El fitxer '{nom_arxiu}' s'ha creat de manera immillorable.")
    else:
        print("⚠️ Alerta extrema: No s'ha interceptat cap fitxer de vídeo .m3u8 en aquesta sessió.")

except Exception as e:
    print(f"❌ Error crític controlat: {e}")
    raise e

finally:
    navegador.quit()
    print("Navegador tancat i memòria alliberada.")
