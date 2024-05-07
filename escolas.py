from playwright.sync_api import sync_playwright
import time
import os

from functions import *

class Cursos():
    """Classe responsável pela manipulação dos cursos."""

    def estrategia_concursos(self, txt_file):
        """Download dos Cursos da Estratégia Concursos."""

        with sync_playwright() as p:
            self.browser = p.chromium.launch(headless=True)
            self.context = self.browser.new_context()
            self.context.set_default_timeout(15000)
            self.context.on("download", self.handle_download)

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
                    print(f"{numero}.\nAcessar usando a conta: {nome_usuario}\n")
                escolha = input("> Digite sua escolha: ")
                print('\n')

                if escolha == "0":
                    print("+ Adicionando conta...")
                    time.sleep(1)
                    email = input("> Insira seu usuário: ")
                    password = input("> Insira sua senha: ")
                    user_login = login(self.page, email, password)
                    if user_login:
                        print("> Conta adicionada com sucesso")
                        save_file_name(self.page, txt_file, user_login)
                    else:
                        print("x Conta não adicionada com sucesso")
                        exit(0)
                else:
                    sair = True
                    for line in lines:
                        numero = line.split('-')[0].strip()
                        nome_arquivo = line.split('-')[1].strip()
                        nome_usuario = line.split('-')[2].strip()
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
                user_login = login(self.page, email, password)
                if user_login:
                    print("+ Login efetuado com sucesso")
                else:
                    print("x Login não efetuado com sucesso")
                    exit(0)

                save_file_name(self.page, txt_file, user_login)

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
                download_por_lista(self.page, self.resolucao)

            elif self.servico == "2":
                # Download por URL
                url = input("> Digite ou Cole aqui o link do Curso: ")
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
                        download_por_url(self.page, link, self.resolucao, pacote_path=path_pacote)
                else:
                    download_por_url(self.page, url, self.resolucao, pacote_path=None)

    def juridico(self):
        """Download dos Cursos Jurídicos da Estratégia Concursos."""

        if self.servico == "1":
            # Download por lista
            ...
        
        elif self.servico == "2":
            # Download por URL
            ...

    def __del__(self):
        self.browser.close()

    def handle_download(self, download):
        download.save_as(os.getcwd())
