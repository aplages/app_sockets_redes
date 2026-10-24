import socket
import threading
import json

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)      # define o cliente como (IPv4, TCP)
client.connect(("127.0.0.1", 55555))                            # conecta o cliente ao servidor

def login():
    user = str(input('Nome de usuário:  '))
    senha = str(input('Senha:   '))

    while len(user) < 3:
        user = str(input('Nome de usuário (3 ou mais caracteres):  '))
    while len(senha) < 3:
        senha = str(input('Senha (3 ou mais caracteres):   '))

    msg = {
            "acao": "LOGIN", 
            "username": user, 
            "senha": senha
            }

    return json.dumps(msg)


def register():
    user = str(input('Escolha um nome de usuário:   '))
    senha = str(input('Escolha uma senha segura:    '))

    msg = {
            "acao": "REGISTER", 
            "username": user, 
            "senha": senha
            }

    return json.dumps(msg)


def auth():
    # TRATAR NOME/SENHA VAZIOS NO CLIENTE (nas funções, antes de transformar em JSON)

    while True:
        authent = str(input('Digite 1 para LOGIN\nOu 2 para REGISTRO:\n>>\t'))
        if authent == '1':
            client.sendall(login().encode())
        elif authent == '2':
            client.sendall(register().encode())
        else:
            print('\nOpção inválida\n\n')
            continue

        resposta = json.loads(client.recv(1024).decode())

        resp = resposta['acao']

        if resp == 'OK':
            print('Sucesso na autenticação! \n')
            # Iniciamos a thread de envio. O próprio input('>> ') dela desenha o prompt inicial.
            send_thread = threading.Thread(target=send)
            send_thread.start()
            break
        elif resp == 'ERRO':
            if resposta['local'] == 'LOGIN':
                if resposta['erro'] == '0':
                    print('\nUsuário inválido.')
                    continue
                else:
                    print('Senha inválida.')
                    continue
            elif resposta['local'] == 'REGISTER':
                if resposta['erro'] == '0':
                    print('Usuário já existe.')
                    continue


def novo_grupo(nome=None, membros=[]):
    nome = nome
    membros = membros

    grupo = {
            "acao": "CREATE_GROUP",
            "nome_do_grupo": nome,
            "membros": membros
            }

    client.sendall(json.dumps(grupo).encode())

    return

def direct_message(origem, destino, mensagem):
    info = {
        "acao": 'DIRECT',
        "origem": origem,
        "destino": destino,
        "mensagem": mensagem
    }
    
    client.sendall(json.dumps(info).encode())

    return

def group_message(origem, grupo, mensagem):
    info = {
        "acao": 'GROUP_MSG',
        "origem": origem,
        "destino": grupo,
        "mensagem": mensagem
    }
    
    client.sendall(json.dumps(info).encode())

    return

def print_msg(json):
    if json["acao"] == "GROUP_MSG":
        print(f'[{json["destino"]}] {json["origem"]}: {json["mensagem"]}')
    elif json["acao"] == "DIRECT":
        print(f'{json["origem"]}: {json["mensagem"]}')
    else:
        print("Erro, nenhuma acao encontrada em print_msg")

    return

def receive():
    """
    Recebe mensagens do servidor.
    """
    while True:
        try:
            server_com = client.recv(1024).decode()
            if server_com == 'AUTH_HEADER':
                print('auth')
                auth()
                
            elif server_com == 'CREATE_GROUP':
                novo_grupo()
            else:
                server_com = json.loads(server_com)
                if server_com["acao"] == 'OK':
                    continue
                print_func = threading.Thread(print_msg(server_com))
                print_func.start()
                # \r move o cursor para o começo da linha e \033[K apaga qualquer texto existente ali.
                # Isso limpa o '>> ' antigo ou algo digitado pelo cliente para não misturar com o que chegou.
                print(f'\r\033[K{server_com}')
                # Redesenha o '>> ' imediatamente para o usuário continuar digitando se quiser
                print('>> ', end='', flush=True)

        except:
            print('Erro!!')
            client.close()
            break


def send():
    """
    Escreve uma mensagem e envia ao servidor.
    """

    # message = input('>> ')
    # client.send(message.encode())
    opcao = 99
    while opcao != 0:
        if opcao == 1:
            nome = str(input('Digite o nome do usuário destino:   '))
            mensagem = str(input('Digite a mensagem:\n>>\t'))
            pass
        elif opcao == 2:
            # enviar mensagem pra grupo
            nome = str(input('Digite o nome do grupo destino:   '))
            mensagem = str(input('Digite a mensagem:\n>>\t'))
            pass
        elif opcao == 3:
            # criar grupo
            nome = str(input('Nome do grupo:    '))
            membro1 = str(input('Nome de usuário do membro 1:   '))
            membro2 = str(input('Nome de usuário do membro 2:   '))
            membros = [membro1, membro2]


        opcao = 99

receive_thread = threading.Thread(target=receive)
receive_thread.start()

