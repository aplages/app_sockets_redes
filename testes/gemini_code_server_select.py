import socket
import select

# Configuração do socket principal
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("127.0.0.1", 38912))
server.listen()

# A lista que o OS vai vigiar. Começa apenas com o servidor.
sockets_monitorados = [server]

print("Servidor aguardando conexões...")

while True:
    # O código bloqueia aqui. O sistema operacional assume e só libera 
    # quando houver tráfego em algum dos sockets da lista.
    prontos_para_ler, _, _ = select.select(sockets_monitorados, [], [])

    # Iteramos apenas sobre os sockets que tiveram atividade garantida
    for sock in prontos_para_ler:
        
        # Cenário 1: Alguém novo está tentando conectar
        if sock == server:
            cliente, endereco = server.accept()
            print(f"Nova conexão de {endereco}")
            sockets_monitorados.append(cliente) # Adiciona à vigilância
            
        # Cenário 2: Um cliente existente mandou dados ou desconectou
        else:
            try:
                dados = sock.recv(1024)
                if dados:
                    mensagem = dados.decode('utf-8')
                    # Aqui você interpretaria o seu protocolo de aplicação
                    print(f"Recebido: {mensagem}")
                    sock.sendall(b'Mensagem Recebida!')


                    mens = f'{sock} enviou: {mensagem}'
                    for i in sockets_monitorados:
                        i.sendall(mens.encode())

                    if mensagem == "Fechar" or mensagem == "fechar":
                        print("Cliente desconectado.")
                        sockets_monitorados.remove(sock)
                        sock.close()
                else:
                    # recv() retornou bytes vazios: o cliente fechou a conexão
                    print("Cliente desconectado.")
                    sockets_monitorados.remove(sock)
                    sock.close()
            except ConnectionResetError:
                # Tratamento caso o cliente caia abruptamente
                sockets_monitorados.remove(sock)
                sock.close()