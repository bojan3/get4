import math
from kivy.config import Config
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Line
import numpy as np
from threading import Thread, Lock
from kivy.properties import Clock
import random
from kivy.clock import Clock

Config.set('graphics', 'width', '700')
Config.set('graphics', 'height', '600')

TABLE_SIZE = 5
PLAYER_SYM = 1
AI_SYM = 2



class Move:
    def __init__(self, pos):
        self.position = pos
        self.points = -1000


class TicGame(Widget):
    vertical_lines = []
    horizontal_lines = []
    one_ikss = []
    two_ikss = []
    one_okss = []
    two_okss = []
    end = False

    def __init__(self, **kwargs):
        super(TicGame, self).__init__(**kwargs)
        self.board = np.zeros([5, 5])
        self.init_vertical_lines()
        self.init_horizontal_lines()
        self.init_iks()
        self.init_okss()
        Clock.schedule_interval(self.update_all, 1.0 / 10.0)

    def on_touch_up(self, touch):
        offset_x = self.width * .05
        offset_y = self.height * .05
        field_width = (self.width - 2 * offset_x) / TABLE_SIZE
        field_height = (self.height - 2 * offset_y) / TABLE_SIZE
        x = int((touch.pos[0] - offset_x) / field_width)
        y = int((touch.pos[1] - offset_y) / field_height)
        self.board[TABLE_SIZE - 1 - y, x] = 1
        self.ai_turn()

    def on_size(self, *args):
        self.update_vertical_lines()
        self.update_horizontal_lines()

    def update_all(self, dt):
        if winning_move(self.board, AI_SYM):
            print("AI WIN!")
        elif winning_move(self.board, PLAYER_SYM):
            print("PLAYER WIN!")
        self.update_table()

    def ai_turn(self):
        # x, y = random.choice(get_valid_actions())
        # x, y = get_best_action(self.board, AI_SYM)
        x, y = minimax(self.board, 3, True)[0]
        print('score: ', minimax(self.board, 2, True)[1])
        self.board[x, y] = 2

    def init_okss(self):
        with self.canvas:
            Color(0, 1, 0)
            for i in range(0, 25):
                self.one_okss.append(Line(points=[0, 0, 0, 0]))
                self.two_okss.append(Line(points=[0, 0, 0, 0]))

    def init_iks(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, 25):
                self.one_ikss.append(Line(points=[0, 0, 0, 0]))
                self.two_ikss.append(Line(points=[0, 0, 0, 0]))

    def init_vertical_lines(self):
        with self.canvas:
            Color(1, 1, 1)
            line_space = int(self.width / TABLE_SIZE)
            for i in range(TABLE_SIZE - 1):
                self.vertical_lines.append(Line(points=[0, 0, 0, 0]))

    def update_vertical_lines(self):
        line_space = int(self.width / TABLE_SIZE)
        offset = .05 * self.width
        for i in range(TABLE_SIZE - 1):
            self.vertical_lines[i].points = [line_space * (i + 1), offset, line_space * (i + 1), self.height - offset]

    def init_horizontal_lines(self):
        with self.canvas:
            Color(1, 1, 1)
            line_space = int(self.height / 3)
            for i in range(TABLE_SIZE - 1):
                self.horizontal_lines.append(Line(points=[0, 0, 0, 0]))

    def update_horizontal_lines(self):
        line_space = int(self.height / TABLE_SIZE)
        offset = .05 * self.width
        for i in range(TABLE_SIZE - 1):
            self.horizontal_lines[i].points = [offset, line_space * (i + 1), self.width - offset, line_space * (i + 1)]

    def update_table(self):
        spacing = int(self.width / TABLE_SIZE)
        h_spacing = int(self.height / TABLE_SIZE)
        mat = np.transpose(self.board)
        for x in range(0, TABLE_SIZE):
            for y in range(0, TABLE_SIZE):
                if mat[x, y] == 1:
                    tl_x = x * spacing + .05 * self.width
                    tl_y = (TABLE_SIZE - y) * h_spacing - .05 * self.height
                    tr_x = (x + 1) * spacing - .05 * self.width
                    tr_y = tl_y

                    bl_x = tl_x
                    bl_y = (TABLE_SIZE - 1 - y) * h_spacing + .05 * self.height
                    br_x = tr_x
                    br_y = bl_y

                    self.one_ikss[x * TABLE_SIZE + y].points = [tl_x, tl_y, br_x, br_y]
                    self.two_ikss[x * TABLE_SIZE + y].points = [tr_x, tr_y, bl_x, bl_y]
                if mat[x, y] == 2:
                    tl_x = x * spacing + .05 * self.width
                    tl_y = (TABLE_SIZE - y) * h_spacing - .05 * self.height
                    tr_x = (x + 1) * spacing - .05 * self.width
                    tr_y = tl_y

                    bl_x = tl_x
                    bl_y = (TABLE_SIZE - 1 - y) * h_spacing + .05 * self.height
                    br_x = tr_x
                    br_y = bl_y

                    self.one_okss[x * TABLE_SIZE + y].points = [tl_x, tl_y, br_x, br_y]
                    self.two_okss[x * TABLE_SIZE + y].points = [tr_x, tr_y, bl_x, bl_y]


