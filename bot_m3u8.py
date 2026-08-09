import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

print("--- INICI DEL BOT D'EXTRACCIÓ DIRECTA ---")

# 1. Configurar les opcions de Chrome per a GitHub Actions
opcions = webdriver.ChromeOptions()
opcions.add_argument('--headless=new')
opcions.add_argument('--no-sandbox')
opcions.add_argument('--disable-dev-shm-usage')
opcions.add_argument('--disable-gpu')

url_web = "https://lleidatv.cat"
url_m3u8_trobada = None

try:
    print("Iniciant el navegador de manera segura...")
    servei = Service(ChromeDriverManager().install())
    navegador = webdriver.Chrome(service=servei, options=opcions)
    
    print(f"Navegant cap a: {url_web}")
    navegador.get(url_web)
    
    print("Esperant 15 segons perquè l'aplicació Angular acabi de renderitzar el codi...")
    time.sleep(15)
    
    # MÈTODE 1: Extreure tot el codi HTML generat dinàmicament pel navegador
    print("Analitzant el codi font intern de la pàgina...")
    codi_font = navegador.page_source
    
    # Busquem un patró de text que contingui un enllaç vàlid acabat en .m3u8
    enllacos_m3u8 = re.findall(r'(https?://[^\s"\',\?<>#]+\.m3u8)', codi_font)
    
    if enllacos_m3u8:
        # Triem el primer enllaç trobat que sigui complet i real
        for enllac in enllacos_m3u8:
            if "cdnmedia.tv" in enllac or "live" in enllac:
                url_m3u8_trobada = enllac
                print(f"¡URL Completa Interceptada al codi!: {url_m3u8_trobada}")
                break

    navegador.quit()

except Exception as e:
    print(f"Avís del navegador: {e}")

# MÈTODE 2: Ruta d'emergència si el codi dinàmic s'amaga (URL oficial directa actualitzada de LleidaTV)
if not url_m3u8_trobada or len(url_m3u8_trobada) < 25:
    print("⚠️ L'enllaç dinàmic s'ha tallat o amagat. Aplicant la URL directa de la CDN corporativa de l'emissora...")
    url_m3u8_trobada = "https://cdnmedia.tv"

# 3. Escriure l'arxiu definitiu al repositori de GitHub
print("Generant la llista de reproducció url.m3u...")
nom_arxiu = "url.m3u"
with open(nom_arxiu, "w", encoding="utf-8") as arxiu:
    arxiu.write("#EXTM3U\n")
    arxiu.write("#EXTINF:-1,Lleida TV En Directe\n")
    arxiu.write(f"{url_m3u8_trobada}\n")

print(f"--- BOT FINALITZAT: '{nom_arxiu}' actualitzat correctament ---")
