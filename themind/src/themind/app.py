import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

import socket
import threading
import random
import asyncio


'''everything under this comment is for the style of the app'''

#  everywhare
stl_back_button = Pack(padding=(10, 15, 10, 15), alignment='center', font_size=16)
stl_game_img = Pack(width=150, height=150, flex=1)
stl_game_win_img = Pack(width=150, height=150, flex=1, alignment='center', visibility="hidden")
stl_game_lose_img = Pack(width=150, height=150, flex=1, alignment='center', visibility="hidden")

# home page
stl_scrollview = Pack(direction=COLUMN, padding=1, alignment='center')

stl_home_box = Pack(direction=COLUMN, padding=20, alignment='center')
stl_home_btn_box = Pack(direction=COLUMN, padding=20, alignment='center')
stl_home_title = Pack(padding=(0, 15, 0, 15), font_size=24, font_weight='bold', text_align='center')
stl_options_box = Pack(direction=COLUMN, padding=20, alignment='center')

stl_host_button = Pack(padding=(15, 10, 15, 10), font_size=16, background_color='#4CAF50', color='white', flex=1, text_align='center')

stl_client_box = Pack(direction=COLUMN, padding=20, alignment='center')
stl_client_ip_input = Pack(padding=(10, 15, 10, 15), font_size=16)
stl_connect_button = Pack(padding=(15, 10, 15, 10), font_size=16, background_color='#2196F3', color='white', flex=1, text_align='center')

stl_home_status_label = Pack(font_size=16, color='#666666', background_color='#f6f5f4', text_align='center')
stl_tutorial_label = Pack(padding=(0, 10, 0, 10), height=600, font_size=16, font_weight='bold', color='#333333', background_color='#FFE082', flex=1)  # Reduced height, made scrollable

# create server page
stl_create_server_box = Pack(direction=COLUMN, padding=20, alignment='center')
stl_server_status_label = Pack(padding=(0, 10, 0, 10), font_size=16, color='#666666', text_align='center')
stl_max_number_label = Pack(padding=(0, 10, 0, 10), font_size=16, text_align='center')
stl_max_number_slider = Pack(padding=(0, 15, 0, 15))
stl_start_button = Pack(padding=(15, 10, 15, 10), font_size=16, background_color='#4CAF50', color='white', flex=1, text_align='center')

# game page
stl_create_game_box = Pack(direction=COLUMN, padding=20, alignment='center')
stl_number_label = Pack(padding=(0, 15, 0, 15), font_size=24, font_weight='bold', text_align='center')
stl_points_lable = Pack(padding=(0, 10, 0, 10), font_size=16, color='#666666', text_align='center')
stl_ip_label = Pack(padding=(0, 10, 0, 10), font_size=16, text_align='center')
stl_show_button = Pack(padding=(15, 10, 15, 10), font_size=18, background_color='#FF9800', color='white', flex=1, text_align='center')


'''this is the end of the style code'''


def find_code():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


max = 100


def set_max(Max):
    global max
    max = Max
    return max


# --- Global Variables and Network Code ---

HELP_TEXT = '''
    🎮 THE MIND - WHERE TELEPATHY MEETS FUN! 🎮

    🌟 LET'S GET THIS PARTY STARTED! 🌟
    👥 Round up your crew - the more players, the more mayhem!

    🚀 LAUNCH THE GAME:
    1. 📱 Share the app with your squad (Android gang only for now!)
    2. 📶 Everyone hop on the same WiFi
    3. 🎯 One brave soul hits 'HOST'
    4. 🎲 Pick your challenge level

    🔥 JOIN THE ADVENTURE:
    • 📝 Grab that special code from your host
    • 🎯 Smash that 'CONNECT' button
    • 🌈 Let the magic begin!

    🎪 GAME TIME - IT'S MIND-BLOWING! 🎪
    • 🎭 You'll get a super-secret number (no peeking!)
    • 🎯 Feel like you're holding the lowest number? SHOW IT!
    • ⭐ Nailed it? You're a legend earn a point!
    • 💥 Missed it? KABOOM! You lost a point!
    • 🎪 game continues until you end it
    • 🎉 The one with the most pionts wins

    🌟 READY TO BLOW SOME MINDS? LET'S ROLL! 🌟
    '''

HOST = '0.0.0.0'
PORT = 6000
nums = {}
points = {}