class TicApp(App):
    pass


# -----------------------AI-----------------------


def get_best_action(board, piece):
    best_score = -9999999
    valid_actions = get_valid_actions()
    best_action = random.choice(valid_actions)
    # print(valid_actions)
    for action in valid_actions:
        temp_board = board.copy()
        print('matrix', temp_board)
        x, y = action
        temp_board[x, y] = piece
        score = score_action(temp_board, AI_SYM)
        print(score)
        if score > best_score:
            best_score = score
            best_action = action
    return best_action


def winning_move(board, piece):
    # Horizontal
    for c in range(TABLE_SIZE - 3):
        for r in range(TABLE_SIZE):
            if board[r][c] == piece and board[r][c + 1] == piece and board[r][c + 2] == piece and board[r][
                c + 3] == piece:
                return True
    # Vertical
    for r in range(TABLE_SIZE - 3):
        for c in range(TABLE_SIZE):
            if board[r][c] == piece and board[r + 1][c] == piece and board[r + 2][c] == piece and board[r + 3][
                c] == piece:
                return True
    # Positive slops
    for r in range(TABLE_SIZE - 3):
        for c in range(TABLE_SIZE - 3):
            if board[r][c] == piece and board[r + 1][c + 1] == piece and board[r + 2][c + 2] == piece and \
                    board[r + 3][c + 3] == piece:
                return True
    # Negative slops
    for c in range(TABLE_SIZE - 3):
        for r in range(3, TABLE_SIZE):
            if board[r][c] == piece and board[r - 1][c + 1] == piece and board[r - 2][c + 2] == piece and \
                    board[r - 3][c + 3] == piece:
                return True
    return False


def score_action(poss_board, piece):
    score = 0
    # Horizontal
    for r in range(TABLE_SIZE):
        row_array = [int(i) for i in list(poss_board[r, :])]
        for c in range(TABLE_SIZE - 3):
            section = row_array[c:c + 4]
            # score += section_score(window, piece)
            if section.count(piece) == 4:
                score += 100
            elif section.count(piece) == 3 and section.count(0) == 1:
                score += 10
            elif section.count(piece) == 2 and section.count(0) == 2:
                score += .1

    # Vertical
    for c in range(TABLE_SIZE):
        column_array = [int(i) for i in list(poss_board[:, c])]
        for r in range(TABLE_SIZE - 3):
            window = column_array[r:r + 4]
            score += section_score(window, piece)
    # Postive sloped diagonal
    for r in range(TABLE_SIZE - 3):
        for c in range(TABLE_SIZE - 3):
            window = [poss_board[r + i][c + i] for i in range(4)]
            score += section_score(window, piece)
    # Negative sloped diagonal
    for r in range(TABLE_SIZE - 3):
        for c in range(TABLE_SIZE - 3):
            window = [poss_board[r + 3 - i][c + i] for i in range(4)]
            score += section_score(window, piece)
    return score


def section_score(section, piece):
    score = 0
    opp_piece = PLAYER_SYM
    # if piece == PLAYER_SYM:
    #     opp_piece = AI_SYM
    if section.count(piece) == 4:
        score += 100
    elif section.count(piece) == 3 and section.count(0) == 1:
        score += 10
    elif section.count(piece) == 2 and section.count(0) == 2:
        score += 1
    elif section.count(opp_piece) == 3 and section.count(0) == 1:
        score -= 80
    return score


def get_valid_actions(board):
    valid_actions = []
    for row in range(TABLE_SIZE):
        for col in range(TABLE_SIZE):
            if board[col, row] == 0:
                valid_actions.append([col, row])
    return valid_actions


def is_terminal_node(board):
    return winning_move(board, PLAYER_SYM) or winning_move(board, AI_SYM)


def minimax(node, depth, maximizingPlayer):
    valid_actions = get_valid_actions(node)
    is_terminal = is_terminal_node(node)

    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(node, AI_SYM):
                print('ai_win')
                return None, 100000000000
            if winning_move(node, PLAYER_SYM):
                print('player_win')
                return None, -100000000000
            else:
                print('none_win')
                return None, 0
        else:
            # print('depth==0')
            # print(node)
            return None, score_action(node, AI_SYM)
    # maximizingPlayer
    if maximizingPlayer:
        max_score = -math.inf
        best_action = random.choice(valid_actions)
        for action in valid_actions:
            temp_board = node.copy()
            x, y = action
            temp_board[x, y] = AI_SYM
            score = minimax(temp_board, depth-1, False)[1]
            if score > max_score:
                max_score = score
                best_action = action
        print('max', max_score)
        return best_action, max_score
    # minimizingPlayer
    else:
        min_score = math.inf
        best_action = random.choice(valid_actions)
        for action in valid_actions:
            temp_board = node.copy()
            x, y = action
            temp_board[x, y] = PLAYER_SYM
            score = minimax(temp_board, depth-1, True)[1]
            if score < min_score:
                min_score = score
                best_action = action
        print('min', min_score)
        return best_action, min_score

# ------------------------------------------------


if __name__ == "__main__":
    TicApp().run()









