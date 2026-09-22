import socket
import select

HOST = '0.0.0.0'
PORT = 5000

def iniciar_servidor():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind((HOST, PORT))
    servidor.listen()
    
    # Lista de sockets que 'select' va a monitorear
    entradas_sockets = [servidor]
    
    # Mapeos para rastrear clientes:
    # socket -> apodo  |  apodo -> socket
    socket_a_apodo = {}
    apodo_a_socket = {}

    print(f"Servidor Monohilo (select) activo en el puerto {PORT}...")

    while True:
        # select() bloquea hasta que al menos un socket tenga datos o conexiones listas
        lectura_lista, _, _ = select.select(entradas_sockets, [], [])

        for sock in lectura_lista:
            # CASO 1: Nueva conexión entrante al servidor
            if sock == servidor:
                sock_cliente, direccion = servidor.accept()
                entradas_sockets.append(sock_cliente)
                sock_cliente.send("SOLICITAR_NICKNAME".encode('utf-8'))
            
            # CASO 2: Un cliente existente envió datos
            else:
                try:
                    datos = sock.recv(1024).decode('utf-8')
                    if not datos:
                        desconectar_cliente(sock, entradas_sockets, socket_a_apodo, apodo_a_socket)
                        continue

                    # Handshake inicial: El cliente envía su apodo
                    if sock not in socket_a_apodo:
                        apodo = datos.strip()
                        if apodo in apodo_a_socket or not apodo:
                            sock.send("ERROR:Nombre en uso o inválido.".encode('utf-8'))
                            desconectar_cliente(sock, entradas_sockets, socket_a_apodo, apodo_a_socket)
                        else:
                            socket_a_apodo[sock] = apodo
                            apodo_a_socket[apodo] = sock
                            print(f"[+] {apodo} conectado.")
                            sock.send("OK:Conexión exitosa.".encode('utf-8'))
                            notificar_usuarios(apodo_a_socket)
                    
                    # Enrutamiento de mensaje privado "DESTINATARIO:MENSAJE"
                    else:
                        if ":" in datos:
                            destinatario, mensaje = datos.split(":", 1)
                            emisor = socket_a_apodo[sock]
                            
                            sock_destino = apodo_a_socket.get(destinatario)
                            if sock_destino:
                                paquete = f"MENSAJE_PRIVADO:{emisor}:{mensaje}"
                                sock_destino.send(paquete.encode('utf-8'))
                            else:
                                sock.send(f"SISTEMA:El usuario '{destinatario}' no está en línea.".encode('utf-8'))

                except Exception:
                    desconectar_cliente(sock, entradas_sockets, socket_a_apodo, apodo_a_socket)

def notificar_usuarios(apodo_a_socket):
    """Envía la lista actualizada de usuarios activos."""
    lista = "LISTA_USUARIOS:" + ",".join(apodo_a_socket.keys())
    for sock in apodo_a_socket.values():
        try:
            sock.send(lista.encode('utf-8'))
        except:
            pass

def desconectar_cliente(sock, entradas, sock_map, apodo_map):
    """Limpia las referencias del socket cuando un cliente se desconecta."""
    if sock in entradas:
        entradas.remove(sock)
    if sock in sock_map:
        apodo = sock_map[sock]
        del sock_map[sock]
        if apodo in apodo_map:
            del apodo_map[apodo]
        print(f"[-] {apodo} se ha desconectado.")
        notificar_usuarios(apodo_map)
    sock.close()

if __name__ == "__main__":
    iniciar_servidor()