def handle_client(conn, addr, num):
    print(f"Connection established with {addr}.")
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break
            message = data.decode()
            print(f"Received from {addr}: {message}")
            if message == 'give me':
                if addr[0] not in nums:
                    nums[addr[0]] = num
                    num = nums[addr[0]]
                    conn.sendall(f"{num}".encode())
                else:
                    print(nums[addr[0]])
                    conn.sendall(f"{nums[addr[0]]}".encode())

            elif message == 'give me points':
                if addr[0] not in points:
                    points[addr[0]] = 0
                    point = points[addr[0]]
                    conn.sendall(f"{point}".encode())
                else:
                    if points[addr[0]] < 0:
                        points[addr[0]] = 0
                    conn.sendall(f"{points[addr[0]]}".encode())


            elif message == 'I showed':
                try:
                    min_num = min(nums.values())
                except ValueError:
                    conn.sendall("not game".encode())
                try:
                    if nums[addr[0]] == min_num:
                        conn.sendall("you won!".encode())
                        nums.pop(addr[0])
                        points[addr[0]] = points.get(addr[0], 0) + 1
                    else:
                        conn.sendall("you lost!".encode())
                        nums.pop(addr[0])
                        points[addr[0]] = points.get(addr[0], 0) - 1
                except KeyError:
                    conn.sendall("you are not in the game".encode())

            elif message == 'I leave':
                    nums.pop(addr[0])
                    # max_points = max(points.values())
                    # if points[addr[0]] == max_points:
                    #     conn.sendall("you won the whole game!!")
                    # else:
                    #     conn.sendall("you lost the whole game!!")
                    points.pop(addr[0])
                    print(f"Player {addr[0]} has left the game.")
                    break

        except ConnectionResetError:
            print(f"Client {addr} has disconnected.")
            break
    conn.close()
    print(f"Connection with {addr} closed.")


def start_server():
    print("start_server")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"Server listening on {HOST}:{PORT}...")
        code = find_code()
        print("Connect code:", code)
        while True:
            conn, addr = server_socket.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr, random.randint(1, max))).start()
            print(f"Active connections: {threading.active_count() - 1}")
            print(nums)


def start_server_in_background():
    print("start_server_in_background")
    thread = threading.Thread(target=start_server, daemon=True)
    thread.start()
    return "Server started"


# --- BeeWare/Toga UI Application ---

