import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

print("--- INICI DEL BOT D'ALTA PRECISIÓ ---")

opcions = webdriver.ChromeOptions()
opcions.add_argument('--headless=new')
opcions.add_argument('--no-sandbox')
opcions.add_argument('--disable-dev-shm-usage')
opcions.add_argument('--disable-gpu')
opcions.add_argument('--mute-audio')
opcions.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

url_web = "https://lleidatv.cat"
url_m3u8_trobada = None

try:
    print("Instal·lant i iniciant Google Chrome...")
    servei = Service(ChromeDriverManager().install())
    navegador = webdriver.Chrome(service=servei, options=opcions)
    
    print(f"Navegant cap a la plataforma de vídeo: {url_web}")
    navegador.get(url_web)
    
    # Intentar acceptar cookies o fer clic a la pantalla per forçar la intercepció de xarxa
    print("Simulant interacció humana per activar el reproductor...")
    time.sleep(6)
    try:
        # Busquem qualsevol element que pugui ser un botó de reproducció o l'acceptació de cookies
        botons = navegador.find_elements(By.TAG_NAME, "button")
        for boto in botons:
            if "aceptar" in boto.text.lower() or "play" in boto.text.lower():
                boto.click()
                print("Botó clicat dinàmicament per activar el directe.")
                break
    except:
        pass

    print("Esperant 10 segons addicionals perquè el flux m3u8 es registri...")
    time.sleep(10)
    
    print("Escanejant l'historial de connexions internes de la CDN...")
    registres = navegador.get_log('performance')
    
    for entrada in registres:
        missatge = json.loads(entrada['message'])['message']
        if 'method' in missatge and missatge['method'] == 'Network.requestWillBeSent':
            url_peticio = missatge['params']['request']['url']
            
            # Filtrem que provingui del servidor de vídeo i contingui l'extensió m3u8 correcta
            if '.m3u8' in url_peticio and 'live' in url_peticio.lower():
                url_m3u8_trobada = url_peticio
                print(f"¡URL Real Capturada!: {url_m3u8_trobada}")
                break
                
    navegador.quit()

except Exception as e:
    print(f"Avís del navegador controlat: {e}")

# Si no ha caçat cap enllaç dinàmic, posem la URL de transmissió directa oficial de la seva plataforma
if not url_m3u8_trobada or "playlist.m3u8" in url_m3u8_trobada:
    url_m3u8_trobada = "https://cdnmedia.tv"

print("Escrivint la llista de reproducció definitiva .m3u...")
nom_arxiu = "url.m3u"
with open(nom_arxiu, "w", encoding="utf-8") as arxiu:
    arxiu.write("#EXTM3U\n")
    arxiu.write("#EXTINF:-1,Lleida TV En Directe\n")
    arxiu.write(f"{url_m3u8_trobada}\n")

print(f"--- BOT FINALITZAT: '{nom_arxiu}' desat al repositori ---")
