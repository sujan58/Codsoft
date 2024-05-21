import sqlite3
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen

def create_user_table():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()
    return True

def authenticate_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = c.fetchone()
    conn.close()
    return user is not None

create_user_table()

def chatbot_response(user_input):
    user_input = user_input.lower()

    if 'hello' in user_input or 'hi' in user_input:
        return "Hello! How can I help you today?"
    elif 'how are you' in user_input:
        return "I'm just a bot, but I'm here to help you!"
    elif 'bye' in user_input or 'goodbye' in user_input:
        return "Goodbye! Have a great day!"
    elif 'name' in user_input:
        return "I am a simple chatbot created to assist you."
    elif 'help' in user_input:
        return "Sure! How can I assist you today?"
    elif 'weather' in user_input:
        return "I can't check the weather right now, but you can try asking a weather service."
    else:
        return "I'm sorry, I don't understand that. Can you please rephrase?"

class LoginRegisterScreen(BoxLayout):
    def __init__(self, **kwargs):
        super(LoginRegisterScreen, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 10
        self.padding = [50, 50, 50, 50]

        self.add_widget(Label(text="Welcome to ChatBot", font_size=24, size_hint=(1, 0.2), halign='center'))

        self.username_input = TextInput(hint_text="Username", multiline=False, size_hint=(1, 0.2))
        self.add_widget(self.username_input)

        self.password_input = TextInput(hint_text="Password", multiline=False, password=True, size_hint=(1, 0.2))
        self.add_widget(self.password_input)

        self.login_button = Button(text="Login", background_color=(0.1, 0.5, 0.7, 1), size_hint=(1, 0.2))
        self.login_button.bind(on_press=self.login)
        self.add_widget(self.login_button)

        self.register_button = Button(text="Register", background_color=(0.1, 0.7, 0.3, 1), size_hint=(1, 0.2))
        self.register_button.bind(on_press=self.register)
        self.add_widget(self.register_button)

    def login(self, instance):
        username = self.username_input.text
        password = self.password_input.text
        if authenticate_user(username, password):
            App.get_running_app().show_chat_screen()
        else:
            self.show_popup("Login failed", "Invalid username or password")

    def register(self, instance):
        username = self.username_input.text
        password = self.password_input.text
        if add_user(username, password):
            self.show_popup("Registration successful", "You can now login with your credentials")
        else:
            self.show_popup("Registration failed", "Username already exists")

    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(None, None), size=(400, 200))
        popup.open()

class ChatBotApp(App):
    def build(self):
        self.screen_manager = ScreenManager()
        self.login_screen = Screen(name='login')
        self.login_screen.add_widget(LoginRegisterScreen())
        self.chat_screen = Screen(name='chat')
        self.chat_screen.add_widget(self.create_chat_screen())

        self.screen_manager.add_widget(self.login_screen)
        self.screen_manager.add_widget(self.chat_screen)

        return self.screen_manager

    def create_chat_screen(self):
        chat_layout = BoxLayout(orientation='vertical', padding=[10, 10, 10, 10], spacing=10)

        self.chat_history = Label(size_hint_y=None, height=400, text="Chatbot: Hello! I am a simple chatbot. Type 'bye' to exit.\n", valign='top')
        chat_layout.add_widget(self.chat_history)

        self.user_input = TextInput(multiline=False, size_hint_y=None, height=30)
        chat_layout.add_widget(self.user_input)

        self.submit_button = Button(text="Send", size_hint_y=None, height=50, background_color=(0.1, 0.5, 0.7, 1))
        self.submit_button.bind(on_press=self.on_button_press)
        chat_layout.add_widget(self.submit_button)

        return chat_layout

    def show_chat_screen(self):
        self.screen_manager.current = 'chat'

    def on_button_press(self, instance):
        user_message = self.user_input.text
        if user_message.lower() == 'bye':
            self.update_chat_history("Goodbye! Have a great day!")
            self.user_input.disabled = True
            self.submit_button.disabled = True
        else:
            response = chatbot_response(user_message)
            self.update_chat_history(f"You: {user_message}")
            self.update_chat_history(f"Chatbot: {response}")
            self.user_input.text = ""

    def update_chat_history(self, message):
        self.chat_history.text += message + "\n"
        self.chat_history.height += 20

if __name__ == "__main__":
    ChatBotApp().run()
