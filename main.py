from playwright.sync_api import sync_playwright
import time
import os
import wget
from tqdm import tqdm

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
            email = "regustavosisosiso@gmail.com"
            password = "decanoato1991"
            user_login = login(page, email, password)
            if user_login:
                print("> Login efetuado com sucesso")
            else:
                print("x Login não efetuado com sucesso")
                exit(0)

            save_file_name(page, txt_file, user_login)

        cursos = return_courses(page)
        lista_cursos = []
        os.system('cls' if os.name == 'nt' else 'clear')
        print("+ Selecione o que deseja baixar: \n")
        for i, curso in enumerate(cursos):
            course = {}
            nome_curso = curso.wait_for_selector('xpath=.//h1').inner_text()
            qualificacao = curso.wait_for_selector('xpath=./../../h2').inner_text()
            url = curso.wait_for_selector('xpath=./a').get_attribute('href')
            if 'aula' in url:
                url = "https://www.estrategiaconcursos.com.br" + url
                print(f"{i+1}.\nNome: {nome_curso}\nQualificação: {qualificacao}\nURL: {url}\n")
                course['id'] = i+1
                course['nome'] = nome_curso
                course['qualificacao'] = qualificacao
                course['url'] = url
                lista_cursos.append(course)
            else:
                i -= 1

        escolha = input("> Digite a sua escolha: ")
        sair = True
        for curso in lista_cursos:
            if escolha == str(curso['id']):
                sair = False
                print("+ Obtendo dados do curso...")
                time.sleep(1)
                filename = os.path.join(os.getcwd(), curso['nome'])
                os.makedirs(filename, exist_ok=True)
                os.system('cls' if os.name == 'nt' else 'clear')
                data = get_course_data(page, curso)
                total = return_total_videos(data)
                bar = tqdm(total, desc="Baixando Vídeos")

                for item in data:
                    bar.set_description(f"Baixando Vídeos {item['id']}")
                    nome_aula = f"{item['id']}_{item['nome']}"
                    dir_aula = os.path.join(filename, nome_aula)
                    os.makedirs(dir_aula, exist_ok=True)
                    for video in item['videos']:
                        nome_video = f"{video['id']}_{video['nome']}.mp4"
                        path = os.path.join(dir_aula, nome_video)
                        wget.download(video['link'], path)
                        bar.update(1)

                print("> Curso baixado com sucesso")
        if sair:
            print("x Opção Inválida")
            exit(0)

        browser.close()

if __name__ == "__main__":
    txt_file = create_txt()

    os.system('cls' if os.name == 'nt' else 'clear')
    print("+ Selecione o seu provedor de serviços:\n")
    print("1.\nNome: Estratégia Concursos\nURL: https://estrategiaconcursos.com.br\n")
    print("2.Sair\n")
    escolha = input("> Digite sua escolha: ")

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
