import socket
import pickle
import struct


class SimpleDisplayClient:
    '''Simple client to send frames to the RGB matrix server. Expects rgb image arrays.'''
    def __init__(self, server_address):
        self.server_address = server_address
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect(server_address)
        except socket.error as e:
            print(f"Error connecting to server: {e}")
            self.client_socket = None

    def send_matrix(self, matrix):
        if not self.client_socket:
            print("Client socket is not connected.")
            return

        serialized_data = pickle.dumps(matrix)
        message = struct.pack(">L", len(serialized_data)) + serialized_data

        try:
            self.client_socket.sendall(message)
        except socket.error as e:
            print(f"Error sending data to server: {e}")

    def close(self):
        if self.client_socket:
            self.client_socket.close()


