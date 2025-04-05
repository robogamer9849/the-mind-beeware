"""
game card The mind mad to a mobile game
"""

#TODO: use async await to fix auto connect

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

import socket
import threading
import random
import asyncio

def find_code():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip



# --- Global Variables and Network Code ---

HOST = '0.0.0.0'
PORT = 6000
nums = []

def handle_client(conn, addr, num):
    print(f"Connection established with {addr}.")
    nums.append(num)
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                if num in nums:
                    nums.remove(num)
                break
            message = data.decode()
            print(f"Received from {addr}: {message}")
            if message == 'give me':
                conn.sendall(f"{num}".encode())
        except ConnectionResetError:
            print(f"Client {addr} has disconnected.")
            break
    conn.close()
    print(f"Connection with {addr} closed.")

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"Server listening on {HOST}:{PORT}...")
        code = find_code()
        print("Connect code:", code)
        while True:
            conn, addr = server_socket.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr, random.randint(1, 1000000)))
            thread.start()
            print(f"Active connections: {threading.active_count() - 1}")

def start_server_in_background():
    thread = threading.Thread(target=start_server, daemon=True)
    thread.start()
    return "Server started"

# --- BeeWare/Toga UI Application ---

class HomeApp(toga.App):
    def startup(self):
        # Create the main window.
        self.main_window = toga.MainWindow(title=self.formal_name)

        # Create three boxes to act as our "screens"
        self.home_box = self.create_home_box()
        self.server_box = self.create_server_box()
        self.game_box = self.create_game_box()

        # Start with the home screen.
        self.main_window.content = self.home_box
        self.main_window.show()

    def create_home_box(self):
        box = toga.Box(style=Pack(direction=COLUMN, padding=10 ))
        title = toga.Label("Do you want to host (server) or connect as a client?",
                            style=Pack(padding_bottom=10))
        box.add(title)
        
        # Row for Host and Client options
        options_box = toga.Box(style=Pack(direction=ROW ))
        
        # Host button
        host_button = toga.Button("Host", on_press=self.go_to_server, style=Pack(padding=5))
        options_box.add(host_button)
        
        # Client section: text input and connect button
        client_box = toga.Box(style=Pack(direction=COLUMN ))
        self.client_ip_input = toga.TextInput(placeholder="Connect code (IP)",
                                                style=Pack(width=200))
        connect_button = toga.Button("Client", on_press=self.on_connect_press,
                                        style=Pack(padding=5))
        client_box.add(self.client_ip_input)
        client_box.add(connect_button)
        
        options_box.add(client_box)
        box.add(options_box)
        
        # Status label for errors or info
        self.home_status_label = toga.Label("", style=Pack(padding_top=10))
        box.add(self.home_status_label)
        return box

    def create_server_box(self):
        box = toga.Box(style=Pack(direction=COLUMN, padding=10 ))
        self.server_status_label = toga.Label("Press 'Start Server' to begin hosting",
                                                style=Pack(padding_bottom=10))
        box.add(self.server_status_label)
        
        start_button = toga.Button("Start Server", on_press=self.start_server_thread,
                                    style=Pack(padding=5))
        back_button = toga.Button("Back to Home", on_press=self.go_home,
                                    style=Pack(padding=5))
        box.add(start_button)
        box.add(back_button)
        return box

    def create_game_box(self):
        box = toga.Box(style=Pack(direction=COLUMN, padding=10 ))
        self.number_label = toga.Label("Your number: ", style=Pack(font_size=20))
        self.status_label = toga.Label("", style=Pack(font_size=16))
        self.ip_label = toga.Label("", style=Pack(font_size=14))
        
        # show_button = toga.Button("SHOW", on_press=self.on_show_press, style=Pack(padding=5))
        back_button = toga.Button("Back to Home", on_press=self.go_home, style=Pack(padding=5))
        
        box.add(self.number_label)
        box.add(self.status_label)
        box.add(self.ip_label)
        # box.add(show_button)
        box.add(back_button)
        return box

    def go_to_server(self, widget):
        self.main_window.content = self.server_box

    def go_home(self, widget):
        self.main_window.content = self.home_box

    def on_connect_press(self, widget):
        host = self.client_ip_input.value.strip()
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((host, PORT))
                client_socket.sendall("give me".encode())
                data = client_socket.recv(1024)
                number = data.decode()
                print("Received number:", number)
                self.set_game_screen(number, host)
                self.main_window.content = self.game_box
        except OSError as e:
            error_text = f"Error: {e}. Check the IP or network."
            print(error_text)
            self.home_status_label.text = error_text

    async def start_server_thread(self, widget):
        code = find_code()  # Assume this returns the device's IP code.
        self.server_status_label.text = f"Server started!\nConnect code: {code}\nListening on port {PORT}"
        self.server_status_label.text = f"{start_server_in_background()}\nConnect code: {code}\nListening on port {PORT}"
        # start_server_in_background()
        await asyncio.sleep(1)  # Wait for the server to start.
        self.auto_connect_client(code)

        # Auto-connect as client after a short delay using threading.Timer.
        # threading.Timer(1.0, self.auto_connect_client, args=(code,)).start()

    def auto_connect_client(self, code):
        host = '127.0.0.1'
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((host, PORT))
                client_socket.sendall("give me".encode())
                data = client_socket.recv(1024)
                number = data.decode()
                print("Received number:", number)
                self.set_game_screen(number, find_code())
                self.main_window.content = self.game_box
        except OSError as e:
            error_text = f"Error: {e}. Check the IP or network."
            print(error_text)
            self.home_status_label.text = error_text


    def set_game_screen(self, number, host):
        self.number_label.text = f"Your number: {number}"
        self.ip_label.text = f"Code (IP): {host}"
        self.status_label.text = "Game in progress..."

    def on_show_press(self, widget):
        # When SHOW is pressed, send the "I showed" command to the server.
        host_text = self.ip_label.text.replace("Code (IP): ", "").strip()
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((host_text, PORT))
                client_socket.sendall("I showed".encode())
                data = client_socket.recv(1024)
                response = data.decode()
                self.status_label.text = f"Result: {response}"
        except Exception as e:
            self.status_label.text = f"Error: {e}"

def main():
    return HomeApp('HomeApp', 'org.beeware.homeapp')

if __name__ == '__main__':
    main().main_loop()
