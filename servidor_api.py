from flask import Flask, jsonify
from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import threading
import time
import os
import sys
import json
import logging

# --- CORREÇÃO DE CAMINHO ---
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)

# --- SILENCIADOR DE LOGS DO FLASK (Para não poluir o terminal) ---
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
# -----------------------------------------------------------------

# ==========================================
# ⚙️ SUAS CREDENCIAIS E MEMÓRIA BLINDADA
# ==========================================
USUARIO_ESPORTIVA = "SEU_EMAIL_AQUI@gmail.com"
SENHA_ESPORTIVA = "SUA_SENHA_AQUI"

ARQUIVO_MEMORIA = os.path.join(application_path, "memoria_bacbo.json")
historico_global = []

def carregar_memoria():
    global historico_global
    if os.path.exists(ARQUIVO_MEMORIA):
        try:
            with open(ARQUIVO_MEMORIA, "r") as f:
                historico_global = json.load(f)
            print(f"🧠 Memória restaurada com sucesso! Voltando com {len(historico_global)} rodadas salvas.")
        except:
            historico_global = []

def salvar_memoria():
    try:
        with open(ARQUIVO_MEMORIA, "w") as f:
            json.dump(historico_global, f)
    except: pass

def atualizar_memoria(nova_leitura_invertida):
    global historico_global
    if not historico_global:
        historico_global = nova_leitura_invertida
        salvar_memoria()
        return

    assinatura = historico_global[:8]
    novas_bolinhas = []
    achou_conexao = False
    
    for i in range(len(nova_leitura_invertida)):
        if nova_leitura_invertida[i:i+8] == assinatura:
            novas_bolinhas = nova_leitura_invertida[:i]
            achou_conexao = True
            break
            
    if achou_conexao:
        if len(novas_bolinhas) > 0:
            historico_global = novas_bolinhas + historico_global
            salvar_memoria()
    else:
        historico_global = nova_leitura_invertida
        salvar_memoria()
        
    if len(historico_global) > 10000:
        historico_global = historico_global[:10000]
        salvar_memoria()

