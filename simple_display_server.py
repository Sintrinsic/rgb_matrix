import socket
import threading
from queue import Queue
from lib.samplebase import SampleBase
import pickle
import struct

class PixelDisplayServer(SampleBase):
    def __init__(self, *args, **kwargs):
        super(PixelDisplayServer, self).__init__(*args, **kwargs)
        self.pixel_queue = Queue()

    def run(self):
        self.start_server()  # Start the server in the background

        while True:
            if not self.pixel_queue.empty():
                pixel_data = self.pixel_queue.get()
                self.update_display(pixel_data)

    def update_display(self, pixel_data):
        canvas = self.matrix.CreateFrameCanvas()
        for x in range(len(pixel_data)):
            for y in range(len(pixel_data[x])):
                r, g, b = pixel_data[x][y]
                canvas.SetPixel(x, y, r, g, b)
        self.matrix.SwapOnVSync(canvas)

    def start_server(self, host='192.168.1.62', port=12345):
        def server_thread():
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind((host, port))
            server_socket.listen()
            print(f"Server started on {host}:{port}")

            while True:
                client_socket, addr = server_socket.accept()
                print(f"Connection from {addr} has been established.")
                client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
                client_handler.start()

        threading.Thread(target=server_thread, daemon=True).start()

    def handle_client(self, client_socket):
        data = b""
        payload_size = struct.calcsize(">L")
        try:
            while True:
                while len(data) < payload_size:
                    packet = client_socket.recv(4096)
                    if not packet:
                        return
                    data += packet

                packed_msg_size = data[:payload_size]
                data = data[payload_size:]
                msg_size = struct.unpack(">L", packed_msg_size)[0]

                while len(data) < msg_size:
                    data += client_socket.recv(4096)

                pixel_data = data[:msg_size]
                data = data[msg_size:]

                pixel_data = pickle.loads(pixel_data)
                self.pixel_queue.put(pixel_data)
                client_socket.send(b'Pixel data received')
        except Exception as e:
            print(f"Error: {e}")
        finally:
            client_socket.close()

def main():
    display_server = PixelDisplayServer()
    if not display_server.process():
        display_server.print_help()

if __name__ == "__main__":
    main()