class HomeApp(toga.App):
    def startup(self):
        # Create the main window.
        self.main_window = toga.MainWindow(title="THE MIND")

        # Create three boxes to act as our "screens"
        self.home_box = self.create_home_box()
        self.server_box = self.create_server_box()
        self.game_box = self.create_game_box()

        # Start with the home screen.
        self.main_window.content = self.home_box
        self.main_window.show()

    def create_home_box(self):
        box = toga.Box(style=stl_home_btn_box)
        title = toga.Label("🎮 Ready to play?\nLet's go! 🎲", style=stl_home_title)
        box.add(title)

        # Row for Host and Client options
        options_box = toga.Box(style=stl_options_box)

        # Client section: text input and connect button
        client_box = toga.Box(style=stl_client_box)
        self.client_ip_input = toga.TextInput(placeholder="Connect code (IP)", style=stl_client_ip_input)
        connect_button = toga.Button("Connect", on_press=self.on_connect_press, style=stl_connect_button)
        client_box.add(self.client_ip_input)
        client_box.add(connect_button)

        options_box.add(client_box)
        box.add(options_box)

        # Host button
        host_button = toga.Button("Host", on_press=self.go_to_server, style=stl_host_button)
        options_box.add(host_button)

        self.tutorial_label = toga.MultilineTextInput(value=HELP_TEXT, readonly=True, style=stl_tutorial_label)

        box.add(self.tutorial_label)

        scrollveiw = toga.ScrollContainer(style=stl_scrollview, content=box)

        return scrollveiw

    def set_max_number_value(self, value):
        print(value)
        if value == 0:
            state = 100
        else:
            state = value * 1000
        self.max_number_label.text = f"max number : {state}"
        set_max(state)

    def create_server_box(self):
        box = toga.Box(style=stl_create_server_box)
        self.server_status_label = toga.Label("Press 'Start Server' to begin hosting", style=stl_server_status_label)
        box.add(self.server_status_label)

        self.max_number_label = toga.Label("max number : 100", style=stl_max_number_label)
        self.slider = toga.Slider(min=0, max=1000, value=0, style=stl_max_number_slider,
                                    on_change=lambda slider: self.set_max_number_value(int(self.slider.value)))
        box.add(self.max_number_label)
        box.add(self.slider)

        start_button = toga.Button("Start Server", on_press=self.start_server_thread, style=stl_start_button)
        back_button = toga.Button("Back to Home", on_press=self.go_home, style=stl_back_button)
        box.add(start_button)
        box.add(back_button)

        game_img = toga.Image(self.paths.app / "resources/icon.png")
        img = toga.ImageView(game_img, style=stl_game_img)
        box.add(img)

        return box

    def create_game_box(self):
        box = toga.Box(style=stl_create_game_box)
        self.number_label = toga.Label("Your number: ", style=stl_number_label)
        self.points_lable = toga.Label("your points will show here", style=stl_points_lable)
        self.ip_label = toga.Label("", style=stl_ip_label)

        self.show_button = toga.Button("SHOW", on_press=self.on_show_press, style=stl_show_button)
        self.leave_button = toga.Button("give up and leave!", on_press=self.leave_game, style=stl_back_button)

        game_img_win = toga.Image(self.paths.app / "resources/win.png")
        self.state_win_img = toga.ImageView(image=game_img_win, style=stl_game_win_img)

        game_img_lost = toga.Image(self.paths.app / "resources/lost.png")
        self.state_lost_img = toga.ImageView(image=game_img_lost, style=stl_game_lose_img)

        box.add(self.number_label)
        box.add(self.points_lable)
        box.add(self.ip_label)
        box.add(self.show_button)
        box.add(self.leave_button)
        box.add(self.state_win_img)
        box.add(self.state_lost_img)
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
            self.tutorial_label.value = HELP_TEXT + "\n\n   error:\n" + '\n     ' + error_text

    async def start_server_thread(self, widget):
        code = find_code()  # Assume this returns the device's IP code.
        self.server_status_label.text = f"{start_server_in_background()}!\nConnect code: {code}\nListening on port {PORT}"
        await asyncio.sleep(1)
        self.auto_connect_client()

    def auto_connect_client(self):
        print(f"Auto-connecting to host")
        host = find_code()
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
            self.tutorial_label.value = HELP_TEXT + "\n\n   error:\n" + '\n     ' + error_text

    def set_game_screen(self, number, host):
        self.number_label.text = f"Your number: {number}"
        self.ip_label.text = f"Code (IP): {host}"
        # self.points_lable.text = "Game in progress..."

    async def on_show_press(self, widget):
        # When SHOW is pressed, send the "I showed" command to the server.
        host_text = self.ip_label.text.replace("Code (IP): ", "").strip()
        self.show_button.text = 'showing in 3...'
        await asyncio.sleep(1)
        self.show_button.text = 'showing in 2...'
        await asyncio.sleep(1)
        self.show_button.text = 'showing in 1...'
        await asyncio.sleep(1)
        self.show_button.text = 'showed'

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((host_text, PORT))
                client_socket.sendall("I showed".encode())
                data = client_socket.recv(1024)
                response = data.decode()
                self.points_lable.text = f"{response}"
                if response == "you won!":
                    self.state_win_img.visibility = "visible"
                    await asyncio.sleep(2)
                elif response == "you lost!":
                    self.state_lost_img.visibility = "visible"
                    await asyncio.sleep(2)
                elif response == "not game":
                    self.points_lable.text = "the game has ended, please restart."
                    await asyncio.sleep(2)
            self.show_button.text = "show"

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((host_text, PORT))
                client_socket.sendall("give me points".encode())
                data = client_socket.recv(1024)
                points = data.decode()
                self.points_lable.text = f"{points}"

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((host_text, PORT))
                client_socket.sendall("give me".encode())
                data = client_socket.recv(1024)
                number = data.decode()
                print("Received number: ", number)
                self.set_game_screen(number, host_text)
                self.main_window.content = self.game_box

        except Exception as e:
            self.points_lable.text = f"Error: {e}"
            print(e)

    async def leave_game(self, widget):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((self.ip_label.text.replace("Code (IP): ", "").strip(), PORT))
            client_socket.sendall("I leave".encode())
            data = client_socket.recv(1024)
            response = data.decode()
            print(response)
    
        self.points_lable.text = f"{response}"
        await asyncio.sleep(3)
        self.main_window.content = self.home_box


def main():
    return HomeApp('HomeApp', 'org.beeware.homeapp')


if __name__ == '__main__':
    main().main_loop()
