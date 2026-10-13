import socket
import threading
import json

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)      # define o cliente como (IPv4, TCP)
client.connect(("127.0.0.1", 55555))                            # conecta o cliente ao servidor

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


def receive():
    """
    Recebe mensagens do servidor.
    """
    while True:
        try:
            server_com = client.recv(1024).decode()
            if server_com == 'AUTH_HEADER':
                auth()
            else:
                print(server_com)

        except:
            print('Erro!!')
            client.close()
            break

def send():
    """
    Escreve uma mensagem e envia ao servidor.
    """
    while True:
        message = input('>> ')
        client.send(message.encode())

receive_thread = threading.Thread(target=receive)
receive_thread.start()

#send_thread = threading.Thread(target=send)
#send_thread.start()
