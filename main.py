import os
import time

from functions.estrategia import create_txt
from escolas import Cursos

if __name__ == "__main__":

    os.system('cls' if os.name == 'nt' else 'clear')
    print("+ Selecione o seu provedor de serviços:\n")
    print("1.\nNome: Estratégia Concursos\nURL: https://estrategiaconcursos.com.br\n")
    print("2.\nNome: Carreira Jurídica (Estratégia)\nURL: https://cj.estrategia.com\n")
    print("3.Sair\n")
    escolha = input("> Digite sua escolha: ")
    print('\n')

    if escolha == "1":
        txt_file = create_txt('estrategia')
        curso = Cursos()
        curso.estrategia_concursos(txt_file)

    elif escolha == "2":
        txt_file = create_txt('juridico')
        curso = Cursos()
        curso.juridico(txt_file)

    elif escolha == "3":
        print("Saindo...")
        time.sleep(2)
        exit(0)
    else:
        print("Opção inválida. Por favor, tente novamente.")
        time.sleep(1.5)
        exit(0)
