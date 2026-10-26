import socket
import threading
import json

user = str(input("Nome de usuário:\t"))

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)      # define o cliente como (IPv4, TCP)
client.connect(("189.6.245.67", 55555))                            # conecta o cliente ao servidor

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

def direct_message(destino, mensagem, origem=user):
    info = {
        "acao": 'DIRECT',
        "origem": origem,
        "destino": destino,
        "mensagem": mensagem
    }
    
    client.sendall(json.dumps(info).encode())

    return

def group_message(grupo, mensagem, origem=user):
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


def send():
    """
    Escreve uma mensagem e envia ao servidor.
    """
    print('send(thread) iniciada.')

    # message = input('>> ')
    # client.send(message.encode())
    opcao = "99"
    while opcao != "0":
        print(f'Digite 1 para enviar DM.\nDigite 2 para enviar Group Message\nDigite 3 para criar um grupo.\nDigite 0 para sair.')
        opcao = str(input('>>\t'))
        if opcao == "1":
            nome = str(input('Digite o nome do usuário destino:   '))
            mensagem = str(input('Digite a mensagem:\n>>\t'))
            print(f'{nome}: {mensagem}')
            direct_message(destino=nome, mensagem=mensagem)

        elif opcao == "2":
            # enviar mensagem pra grupo
            nome = str(input('Digite o nome do grupo destino:   '))
            mensagem = str(input('Digite a mensagem:\n>>\t'))
            print(f'{nome}: {mensagem}')
            group_message(grupo=nome, mensagem=mensagem)

        elif opcao == "3":
            # criar grupo
            nome = str(input('Nome do grupo:    '))
            membro1 = str(input('Nome de usuário do membro 1:   '))
            membro2 = str(input('Nome de usuário do membro 2:   '))
            membros = [membro1, membro2]


    print('zerou')

def receive():
    """
    Recebe mensagens do servidor.
    """
    print('receive() thread iniciada. Recebendo mensagens do servidor...\n.\n.\n.')
    while True:
        try:
            server_com = client.recv(1024).decode()
            print(f"receive():\t{server_com}")
        except:
            print('Erro!!')
            client.close()
            break


while True:
    server_com = client.recv(1024).decode()
    print(f"START: {server_com}")
    if server_com == 'USER':
        print('user?')
        client.sendall(user.encode())
        print('user enviado')
        server_com = client.recv(1024).decode()
        print('recbv')
        if server_com == 'OK':
            print("Autenticado com sucesso.\n")
            break

receive_thread = threading.Thread(target=receive)
send_thread = threading.Thread(target=send)

send_thread.start()