def login_esportiva_bet(driver):
    print("\n" + "█"*40)
    print("🔐 LOGIN AUTOMÁTICO NA ESPORTIVA.BET (SERVIDOR API)")
    print("█"*40)

    driver.set_window_size(1920, 1080)

    arquivo_credenciais = os.path.join(application_path, "credenciais_esportiva.txt")
    usuario = None
    senha = None
    
    if os.path.exists(arquivo_credenciais):
        with open(arquivo_credenciais, "r") as f:
            linhas = f.read().splitlines()
            if len(linhas) >= 2:
                usuario = linhas[0].strip()
                senha = linhas[1].strip()
        print("✅ Credenciais lidas do arquivo automático!")
    
    if not usuario or not senha:
        usuario = USUARIO_ESPORTIVA
        senha = SENHA_ESPORTIVA

    print(f"A iniciar sessão na conta: {usuario}...")
    driver.get("https://esportiva.bet.br/")
    
    try:
        driver.delete_all_cookies()
        driver.execute_script("window.localStorage.clear();")
        driver.execute_script("window.sessionStorage.clear();")
    except: pass
    
    try:
        time.sleep(5)

        def forcar_clique(texto_botao):
            xpath = f"//*[(local-name()='button' or local-name()='a' or local-name()='span' or local-name()='div') and contains(translate(., '{texto_botao.upper()}', '{texto_botao.lower()}'), '{texto_botao.lower()}')]"
            elementos = driver.find_elements(By.XPATH, xpath)
            if elementos:
                for el in reversed(elementos):
                    if el.is_displayed():
                        try:
                            driver.execute_script("arguments[0].click();", el)
                            return True
                        except: pass
            return False

        # Limpando pop-ups
        try:
            if forcar_clique("ACEITAR TODOS") or forcar_clique("ACEITAR"): pass
            time.sleep(1)
        except: pass
        try:
            if forcar_clique("ESCURO") or forcar_clique("CLARO") or forcar_clique("SALVAR"): pass
            time.sleep(1)
        except: pass
        try:
            btn_popup = driver.find_element(By.XPATH, '/html/body/div[2]/div/div[2]/span')
            if btn_popup.is_displayed(): btn_popup.click()
        except: pass
        try:
            forcar_clique("CONFIRMAR")
            time.sleep(1)
        except: pass
        try:
            forcar_clique("SIM")
            time.sleep(1)
        except: pass
        try:
            forcar_clique("SIM")
            time.sleep(1)
        except: pass
        try:
            abriu_login = forcar_clique("FAZER LOGIN")
            if not abriu_login:
                abriu_login = forcar_clique("ENTRAR")
            time.sleep(2)
        except: pass

        print("🔑 A preencher credenciais...")
        input_user = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@id='login' or @name='login' or @type='login']")))
        driver.execute_script("arguments[0].click();", input_user)
        input_user.clear()
        time.sleep(0.5)
        for letra in usuario:
            input_user.send_keys(letra)
            time.sleep(0.05)
            
        driver.execute_script("arguments[0].blur();", input_user)
        time.sleep(1)

        input_pass = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@type='password' or @id='password' or @name='password']")))
        driver.execute_script("arguments[0].click();", input_pass)
        input_pass.clear()
        time.sleep(0.5)
        for letra in senha:
            input_pass.send_keys(letra)
            time.sleep(0.05)
            
        time.sleep(1)

        try:
            btn_entrar = driver.find_element(By.XPATH, "//button[@type='submit' and contains(translate(., 'ENTRAR', 'entrar'), 'entrar')]")
            driver.execute_script("arguments[0].removeAttribute('disabled');", btn_entrar)
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", btn_entrar)
        except:
            input_pass.send_keys(Keys.ENTER)
        
        print("⏳ Aguardando a plataforma confirmar a sessão...")
        logado = False
        for i in range(15): 
            time.sleep(1)
            try:
                pass_fields = driver.find_elements(By.XPATH, "//input[@type='password']")
                if len(pass_fields) == 0 or not pass_fields[0].is_displayed():
                    print("✅ Login validado com sucesso na plataforma!")
                    logado = True
                    time.sleep(2)
                    break
            except: pass
            
            try:
                logout_msg = driver.find_element(By.XPATH, "//*[contains(text(), 'Você saiu da sua conta')]")
                if logout_msg.is_displayed():
                    driver.find_element(By.XPATH, "//*[contains(text(), 'Entrar')]").click()
                    time.sleep(3)
                    input_pass.send_keys(Keys.ENTER)
            except: pass
            
        if not logado:
            print("⚠️ Demorou muito, mas seguindo para a mesa...")
        
    except Exception as e:
        print(f"\n⚠️ Erro técnico no Login: {e}")
        raise Exception("Falha crítica no login.") 


