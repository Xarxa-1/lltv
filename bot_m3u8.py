import time
import json
from selenium import webdriver  # Selenium estàndard, sense wire
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# 1. Configurar opcions del navegador per activar el registre de xarxa
opcions = webdriver.ChromeOptions()
opcions.add_argument('--headless=new')  # Mode ocult modern
opcions.add_argument('--no-sandbox')
opcions.add_argument('--disable-dev-shm-usage')
opcions.add_argument('--disable-gpu')

# CRÍTIC: Diem a Chrome que enregistri tota l'activitat de xarxa
opcions.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

print("Iniciant Google Chrome a GitHub Actions...")
servei = Service(ChromeDriverManager().install())
navegador = webdriver.Chrome(service=servei, options=opcions)

url_web = "https://lleidatv.cat"
url_m3u8_trobada = None

try:
    print(f"Navegant cap a: {url_web}")
    navegador.get(url_web)
    
    print("Esperant 15 segons perquè el reproductor carregui el flux m3u8...")
    time.sleep(15)

    # 2. Extreure els registres de rendiment del propi Chrome
    print("Analitzant el registre de connexions de Chrome...")
    registres = navegador.get_log('performance')
    
    for entrada in registres:
        missatge = json.loads(entrada['message'])['message']
        
        # Busquem mètodes de xarxa on s'hagi enviat una petició (Network.requestWillBeSent)
        if 'method' in missatge and missatge['method'] == 'Network.requestWillBeSent':
            url_peticio = missatge['params']['request']['url']
            
            # Filtrem si la URL conté .m3u8
            if '.m3u8' in url_peticio:
                url_m3u8_trobada = url_peticio
                print(f"¡ÈXIT! URL m3u8 interceptada: {url_m3u8_trobada}")
                break

    # 3. Crear el fitxer url.m3u
    if url_m3u8_trobada:
        nom_arxiu = "url.m3u"
        with open(nom_arxiu, "w", encoding="utf-8") as arxiu:
            arxiu.write("#EXTM3U\n")
            arxiu.write("#EXTINF:-1,Lleida TV En Directe\n")
            arxiu.write(f"{url_m3u8_trobada}\n")
        print(f"El fitxer '{nom_arxiu}' s'ha creat correctament al repositori.")
    else:
        print("⚠️ Alerta: La web ha carregat, però no s'ha trobat cap enllaç .m3u8 en els registres.")

except Exception as e:
    print(f"❌ Error durant l'execució: {e}")
    raise e

finally:
    navegador.quit()
    print("Navegador tancat.")
