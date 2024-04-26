from playwright.sync_api import sync_playwright
import time
import os
import subprocess

from functions import *

def main():

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
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
                user_login = login(page, email, password)
                if user_login:
                    print("> Conta adicionada com sucesso")
                    save_file_name(page, txt_file, user_login)
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
                        page.context.add_cookies(load_cookies(nome_arquivo))
                        sair = False
                if sair:
                    print("x Opção Inválida")
                    exit(0)
        else:
            print("- Login não localizado")
            time.sleep(1)
            email = input("> Insira seu usuário: ")
            password = input("> Insira sua senha: ")
            user_login = login(page, email, password)
            if user_login:
                print("+ Login efetuado com sucesso")
            else:
                print("x Login não efetuado com sucesso")
                exit(0)

            save_file_name(page, txt_file, user_login)

        print("+ Qual serviço deseja utilzar? \n")
        print("1.\nListar Cursos\n")
        print("2.\nBuscar por URL\n")
        escolha = input("> Digite sua escolha: ")
        print('\n')
        time.sleep(0.5)

        print("+ Qual a resolução do download do vídeo? \n")
        print("1. 720p\n")
        print("2. 480p\n")
        print("3. 360p\n")
        resolucao = input("> Digite sua escolha: ")
        if resolucao == "1":
            resolucao = '720p'
        elif resolucao == "2":
            resolucao = '480p'
        elif resolucao == "3":
            resolucao = '360p'
        else:
            print("x Opção inválida. Por favor, tente novamente.")
            time.sleep(1.5)
            exit(0)

        if escolha == "1":
            download_por_lista(page, resolucao)

        elif escolha == "2":
            url = input("> Digite ou Cole aqui o link do Curso: ")
            download_por_url(page, url, resolucao)

        browser.close()

if __name__ == "__main__":
    txt_file = create_txt()

    os.system('cls' if os.name == 'nt' else 'clear')
    print("+ Selecione o seu provedor de serviços:\n")
    print("1.\nNome: Estratégia Concursos\nURL: https://estrategiaconcursos.com.br\n")
    print("2.Sair\n")
    escolha = input("> Digite sua escolha: ")
    print('\n')

    if escolha == "1":
        main()
    elif escolha == "2":
        print("Saindo...")
        time.sleep(2)
        exit(0)
    else:
        print("Opção inválida. Por favor, tente novamente.")
        time.sleep(1.5)
        exit(0)