def motor_raspagem_24h():
    global historico_global
    print("🚀 Iniciando Motor de Captura 24H (Modo Servidor)...")
    carregar_memoria() 
    
    while True:
        try:
            driver = Driver(uc=True, headless2=True)
            login_esportiva_bet(driver)
            
            print("🎲 Entrando na mesa do Bac Bo...")
            driver.get('https://esportiva.bet.br/games/evolution/bac-bo?src=ltdpeqcvodvdbektdymjmebekd&utm_source=522592')
            time.sleep(10)

            falhas_consecutivas = 0

            while True:
                try:
                    driver.switch_to.default_content() 
                    try:
                        iframe_1 = driver.find_element(By.ID, "gameIframe")
                        driver.switch_to.frame(iframe_1)
                        game_container = driver.find_element(By.XPATH, "/html/body/game-container")
                        shadow_root = driver.execute_script("return arguments[0].shadowRoot", game_container)
                        iframe_2 = shadow_root.find_element(By.CSS_SELECTOR, "iframe")
                        driver.switch_to.frame(iframe_2)
                        iframe_3 = driver.find_element(By.XPATH, '/html/body/div[5]/div[2]/iframe')
                        driver.switch_to.frame(iframe_3)
                    except Exception as e:
                        falhas_consecutivas += 1
                        time.sleep(3)
                        if falhas_consecutivas > 10: raise Exception("Iframes não carregaram.")
                        continue

                    caixa_historico = driver.find_element(By.XPATH, '/html/body/div[4]/div/div/div[2]/div[6]/div/div[1]/div/div/div')
                    
                    script_extrator = """
                    var caixa = arguments[0];
                    var svgs = caixa.querySelectorAll('svg[data-type="roadItem"]');
                    var dados = [];
                    var achou_numero = false;
                    for(var i=0; i<svgs.length; i++){
                        var svg = svgs[i];
                        var textEl = svg.querySelector('text');
                        if(textEl) {
                            var txt = textEl.textContent.trim();
                            var num = parseInt(txt, 10);
                            if(!isNaN(num) && num >= 2 && num <= 12) {
                                achou_numero = true;
                                var cor = 'T';
                                var nameAttr = svg.getAttribute('name');
                                if (nameAttr) {
                                    var nome = nameAttr.toLowerCase();
                                    if (nome === 'player') cor = 'P';
                                    else if (nome === 'banker') cor = 'B';
                                    else if (nome === 'tie') cor = 'T';
                                } else {
                                    var gTag = svg.querySelector('g');
                                    if(gTag) {
                                        var fill = gTag.getAttribute('fill');
                                        if(fill) {
                                            fill = fill.toLowerCase();
                                            if(fill.includes('26b5df')) cor = 'P'; 
                                            else if(fill.includes('d51851')) cor = 'B'; 
                                            else if(fill.includes('e9922b')) cor = 'T'; 
                                        }
                                    }
                                }
                                dados.push({"pedra": cor === 'P' ? 'Player' : cor === 'B' ? 'Banker' : 'Tie', "numero": num});
                            }
                        }
                    }
                    return {dados: dados, has_numbers: achou_numero};
                    """
                    
                    resultado_js = driver.execute_script(script_extrator, caixa_historico)
                    
                    if not resultado_js['has_numbers']:
                        falhas_consecutivas += 1
                        print(f"👁️ Painel liso (Tentativa {falhas_consecutivas}/15). Dando clique...")
                        try:
                            actions = ActionChains(driver)
                            actions.move_to_element(caixa_historico).click().pause(0.5).click().perform()
                        except:
                            try:
                                driver.execute_script("var ev = new MouseEvent('click', {bubbles: true, cancelable: true, view: window}); arguments[0].dispatchEvent(ev);", caixa_historico)
                                time.sleep(0.3)
                                driver.execute_script("var ev = new MouseEvent('click', {bubbles: true, cancelable: true, view: window}); arguments[0].dispatchEvent(ev);", caixa_historico)
                            except: pass
                        time.sleep(2) 
                        if falhas_consecutivas >= 15:
                            print("🔄 O painel travou. Dando F5 na página...")
                            driver.refresh()
                            time.sleep(15)
                            falhas_consecutivas = 0
                    else:
                        dados_extraidos = resultado_js['dados']
                        dados_invertidos = dados_extraidos[::-1]
                        atualizar_memoria(dados_invertidos)
                        print(f"📡 API ONLINE: {len(historico_global)} rodadas salvas no banco!")
                        falhas_consecutivas = 0 
                        
                except Exception as e:
                    falhas_consecutivas += 1
                    if falhas_consecutivas > 20:
                        print("❌ Erro crítico contínuo nos Iframes. Reiniciando motor...")
                        break 
                time.sleep(1) 

        except Exception as e:
            print("⚠️ Motor capotou. Reiniciando tudo em 10s...")
            try: driver.quit()
            except: pass
            time.sleep(10)

@app.route('/api_bacbo', methods=['GET'])
def get_api_bacbo():
    return jsonify(historico_global)

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "online", "rodadas_acumuladas": len(historico_global)})

if __name__ == '__main__':
    thread_raspagem = threading.Thread(target=motor_raspagem_24h, daemon=True)
    thread_raspagem.start()
    porta = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=porta)
