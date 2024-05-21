import kivy
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
import sqlite3

kivy.require('2.0.0')

def check_winner(board):
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] != " ":
            return board[i][0]
        if board[0][i] == board[1][i] == board[2][i] != " ":
            return board[0][i]
    if board[0][0] == board[1][1] == board[2][2] != " ":
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != " ":
        return board[0][2]
    if all(board[i][j] != " " for i in range(3) for j in range(3)):
        return "Draw"
    return None

def minimax(board, depth, is_maximizing, alpha, beta):
    winner = check_winner(board)
    if winner == "X":
        return -1
    elif winner == "O":
        return 1
    elif winner == "Draw":
        return 0

    if is_maximizing:
        max_eval = -float('inf')
        for i in range(3):
            for j in range(3):
                if board[i][j] == " ":
                    board[i][j] = "O"
                    eval = minimax(board, depth + 1, False, alpha, beta)
                    board[i][j] = " "
                    max_eval = max(max_eval, eval)
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
        return max_eval
    else:
        min_eval = float('inf')
        for i in range(3):
            for j in range(3):
                if board[i][j] == " ":
                    board[i][j] = "X"
                    eval = minimax(board, depth + 1, True, alpha, beta)
                    board[i][j] = " "
                    min_eval = min(min_eval, eval)
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
        return min_eval

def random_move(board):
    from random import choice
    empty_cells = [(i, j) for i in range(3) for j in range(3) if board[i][j] == " "]
    move = choice(empty_cells)
    board[move[0]][move[1]] = "O"

def ai_move(board, difficulty):
    if difficulty == "easy":
        random_move(board)
    elif difficulty == "medium":
        if board[1][1] == " ":
            board[1][1] = "O"
        else:
            random_move(board)
    elif difficulty == "hard":
        best_score = -float('inf')
        move = None
        for i in range(3):
            for j in range(3):
                if board[i][j] == " ":
                    board[i][j] = "O"
                    score = minimax(board, 0, False, -float('inf'), float('inf'))
                    board[i][j] = " "
                    if score > best_score:
                        best_score = score
                        move = (i, j)
        board[move[0]][move[1]] = "O"

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

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=[50, 50, 50, 50], spacing=10)

        layout.add_widget(Label(text="Welcome to TicTacToe", font_size=24, size_hint=(1, 0.2), halign='center'))

        self.username_input = TextInput(hint_text="Username", multiline=False, size_hint=(1, 0.2))
        layout.add_widget(self.username_input)

        self.password_input = TextInput(hint_text="Password", multiline=False, password=True, size_hint=(1, 0.2))
        layout.add_widget(self.password_input)

        self.login_button = Button(text="Login", background_color=(0.1, 0.5, 0.7, 1), size_hint=(1, 0.2))
        self.login_button.bind(on_press=self.login)
        layout.add_widget(self.login_button)

        self.register_button = Button(text="Register", background_color=(0.1, 0.7, 0.3, 1), size_hint=(1, 0.2))
        self.register_button.bind(on_press=self.register)
        layout.add_widget(self.register_button)

        self.add_widget(layout)

    def login(self, instance):
        username = self.username_input.text
        password = self.password_input.text
        if authenticate_user(username, password):
            self.manager.current = 'dashboard'
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

class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super(DashboardScreen, self).__init__(**kwargs)
        layout = FloatLayout()

        self.easy_btn = Button(text="Easy", size_hint=(.3, .2), pos_hint={'x': .35, 'y': .6})
        self.medium_btn = Button(text="Medium", size_hint=(.3, .2), pos_hint={'x': .35, 'y': .35})
        self.hard_btn = Button(text="Hard", size_hint=(.3, .2), pos_hint={'x': .35, 'y': .1})

        self.easy_btn.bind(on_press=self.start_game_easy)
        self.medium_btn.bind(on_press=self.start_game_medium)
        self.hard_btn.bind(on_press=self.start_game_hard)

        layout.add_widget(self.easy_btn)
        layout.add_widget(self.medium_btn)
        layout.add_widget(self.hard_btn)

        self.add_widget(layout)

    def start_game_easy(self, instance):
        self.manager.get_screen('game').set_difficulty('easy')
        self.manager.current = 'game'

    def start_game_medium(self, instance):
        self.manager.get_screen('game').set_difficulty('medium')
        self.manager.current = 'game'

    def start_game_hard(self, instance):
        self.manager.get_screen('game').set_difficulty('hard')
        self.manager.current = 'game'

class GameScreen(Screen):
    def __init__(self, **kwargs):
        super(GameScreen, self).__init__(**kwargs)
        self.board = [[" " for _ in range(3)] for _ in range(3)]
        self.layout = GridLayout(cols=3)
        self.buttons = [[Button(font_size=32) for _ in range(3)] for _ in range(3)]
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].bind(on_press=self.on_button_press)
                self.layout.add_widget(self.buttons[i][j])
        self.add_widget(self.layout)
        self.difficulty = 'hard'  # default difficulty

    def set_difficulty(self, difficulty):
        self.difficulty = difficulty
        self.reset_board()

    def reset_board(self):
        self.board = [[" " for _ in range(3)] for _ in range(3)]
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].text = " "

    def on_button_press(self, instance):
        for i in range(3):
            for j in range(3):
                if self.buttons[i][j] == instance:
                    if self.board[i][j] == " ":
                        self.board[i][j] = "X"
                        self.buttons[i][j].text = "X"
                        if check_winner(self.board):
                            self.end_game()
                            return
                        ai_move(self.board, self.difficulty)
                        self.update_board()
                        if check_winner(self.board):
                            self.end_game()
                        return

    def update_board(self):
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].text = self.board[i][j]

    def end_game(self):
        winner = check_winner(self.board)
        content = BoxLayout(orientation='vertical')
        if winner == "Draw":
            content.add_widget(Label(text="It's a draw!"))
        else:
            content.add_widget(Label(text=f"The winner is {winner}!"))
        popup = Popup(title='Game Over', content=content, size_hint=(0.5, 0.5))
        content.add_widget(Button(text='Restart', on_press=lambda x: self.restart_game(popup)))
        popup.open()

    def restart_game(self, popup):
        popup.dismiss()
        self.reset_board()
        self.manager.current = 'dashboard'

class TicTacToeApp(App):
    def build(self):
        self.sm = ScreenManager()
        self.sm.add_widget(LoginScreen(name='login'))
        self.sm.add_widget(DashboardScreen(name='dashboard'))
        self.sm.add_widget(GameScreen(name='game'))
        return self.sm

if __name__ == '__main__':
    TicTacToeApp().run()
