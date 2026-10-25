import socket
import threading
import json

user = str(input("Nome de usuário:\t"))

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)      # define o cliente como (IPv4, TCP)
client.connect(("127.0.0.1", 55555))                            # conecta o cliente ao servidor


def print_msg(jinfo):

    print(jinfo)
    print(jinfo['acao'])
    if jinfo["acao"] == "GROUP_MSG":
        print(f'[{jinfo["destino"]}] {jinfo["origem"]}: {jinfo["mensagem"]}')

    elif jinfo["acao"] == "DIRECT":
        print(f'{jinfo["origem"]}: {jinfo["mensagem"]}')

    elif jinfo["acao"] == "BROADCAST":
        print(f'{jinfo["origem"]}: {jinfo["mensagem"]}')
        
    else:
        print("Erro, nenhuma acao encontrada em print_msg")

    return


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

def receive():
    """
    Recebe mensagens do servidor.
    """
    print('receive() thread iniciada. Recebendo mensagens do servidor...\n.\n.\n.')
    while True:
        try:
            server_com = client.recv(1024).decode()


            server_com = json.loads(server_com)     

            print(f"receive():\t{server_com}")

            printer_thread = threading.Thread(target=print_msg, args=(server_com,))
            printer_thread.start()
        except:
            print('Erro!!')
            client.close()
            break


while True:
    server_com = client.recv(1024).decode()
    print(f"START: {server_com}")
    if server_com == 'USER':
        print('user?')
        client.sendall(user.encode())   # ENVIA O NOME DE USUARIO
        print('user enviado')
        server_com = client.recv(1024).decode() # recebe resposta do server
        print('recbv')
        if server_com == 'OK':  # servidor respoondeu OK?
            print("Autenticado com sucesso.\n") # ok
            break

receive_thread = threading.Thread(target=receive)
send_thread = threading.Thread(target=send)

receive_thread.start()  # INICIA O PROGRAMA DE RECEBIMENTO
# send.start()