from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def iniciar_driver():
    options = Options()
    # options.add_argument("--headless")  # Comenta esta línea para desactivar el modo headless
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("start-maximized")
    options.add_argument("disable-infobars")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def obtener_precio_godaddy(dominio):
    driver = iniciar_driver()
    url = f"https://www.godaddy.com/es/domainsearch/find?checkAvail=1&domainToCheck={dominio}"
    driver.get(url)
    try:
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        precio_elemento = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span[data-testid='pricing-main-price']"))
        )
        precio = precio_elemento.text.strip()
    except Exception as e:
        print(f"Error en GoDaddy: {e}")
        precio = "No disponible"
    driver.quit()
    return precio


def obtener_precio_hostinger(dominio):
    driver = None
    try:
        driver = iniciar_driver()
        url = "https://www.hostinger.co/comprar-dominio"
        driver.get(url)

        # Esperar a que la página cargue completamente
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        print("Página cargada correctamente")

        # Manejar el pop-up de cookies (si existe)
        try:
            boton_aceptar_cookies = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button#cookie-consent-accept"))
            )
            boton_aceptar_cookies.click()
            print("Pop-up de cookies cerrado")
        except Exception as e:
            print("No se encontró pop-up de cookies:", e)

        # Ingresar el dominio en el campo de búsqueda
        input_dominio = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input#h-domain-finder-header-input"))
        )
        input_dominio.clear()
        input_dominio.send_keys(dominio)
        print(f"Dominio '{dominio}' ingresado correctamente")

        # Hacer clic en el botón de búsqueda
        boton_buscar = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.h-domain-finder-header__search-btn"))
        )
        boton_buscar.click()
        print("Botón de búsqueda clickeado")

        # Esperar a que el precio del dominio esté visible
        precio_elemento = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span.h-price__number.t-h5"))
        )
        precio = precio_elemento.text.strip()
        print(f"Precio encontrado: {precio}")

        # Formatear el precio
        precio = f"COP {precio}"
    except Exception as e:
        print(f"Error en Hostinger: {e}")
        # Guardar el código fuente de la página para depuración
        if driver:
            with open("hostinger_error.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            # Tomar una captura de pantalla para depuración
            driver.save_screenshot("hostinger_error.png")
        precio = "No disponible"
    finally:
        if driver:
            driver.quit()
    return precio

app = Flask(__name__)
