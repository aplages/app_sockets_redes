import socket

"""
Esse arquivo foi usado pra testar um loop continuo de envio de mensagens entre o cliente e o servidor.
Também testei como fazia pra conectar outro cliente após encerrar a conexão do cliente anterior.
"""

host = "127.0.0.1"
port = 38912

# Cria um socket TCP usando IPv4
# IPv4: usa AF_INET
# TCP: usa SOCK_STREAM
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Associa o socket ao endereço IP e à porta
server.bind((host, port))

# Coloca o socket em modo de escuta
# O argumento indica o tamanho da fila de conexões pendentes
server.listen()
while True:
    print("Servidor aguardando conexão...")

    # Aguarda a conexão e retorna:
    # conn = socket para comunicação com o cliente
    # addr = endereço IP e a porta do cliente
    conn, addr = server.accept()

    print(f"Cliente conectado: {addr}")

    resposta_cliente = None
    while resposta_cliente != "Fechar" and resposta_cliente != "fechar":
        # Recebe até 1024 bytes do cliente.
        data = conn.recv(32768)
        resposta_cliente = data.decode()
        print("Recebido:", data.decode())

        # Envia uma resposta ao cliente.
        conn.sendall(b"Mensagem recebida!")
        

    # Fecha a conexão com o cliente, após o uso do input
    conn.close()

# Fecha o socket do servidor.
server.close()

# IPv6:
# - troque AF_INET por AF_INET6
# - troque 127.0.0.1 por ::1
