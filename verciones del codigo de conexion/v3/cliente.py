import socket
import threading
import sys

usuarios_activos = []

class HiloReceptor(threading.Thread):
    """Hilo dedicado exclusivamente a escuchar las respuestas entrantes del servidor."""
    def __init__(self, sock):
        super().__init__()
        self.sock = sock
        self.daemon = True  # Finaliza automáticamente si el hilo principal termina
        self.activo = True

    def run(self):
        global usuarios_activos
        while self.activo:
            try:
                datos = self.sock.recv(1024).decode('utf-8')
                if not datos:
                    break

                if datos.startswith("LISTA_USUARIOS:"):
                    raw_lista = datos.split(":", 1)[1]
                    usuarios_activos = [u for u in raw_lista.split(",") if u]

                elif datos.startswith("MENSAJE_PRIVADO:"):
                    _, emisor, mensaje = datos.split(":", 2)
                    print(f"\n\n>>> [Mensaje de {emisor}]: {mensaje}")
                    print("\nOpción [1: Escribir | 2: Ver usuarios | 3: Salir]: ", end="")

                elif datos.startswith("SISTEMA:"):
                    _, msg = datos.split(":", 1)
                    print(f"\n[Aviso]: {msg}")

            except:
                break
        print("\nConexión con el servidor finalizada.")


def iniciar_cliente():
    ip_servidor = input("IP del servidor: ").strip()
    puerto = 5000
    apodo = input("Tu nombre de usuario: ").strip()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((ip_servidor, puerto))
    except Exception as e:
        print(f"No se pudo conectar al servidor: {e}")
        return

    # Proceso de autenticación inicial
    msg = sock.recv(1024).decode('utf-8')
    if msg == "SOLICITAR_NICKNAME":
        sock.send(apodo.encode('utf-8'))
        resp = sock.recv(1024).decode('utf-8')
        if not resp.startswith("OK"):
            print(f"Servidor rechazó la conexión: {resp}")
            sock.close()
            return

    # Iniciar el hilo de recepción
    receptor = HiloReceptor(sock)
    receptor.start()

    print(f"\n=== SESIÓN INICIADA COMO: {apodo} ===")

    # Bucle del hilo principal (Interfaz de consola)
    while True:
        print("\n--- MENÚ ---")
        print("1. Enviar mensaje a un usuario")
        print("2. Ver lista de usuarios en línea")
        print("3. Salir")
        opcion = input("Opción: ").strip()

        if opcion == "1":
            destinatario = input("Destinatario: ").strip()
            if destinatario == apodo:
                print("No puedes enviarte mensajes a ti mismo.")
                continue

            mensaje = input(f"Mensaje para {destinatario}: ").strip()
            if mensaje:
                paquete = f"{destinatario}:{mensaje}"
                sock.send(paquete.encode('utf-8'))

        elif opcion == "2":
            print("\nUsuarios en línea:")
            for u in usuarios_activos:
                marcador = "(Tú)" if u == apodo else ""
                print(f" - {u} {marcador}")

        elif opcion == "3":
            print("Cerrando conexión...")
            sock.close()
            sys.exit()

if __name__ == "__main__":
    iniciar_cliente()
