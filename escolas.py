from playwright.sync_api import sync_playwright
import time
import os

from functions.estrategia import *
from functions.jurisico import *
from functions.general import *
from functions.state_utils import load_and_sanitize_state

class Cursos():
    """Classe responsável pela manipulação dos cursos."""

    def estrategia_concursos(self, state_path="state.json"):
        """
        Abre diretamente a dashboard de cursos usando state.json (sessão já logada),
        pulando qualquer fluxo de login/seleção de conta.
        """

        # carrega e saneia o state.json
        try:
            state = load_and_sanitize_state(state_path)
        except FileNotFoundError:
            print(f"x Arquivo {state_path} não encontrado. Gere o state.json primeiro.")
            return
        except Exception as e:
            print(f"x Falha ao ler {state_path}: {e}")
            return

        with sync_playwright() as p:
            self.browser = p.chromium.launch(headless=False, channel='chrome')

            # cria contexto já com os cookies/autenticação
            self.context = self.browser.new_context(storage_state=state)
            self.context.on("download", self.handle_download)
            self.page = self.context.new_page()

            # Reaproveita o seu menu existente
            print("+ Qual serviço deseja utilzar? \n")
            print("1.\nListar Cursos\n")
            print("2.\nBuscar por URL\n")
            self.servico = input("> Digite sua escolha: ")
            print('\n')
            time.sleep(0.5)

            print("+ Qual a resolução do download do vídeo? \n")
            print("1. 720p\n")
            print("2. 480p\n")
            print("3. 360p\n")
            resolucao = input("> Digite sua escolha: ")
            if resolucao == "1":
                self.resolucao = '720p'
            elif resolucao == "2":
                self.resolucao = '480p'
            elif resolucao == "3":
                self.resolucao = '360p'
            else:
                print("x Opção inválida. Por favor, tente novamente.")
                time.sleep(1.5)
                exit(0)

            if self.servico == "1":
                es_download_por_lista(self.page, self.resolucao)

            elif self.servico == "2":
                # Download por URL
                print("> Informe a URL completa do curso:")
                url = input("> ")
                if 'pacote' in url:
                    self.page.goto(url)
                    self.page.wait_for_selector('xpath=//div[@class="containerCursos"]')
                    pacote = self.page.wait_for_selector('xpath=//h2').inner_text()
                    pacote_name = ' '.join(pacote.split(' ')[:4]).split('(')[0]
                    path_pacote = os.path.join(os.getcwd(), clear_name(pacote_name.strip()))
                    os.makedirs(path_pacote, exist_ok=True)
                    
                    time.sleep(1)
                    lista_cursos = self.page.query_selector_all('xpath=//div[@class="containerCursos"]/a')
                    print(f"- Pacote identificado: {pacote_name} com {len(lista_cursos)} cursos para baixar.")
                    links = []
                    for curso in lista_cursos:
                        link = 'https://www.estrategiaconcursos.com.br' + curso.get_attribute('href')
                        links.append(link)

                    for link in links:
                        es_download_por_url(self.page, link, self.resolucao, pacote_path=path_pacote)
                else:
                    es_download_por_url(self.page, url, self.resolucao, pacote_path=None)
        
        self.browser.close()

    def juridico(self, txt_file):
        """Download dos Cursos Jurídicos da Estratégia Concursos."""

        with sync_playwright() as p:
            self.browser = p.chromium.launch(channel='chrome', headless=True)
            self.context = self.browser.new_context(accept_downloads=True)
            self.context.set_default_timeout(15000)

            self.page = self.context.new_page()
            with open(txt_file, 'r') as file:
                lines = file.readlines()
            
            if lines != []:
                print("+ Como você deseja acessar este serviço?")
                print("0.\nAdicionar e usar nova conta\n")
                for line in lines:
                    numero = int(line.split('-')[0].strip())
                    nome_arquivo = line.split('-')[1].strip()
                    nome_usuario = line.split('-')[2].strip()
                    token = line.split('-')[3].strip()
                    print(f"{numero}.\nAcessar usando a conta: {nome_usuario}\n")
                escolha = input("> Digite sua escolha: ")
                print('\n')

                if escolha == "0":
                    print("+ Adicionando conta...")
                    time.sleep(1)
                    email = input("> Insira seu usuário: ")
                    password = input("> Insira sua senha: ")
                    user_login, token = login_estrategia(self.page, email, password)
                    if user_login:
                        print("> Conta adicionada com sucesso")
                        save_file_name(self.page, txt_file, user_login, token)
                    else:
                        print("x Conta não adicionada com sucesso")
                        exit(0)
                else:
                    sair = True
                    for line in lines:
                        numero = line.split('-')[0].strip()
                        nome_arquivo = line.split('-')[1].strip()
                        nome_usuario = line.split('-')[2].strip()
                        token = line.split('-')[3].strip()
                        if escolha == numero:
                            print("+ Acessando conta") 
                            time.sleep(1)
                            self.page.context.add_cookies(load_cookies(nome_arquivo))
                            sair = False
                    if sair:
                        print("x Opção Inválida")
                        exit(0)
            else:
                print("- Login não localizado")
                time.sleep(1)
                email = input("> Insira seu usuário: ")
                password = input("> Insira sua senha: ")
                user_login, token = login_estrategia(self.page, email, password)
                if user_login:
                    print("+ Login efetuado com sucesso")
                else:
                    print("x Login não efetuado com sucesso")
                    exit(0)

                save_file_name(self.page, txt_file, user_login, token)

            print("+ Qual serviço deseja utilzar? \n")
            print("1.\nListar Cursos\n")
            print("2.\nBuscar por URL\n")
            self.servico = input("> Digite sua escolha: ")
            print('\n')
            time.sleep(0.5)

            print("+ Qual a resolução do download do vídeo? \n")
            print("1. 720p\n")
            print("2. 480p\n")
            print("3. 360p\n")
            resolucao = input("> Digite sua escolha: ")
            if resolucao == "1":
                self.resolucao = '720p'
            elif resolucao == "2":
                self.resolucao = '480p'
            elif resolucao == "3":
                self.resolucao = '360p'
            else:
                print("x Opção inválida. Por favor, tente novamente.")
                time.sleep(1.5)
                exit(0)

            if self.servico == "1":
                # Download por lista
                ju_download_por_lista(self.resolucao, token)
                time.sleep(1)

            elif self.servico == "2":
                # Download por URL
                ju_download_por_lista(self.resolucao, token)
                time.sleep(1)

        try:
            self.browser.close()
        except:
            pass

    def handle_download(self, download):
        download.save_as(os.getcwd())
