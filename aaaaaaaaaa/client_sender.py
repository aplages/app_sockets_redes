import socket
import threading
import json

user = str(input("Nome de usuário:\t"))

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)      # define o cliente como (IPv4, TCP)
client.connect(("127.0.0.1", 55555))                            # conecta o cliente ao servidor

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

    # CRIAR ERRO PARA USUARIO NAO ENCONTRADO:
    # Print('Erro, usuário não encontrado.')

    return

def group_message(grupo, mensagem, origem=user):
    info = {
        "acao": 'GROUP_MSG',
        "origem": origem,
        "destino": grupo, 
        "mensagem": mensagem
    }
    
    client.sendall(json.dumps(info).encode())

    # CRIAR ERRO PARA GRUPO NAO ENCONTRADO:
    # Print('Erro, você não está em um grupo.')

    return

def broadcast_message(mensagem, origem = user):
    info = {"acao": "BROADCAST",
            "origem": origem,
            "mensagem": mensagem}
    client.sendall(json.dumps(info).encode())


def send():
    """
    Escreve uma mensagem e envia ao servidor.
    """
    print('send(thread) iniciada.')

    print('-======= Bem-vindo ao Chat =======-')
    print("Comandos: /s (Dizer), /p (Grupo), /w <jogador> (Sussurro)")
    print("Digite '/sair' para encerrar.\n")
    
    canal_atual = '/s'
    alvo_atual = ''
    user = 'VOCÊ'
    
    while True:
        # Recebe input e formata
        if canal_atual == '/w':
            prefixo = f'[{alvo_atual}]: '
        elif canal_atual == '/s':
            prefixo = f'[Geral]: '
        else:
            prefixo = f'[Grupo]: '
    
        entrada = str(input(prefixo)).strip()
    
        if not entrada: # Se a entrada for vazia, vai pro inicio do loop
            continue
    
        if entrada.lower() == '/sair':
            print('Saindo...')
            break
    
        if entrada[0] == '/':
            partes = entrada.split(' ', 1) # Divite a entrada no primeiro espaço
    
            comando = partes[0].lower()
    
            if comando in ['/s', '/p']: # Usuario digitou /s ou /p no inicio
                canal_atual = comando
                if len(partes) > 1: # Testa se o usuario digitou algo após o comando
                    mensagem = partes[1]
                else:
                    continue    # digitou apenas o comando. Troca o canal e volta pro inicio do loop
    
            elif comando == '/w':
                if len(partes) > 1: # Testa se o usuario digitou um destinatario
                    sussurro_partes = partes[1].split(' ', 1)
                    alvo_atual = sussurro_partes[0] # troca o destinatário do sussurro
                    canal_atual = '/w'
    
                    if len(sussurro_partes) > 1: # testa se o usuario digitou uma mensagem após o comando
                        mensagem = sussurro_partes[1]
                    else:
                        continue    # digitou apenas o comando e um destino. troca o destino do sussurro e inicia o loop
                else:   # Digitou apenas /w sem um destino. Uso incorreto.
                    print('Tente novamente. /w <destino> [mensagem]')
                    continue
    
            else:   # Usou / mas nao usou nenhum comando
                print(f'Comando desconhecido.')
                continue
    
        else:   # Não é um comando, então é uma mensagem no canal atual
            mensagem = entrada
    
        # Exibe no terminal
        if canal_atual == '/s':
            print(f'[Geral] {user}: {mensagem}')
            send_t = threading.Thread(target=broadcast_message, args=(mensagem,))
            send_t.start()

        elif canal_atual == '/p':
            print(f'[Grupo] {user}: {mensagem}')
            grupo = 0
            send_t = threading.Thread(target=group_message, args=(grupo, mensagem))
            send_t.start()

        elif canal_atual == '/w':
            print(f'Para <{alvo_atual}>: {mensagem}')
            send_t = threading.Thread(target=direct_message, args=(alvo_atual, mensagem))
            send_t.start()



    """
    # message = input('>> ')
    # client.send(message.encode())
    opcao = "/s"

    print(f'Use /s para falar no chat geral. Use /w para enviar mensagem a um usuario particular. Use /p para falar com seu grupo. Use /invite para convidar um membro para seu grupo. Use /quit para sair')

    while opcao != "/quit":
        entrada = str(input(">>\t"))
        mensagem = entrada
        if entrada[0] == '/':
            opcao, _, mensagem = entrada.partition(" ")
        
        if (opcao == '/s') or (opcao == '/speak') or (opcao == '/say'):
            #broadcast
            # /s blablablabal
            pass

        elif (opcao == '/w') or (opcao == '/whisper'):
            # /w Fulano Mensagemblablalbllablalbal
            user_destino, _, mensagem = mensagem.partition(" ")

            print(f'to {user_destino}: {mensagem}')
            pass

        elif (opcao == '/p') or (opcao == '/party'):
            # party
            # /p blablablabla
            print(f'to party: {mensagem}')
            pass"""

    """
    while opcao != "0":
        print(f'Digite 1 para enviar DM.\nDigite 2 para enviar Group Message\nDigite 3 para criar um grupo.\nDigite 4 para mandar uma mensagem geral. \nDigite 0 para sair')
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
        elif opcao == '4':
            #mensagem broadcast
            mensagem = str(input('Digite a mensagem: \n >> \t'))
            broadcast_message(mensagem = mensagem)
        """
    
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

send_thread.start() # INICIA O PROGRAMA DE ENVIO