import socket
import threading

HOST = '0.0.0.0'
PORT = 5000

# Diccionario compartido para registrar usuarios activos: {apodo: socket}
clientes_conectados = {}
lock = threading.Lock()  # Sincronización para evitar condiciones de carrera

def notificar_lista_usuarios():
    """Envía la lista actualizada de usuarios a todos los conectados."""
    with lock:
        lista = "LISTA_USUARIOS:" + ",".join(clientes_conectados.keys())
        for sock in clientes_conectados.values():
            try:
                sock.send(lista.encode('utf-8'))
            except:
                pass

class HiloCliente(threading.Thread):
    """Clase Thread dedicada a gestionar la conexión individual de un usuario."""
    def __init__(self, sock_cliente, direccion):
        super().__init__()
        self.sock = sock_cliente
        self.direccion = direccion
        self.apodo = ""
        self.activo = True

    def run(self):
        # 1. Autenticación y registro del apodo
        try:
            self.sock.send("SOLICITAR_NICKNAME".encode('utf-8'))
            self.apodo = self.sock.recv(1024).decode('utf-8').strip()

            with lock:
                if self.apodo in clientes_conectados or not self.apodo:
                    self.sock.send("ERROR:Nombre en uso o inválido.".encode('utf-8'))
                    self.sock.close()
                    return
                clientes_conectados[self.apodo] = self.sock

            print(f"[+] {self.apodo} conectado desde {self.direccion}")
            self.sock.send("OK:Conexión exitosa.".encode('utf-8'))
            notificar_lista_usuarios()

        except Exception as e:
            print(f"Error en handshake con {self.direccion}: {e}")
            self.sock.close()
            return

        # 2. Bucle principal del hilo para enrutamiento de mensajes
        while self.activo:
            try:
                datos = self.sock.recv(1024).decode('utf-8')
                if not datos:
                    break

                if ":" in datos:
                    destinatario, mensaje = datos.split(":", 1)
                    
                    with lock:
                        sock_destino = clientes_conectados.get(destinatario)

                    if sock_destino:
                        paquete = f"MENSAJE_PRIVADO:{self.apodo}:{mensaje}"
                        sock_destino.send(paquete.encode('utf-8'))
                    else:
                        self.sock.send(f"SISTEMA:El usuario '{destinatario}' no existe o no está en línea.".encode('utf-8'))
            except:
                break

        # 3. Limpieza al desconectarse
        self.desconectar()

    def desconectar(self):
        self.activo = False
        with lock:
            if self.apodo in clientes_conectados:
                del clientes_conectados[self.apodo]
                print(f"[-] {self.apodo} se ha desconectado.")
        self.sock.close()
        notificar_lista_usuarios()


def iniciar_servidor():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind((HOST, PORT))
    servidor.listen()
    print(f"Servidor Multihilo iniciado en el puerto {PORT}...")

    while True:
        sock_cliente, direccion = servidor.accept()
        # Se instancia y arranca un hilo dedicado por cada nueva conexión
        hilo = HiloCliente(sock_cliente, direccion)
        hilo.start()

if __name__ == "__main__":
    iniciar_servidor()


