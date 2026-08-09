import time
from seleniumwire import webdriver  # Utilitzem selenium-wire en comptes del selenium normal
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# 1. Configurar les opcions del navegador Chrome
opcions = webdriver.ChromeOptions()
opcions.add_argument('--headless')  # Execució en segon pla (sense obrir la finestra gràfica)
opcions.add_argument('--no-sandbox')
opcions.add_argument('--disable-dev-shm-usage')

print("Iniciant el navegador virtual...")
# 2. Arrencar el navegador amb el motor de cerca de selenium-wire
servei = Service(ChromeDriverManager().install())
navegador = webdriver.Chrome(service=servei, options=opcions)

url_web = "https://ott.lleidatv.cat/ca/pl/6"
url_m3u8_trobada = None

try:
    print(f"Navegant cap a: {url_web}")
    navegador.get(url_web)
    
    print("Esperant que el reproductor carregui el flux de vídeo (15 segons)...")
    time.sleep(15)  # Donem temps a la web per executar l'Angular i connectar el directe

    # 3. Revisar totes les peticions de xarxa que ha fet la pàgina web
    print("Analitzant les peticions de xarxa...")
    for peticio in navegador.requests:
        if peticio.response:
            # Busquem qualsevol URL que contingui '.m3u8'
            if '.m3u8' in peticio.url:
                url_m3u8_trobada = peticio.url
                print(f"¡URL trobada!: {url_m3u8_trobada}")
                break  # Hem trobat l'enllaç, podem parar el bucle

    # 4. Si l'hem trobat, el guardem en el format d'arxiu de llista de reproducció (.m3u)
    if url_m3u8_trobada:
        nom_arxiu = "url.m3u"
        with open(nom_arxiu, "w", encoding="utf-8") as arxiu:
            arxiu.write("#EXTM3U\n")
            arxiu.write("#EXTINF:-1,Lleida TV En Directe\n")
            arxiu.write(f"{url_m3u8_trobada}\n")
        print(f"L'enllaç s'ha desat correctament a '{nom_arxiu}'")
    else:
        print("No s'ha detectat cap enllaç .m3u8 durant la càrrega de la pàgina.")

finally:
    # Tanquem sempre el navegador per alliberar la memòria de l'ordinador
    navegador.quit()
    print("Navegador tancat.")
