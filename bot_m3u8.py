import time
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# CONFIGURACIÓ CRÍTICA PER A GITHUB ACTIONS:
# Evita que selenium-wire s'intenti connectar a proxies externs del servidor
seleniumwire_options = {
    'connection_timeout': None,
    'verify_ssl': False,
    'suppress_connection_errors': True
}

opcions = webdriver.ChromeOptions()
opcions.add_argument('--headless=new')  # Mode ocult actualitzat
opcions.add_argument('--no-sandbox')
opcions.add_argument('--disable-dev-shm-usage')
opcions.add_argument('--disable-gpu')
opcions.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

print("Iniciant el navegador virtual optimitzat per a servidors...")

try:
    servei = Service(ChromeDriverManager().install())
    # Afegim les 'seleniumwire_options' aquí per evitar el xoc amb el sistema de GitHub
    navegador = webdriver.Chrome(
        service=servei, 
        options=opcions, 
        seleniumwire_options=seleniumwire_options
    )
    
    url_web = "https://lleidatv.cat"
    url_m3u8_trobada = None

    print(f"Navegant cap a: {url_web}")
    navegador.get(url_web)
    
    print("Esperant que el reproductor i els scripts carreguin el vídeo (12 segons)...")
    time.sleep(12)

    print("Analitzant el trànsit de xarxa en segon pla...")
    for peticio in navegador.requests:
        if peticio.response:
            # Imprimim les peticions m3u8 que veiem per fer depuració a la consola de GitHub
            if '.m3u8' in peticio.url:
                url_m3u8_trobada = peticio.url
                print(f"¡URL DETECTADA AMB ÈXIT!: {url_m3u8_trobada}")
                break

    if url_m3u8_trobada:
        nom_arxiu = "url.m3u"
        with open(nom_arxiu, "w", encoding="utf-8") as arxiu:
            arxiu.write("#EXTM3U\n")
            arxiu.write("#EXTINF:-1,Lleida TV En Directe\n")
            arxiu.write(f"{url_m3u8_trobada}\n")
        print(f"Arxiu '{nom_arxiu}' desat correctament.")
    else:
        print("⚠️ Alerta: El reproductor ha carregat però no s'ha interceptat cap petició de tipus .m3u8.")

except Exception as e:
    print(f"❌ S'ha produït un error físic durant l'execució: {e}")
    raise e  # Forcem l'error perquè GitHub sàpiga que ha fallat

finally:
    try:
        navegador.quit()
        print("Navegador tancat correctament.")
    except:
        pass
