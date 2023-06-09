#
# Othellomino.py 2022/9/17
#
import pyxel
import random
#import copy

WINDOW_WIDTH =  256  # 32*8
WINDOW_HEIGHT = 144  # 18*8
BOARD_X = 8*8
BOARD_Y = 8
BOARD_SIZE = 8*16
BLACK = 0
WHITE = 1
HUMAN = 0
COMPUTER = 1
OPPONENT = {BLACK: WHITE, WHITE: BLACK}
SHAPE9TO4 = (0, 1, 1, 2, 2, 3, 3, 3, 3)
NEXT_SHAPE_DIRECT = (0, 2, 1, 4, 3, 6, 7, 8, 5)
CONNECT9 = (((0, 0),),  # SINGLE
           ((0, 0), (1, 0)),  # DOUBLE
           ((0, 0), (0, 1)),
           ((0, 0), (1, 0), (2, 0)),  # TRIPLE
           ((0, 0), (0, 1), (0, 2)),
           ((0, 0), (0, 1), (1, 1)),  # KUNOJI
           ((1, 0), (1, 1), (0, 1)),
           ((0, 0), (0, 1), (1, 0)),
           ((0, 0), (1, 0), (1, 1)))
DIRECT8 = ((-1, -1), (0, -1), (1, -1),
           (-1,  0),          (1,  0),
           (-1,  1), (0,  1), (1,  1))
HAND_XY = (((29*8, 5*8), (25*8, 8*8), (25*8, 8), (25*8, 13*8)),
           (( 5*8, 5*8), (   8, 8*8), (   8, 8), (   8, 13*8)))

class Stone:
    def __init__(self):
        self.hand_stones = [[6, 6, 1, 3], [6, 6, 1, 3]]
        self.hand_direct = [[0, 1, 3, 5], [0, 1, 3, 5]]
        self.click_shape = -1
        self.click_x = self.click_y = -1
    
    def set_hand_stones(self, stones):
        self.hand_stones = stones
    
    def place(self, turn, shape):
        s = SHAPE9TO4[shape]
        if self.hand_stones[turn][s] > 0:
            self.hand_stones[turn][s] -= 1
            return True
        else:
            return False
    
    def display_stone(self, turn, shape, x, y):
        if shape == 0:  # SINGLE
            pyxel.bltm(x, y, 0,  0*8, turn*64, 2*8, 2*8, 15)
        elif shape == 1:  # DOUBLE
            pyxel.bltm(x, y, 0,  2*8, turn*64, 4*8, 2*8, 15)
        elif shape == 2:
            pyxel.bltm(x, y, 0,  6*8, turn*64, 2*8, 4*8, 15)
        elif shape == 3:  # TRIPLE
            pyxel.bltm(x, y, 0,  8*8, turn*64, 6*8, 2*8, 15)
        elif shape == 4:
            pyxel.bltm(x, y, 0, 14*8, turn*64, 2*8, 6*8, 15)
        elif shape == 5:  # KUNOJI
            pyxel.bltm(x, y, 0, 16*8, turn*64, 4*8, 4*8, 15)
        elif shape == 6:
            pyxel.bltm(x, y, 0, 20*8, turn*64, 4*8, 4*8, 15)
        elif shape == 7:
            pyxel.bltm(x, y, 0, 24*8, turn*64, 4*8, 4*8, 15)
        elif shape == 8:
            pyxel.bltm(x, y, 0, 28*8, turn*64, 4*8, 4*8, 15)
    
    def display_hand_stone(self):
        for turn in range(2):
            for i, direct in enumerate(self.hand_direct[turn]):
                if self.hand_stones[turn][i]:
                    x, y = HAND_XY[turn][i]
                    self.display_stone(turn, self.hand_direct[turn][i], x, y)
                    cx, cy = CONNECT9[self.hand_direct[turn][i]][0]
                    if self.hand_stones[turn][i] < 40:
                        pyxel.text(x+cx*16+6, y+6, f'{self.hand_stones[turn][i]}', 8)
    
    def hand_stone_rotate(self, turn, mouse_x, mouse_y):
        for i, direct in enumerate(self.hand_direct[turn]):
            x, y = HAND_XY[turn][i]
            for rx, ry in CONNECT9[direct]:
                if x+rx*16-8 <= mouse_x < x+rx*16+16+8 and y+ry*16-8 <= mouse_y < y+ry*16+16+8:
                    self.hand_direct[turn][i] = NEXT_SHAPE_DIRECT[self.hand_direct[turn][i]]
                    break
            else:
                continue
            break
    
    def click(self, turn, mouse_x, mouse_y):
        self.click_shape = -1
        for i, direct in enumerate(self.hand_direct[turn]):
            x, y = HAND_XY[turn][i]
            for rx, ry in CONNECT9[direct]:
                if x+rx*16 <= mouse_x < x+rx*16+16 and y+ry*16 <= mouse_y < y+ry*16+16:
                    self.click_shape = self.hand_direct[turn][i]
                    self.click_x = mouse_x - x
                    self.click_y = mouse_y - y
                    break
            else:
                continue
            break
    
    def drag(self, turn, mouse_x, mouse_y):
        if not self.click_shape == -1:
            self.display_stone(turn, self.click_shape, mouse_x-self.click_x, mouse_y-self.click_y)
    
    def drop(self, turn, mouse_x, mouse_y):
        if not self.click_shape == -1:
            bx = mouse_x-self.click_x-BOARD_X+6
            by = mouse_y-self.click_y-BOARD_Y+6
            if 0 <= bx < 8*16+12 and 0 <= by < 8*16+12:
                if 0 <= (bx%16) < 12 and 0 <= (by%16) < 12:
                    return [bx//16, by//16, self.click_shape]
        return -1, -1, -1

class Board:
    def __init__(self):
        self.board = [[0]*8 for _ in range(8)]  # 符号:先手後手, 百:手数, 十:形, 一:接続
        self.board[3][4] =  100
        self.board[4][3] =  300
        self.board[3][3] = -200
        self.board[4][4] = -400
        self.moves = 5
    
    def display(self):
        for y in range(8):
            for x in range(8):
                n = self.board[x][y]
                if n:  # 黒と白
                    shape = (abs(n) // 10) % 10
                    cx, cy = CONNECT9[shape][0]
                    if abs(n) % 10 == 0:
                        Stone.display_stone(self, BLACK if n>0 else WHITE, shape, BOARD_X+x*16-cx*16, BOARD_Y+y*16)
        black, white = self.count_on_board()
        pyxel.text(BOARD_X+118, BOARD_Y+130, f'{black}', 0)
        pyxel.text(BOARD_X+  6, BOARD_Y+130, f'{white}', 7)
    
    def place(self, x, y, turn, shape):
        flip_board = [[0]*8 for _ in range(8)]
        for connect, (dx, dy) in enumerate(CONNECT9[shape]):
            if turn == BLACK:
                self.board[x+dx][y+dy] =  (100*self.moves+10*shape+connect)  # 黒置く
            else:
                self.board[x+dx][y+dy] = -(100*self.moves+10*shape+connect)  # 白置く
            for ex, ey in DIRECT8:
                n = self.count_flip(x+dx, y+dy, ex, ey, turn)
                for i in range(1, n+1):
                   flip_board[x+dx+i*ex][y+dy+i*ey] = 1  # 裏返す
        self.moves += 1
        for dy in range(8):
            for dx in range(8):
                if flip_board[dx][dy] == 1:
                    n = abs(self.board[dx][dy]) // 100
                    for ey in range(8):
                        for ex in range(8):
                            if abs(self.board[ex][ey]) // 100 == n:
                                flip_board[ex][ey] = 2
        for dy in range(8):
            for dx in range(8):
                if flip_board[dx][dy] == 2:
                    self.board[dx][dy] = -self.board[dx][dy]
    
    def count_flip(self, x, y, dx, dy, turn):
        for n in range(8):
            x += dx
            y += dy
            if not (0 <= x < 8 and 0 <= y < 8):
                return 0
            if self.board[x][y] == 0:  # 空
                return 0
            if (turn == BLACK and self.board[x][y] > 0) or (turn == WHITE and self.board[x][y] < 0):
                return n
        return 0
    
    def is_placeable(self, x, y, turn):
        if self.board[x][y]:  # 駒あり
            return False
        return any(self.count_flip(x, y, dx, dy, turn) > 0 for dx, dy in DIRECT8)
    
    def placeable_xy(self, turn, hand_stones):
        placeable_1sotne = [(x, y) for x in range(8) for y in range(8) if self.is_placeable(x, y, turn)]
        placeable = []
        for ax, ay in placeable_1sotne:
            for shape in range(9):
                for dx, dy in CONNECT9[shape]:
                    for ex, ey in CONNECT9[shape]:
                        if not (0 <= ax-dx+ex < 8 and 0 <= ay-dy+ey < 8):
                            break
                        if self.board[ax-dx+ex][ay-dy+ey]:  # 駒あり
                            break
                    else:
                        placeable.extend([[shape, ax-dx, ay-dy]])
        placeable = list(map(list, set(map(tuple, placeable))))  # 重複削除
        placeable = [[shape, x, y] for shape, x, y in placeable if hand_stones[SHAPE9TO4[shape]]]  # 持ち駒無し削除
        return placeable
    
    def count_on_board(self):
        black = white = 0
        for y in range(8):
            for x in range(8):
                if self.board[x][y] > 0:
                    black += 1
                if self.board[x][y] < 0:
                    white += 1
        return black, white

class Com:
    def __init__(self):
        pass
    
    def next_move(self, turn, board, moves, hand_stones, placeable):
        min_count, (shape, x, y) = self.opponet_min(turn, board, moves, hand_stones, placeable)
        if min_count == 0:
            return shape, x, y
        else:
            cshape, cx, cy = self.corner(placeable)
            if cshape == -1:
                return shape, x, y
            else:
                return cshape, cx, cy
    
    def opponet_min(self, turn, board, moves, hand_stones, placeable):
        count_placeable = []
        next_placeable = []
        next_board = Board()
        for shape, x, y in placeable:
            next_board.moves = moves
            #next_board.board = copy.deepcopy(board)
            next_board.board = [[board[i][j] for j in range(len(board[0]))] for i in range(len(board))]
            next_board.place(x, y, turn, shape)
            next_placeable = next_board.placeable_xy(OPPONENT[turn], hand_stones[OPPONENT[turn]])
            cshape, cx, cy = self.corner(next_placeable)
            if cshape == -1:
                count_placeable.append(len(next_placeable))
            else:
                count_placeable.append(len(next_placeable)+1000)
        min_count = min(count_placeable)
        min_indices = [i for i, v in enumerate(count_placeable) if v == min_count]
        return min_count, placeable[random.choice(min_indices)]
    
    def corner(self, placeable):
        corner_indices = []
        for i, (shape, x, y) in enumerate(placeable):
            for dx, dy in CONNECT9[shape]:
                ex = x+dx
                ey = y+dy
                if (ex==0 and ey==0) or (ex==7 and ey==0) or (ex==0 and ey==7) or (ex==7 and ey==7):
                    corner_indices.append(i)
        if corner_indices:
            return placeable[random.choice(corner_indices)]
        else:
            return -1, -1, -1

class App:
    def game_init(self):
        self.is_title = True
        self.is_gameover = False
        self.board = Board()
        self.turn = BLACK
        self.both_pass = [0, 0]
        self.is_drag = 0
        self.placeable = self.board.placeable_xy(self.turn, self.stone.hand_stones[self.turn])
    
    def __init__(self):
        self.player = [HUMAN, HUMAN]
        self.stone = Stone()
        self.com = Com()
        self.game_init()
        pyxel.init(32*8, 18*8, title="Othellomino")
        pyxel.load('assets/Othellomino.pyxres')
        pyxel.mouse(True)
        pyxel.run(self.update, self.draw)
    
    def update(self):
        if self.is_title:
            if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):  # LEFT_UP
                if BOARD_X      <= pyxel.mouse_x < BOARD_X+ 4*8 and 10*8 <= pyxel.mouse_y < 12*8:
                    self.stone.set_hand_stones([[ 6, 6, 1, 3], [ 6, 6, 1, 3]])
                elif BOARD_X+ 4*8 <= pyxel.mouse_x < BOARD_X+ 8*8 and 10*8 <= pyxel.mouse_y < 12*8:
                    self.stone.set_hand_stones([[99, 0, 0, 0], [99, 0, 0, 0]])
                elif BOARD_X+ 8*8 <= pyxel.mouse_x < BOARD_X+12*8 and 10*8 <= pyxel.mouse_y < 12*8:
                    self.stone.set_hand_stones([[99, 4, 0, 0], [99, 4, 0, 0]])
                elif BOARD_X+12*8 <= pyxel.mouse_x < BOARD_X+20*8 and 10*8 <= pyxel.mouse_y < 12*8:
                    self.stone.set_hand_stones([[99, 0, 2, 0], [99, 0, 2, 0]])
                elif BOARD_X      <= pyxel.mouse_x < BOARD_X+ 4*8 and 12*8 <= pyxel.mouse_y < 14*8:
                    self.stone.set_hand_stones([[99, 0, 0, 4], [99, 0, 0, 4]])
                elif BOARD_X+ 4*8 <= pyxel.mouse_x < BOARD_X+ 8*8 and 12*8 <= pyxel.mouse_y < 14*8:
                    self.stone.set_hand_stones([[99, 99, 99, 99], [99, 99, 99, 99]])
                elif BOARD_X+ 8*8 <= pyxel.mouse_x < BOARD_X+12*8 and 12*8 <= pyxel.mouse_y < 14*8:
                    self.stone.set_hand_stones([[ 0, 99, 99, 99], [ 0, 99, 99, 99]])
                elif BOARD_X+12*8 <= pyxel.mouse_x < BOARD_X+20*8 and 12*8 <= pyxel.mouse_y < 14*8:
                    self.stone.set_hand_stones([[2, 2, 2, 2], [2, 2, 2, 2]])
                elif BOARD_X <= pyxel.mouse_x < BOARD_X+BOARD_SIZE and 0 <= pyxel.mouse_y < 8*8:
                    self.game_init()
                    self.is_title = False
            return
        if self.is_gameover:
            if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):  # LEFT_UP
                self.stone.set_hand_stones([[6, 6, 1, 3], [6, 6, 1, 3]])
                self.is_title = True
                self.is_gameover = False
            return
        shape = x = y = -1
        if self.player[self.turn] == COMPUTER:
            # shape, x, y = random.choice(self.placeable)
            shape, x, y = self.com.next_move(self.turn, self.board.board, self.board.moves, self.stone.hand_stones, self.placeable)
        elif pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):  # LEFT_UP
            if pyxel.btnp(pyxel.MOUSE_BUTTON_RIGHT, hold=1, repeat=1):  # RIGHT_DRAG
                self.stone.set_hand_stones([[6, 6, 1, 3], [6, 6, 1, 3]])
                self.is_title = True
                self.is_gameover = False
                return
            self.stone.hand_stone_rotate(self.turn, pyxel.mouse_x, pyxel.mouse_y)
            x, y, shape = self.stone.drop(self.turn, pyxel.mouse_x, pyxel.mouse_y)
        if [shape, x, y] in self.placeable:
            if self.stone.place(self.turn, shape):
                self.board.place(x, y, self.turn, shape)
                #self.draw()
                #pyxel.flip()
                for i in range(2):
                    self.turn = OPPONENT[self.turn]
                    self.placeable = self.board.placeable_xy(self.turn, self.stone.hand_stones[self.turn])
                    if not self.placeable:
                        self.both_pass[self.turn] = 1
                        if all(self.both_pass):
                            self.is_gameover = True
                            break
                        else:
                            continue
                    if i == 0:
                        self.both_pass = [0, 0]
                        break
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):  # LEFT_DOWN
            self.stone.click(self.turn, pyxel.mouse_x, pyxel.mouse_y)
        self.is_drag = pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT, hold=1, repeat=1)  # LEFT_DRAG
    
    def draw_board(self):
        pyxel.rectb(BOARD_X-1, BOARD_Y-1, 16*8+2, 16*8+2, 0)
        pyxel.rectb(BOARD_X  , BOARD_Y  , 16*8  , 16*8  , 0)
        pyxel.rect( BOARD_X+1, BOARD_Y+1, 16*8-2, 16*8-2, 3)
        for i in range(1, 8):
            pyxel.line(BOARD_X+1,      BOARD_Y+i*16-1, BOARD_X+8*16-2, BOARD_Y+i*16-1, 1)
            pyxel.line(BOARD_X+1,      BOARD_Y+i*16  , BOARD_X+8*16-2, BOARD_Y+i*16  , 1)
            pyxel.line(BOARD_X+i*16-1, BOARD_Y+1,      BOARD_X+i*16-1, BOARD_Y+8*16-2, 1)
            pyxel.line(BOARD_X+i*16  , BOARD_Y+1,      BOARD_X+i*16  , BOARD_Y+8*16-2, 1)
    
    def draw(self):
        pyxel.cls(5)
        if self.is_title:
            self.stone.display_hand_stone()
            if BOARD_X <= pyxel.mouse_x < BOARD_X+BOARD_SIZE and 0 <= pyxel.mouse_y < 2*8:
                pyxel.text(11*8, 8, 'HUMAN    vs HUMAN', 4)
                self.player[BLACK] = HUMAN
                self.player[WHITE] = HUMAN
            else:
                pyxel.text(11*8, 8, 'HUMAN', 7)
                pyxel.text(11*8, 8, '         vs', 10)
                pyxel.text(11*8, 8, '            HUMAN', 0)
            if BOARD_X <= pyxel.mouse_x < BOARD_X+BOARD_SIZE and 2*8 <= pyxel.mouse_y < 4*8:
                pyxel.text(11*8, 3*8, 'Computer vs Computer', 4)
                self.player[BLACK] = COMPUTER
                self.player[WHITE] = COMPUTER
            else:
                pyxel.text(11*8, 3*8, 'Computer', 7)
                pyxel.text(11*8, 3*8, '         vs', 10)
                pyxel.text(11*8, 3*8, '            Computer', 0)
            if BOARD_X <= pyxel.mouse_x < BOARD_X+BOARD_SIZE and 4*8 <= pyxel.mouse_y < 6*8:
                pyxel.text(11*8, 5*8, 'Computer vs HUMAN', 4)
                self.player[BLACK] = HUMAN
                self.player[WHITE] = COMPUTER
            else:
                pyxel.text(11*8, 5*8, 'Computer', 7)
                pyxel.text(11*8, 5*8, '         vs', 10)
                pyxel.text(11*8, 5*8, '            HUMAN', 0)
            if BOARD_X <= pyxel.mouse_x < BOARD_X+BOARD_SIZE and 6*8 <= pyxel.mouse_y < 8*8:
                pyxel.text(11*8, 7*8, 'HUMAN    vs Computer', 4)
                self.player[BLACK] = COMPUTER
                self.player[WHITE] = HUMAN
            else:
                pyxel.text(11*8, 7*8, 'HUMAN', 7)
                pyxel.text(11*8, 7*8, '         vs', 10)
                pyxel.text(11*8, 7*8, '            Computer', 0)
            pyxel.text( 8*8+4, 11*8, 'Mode 1', 4 if BOARD_X      <= pyxel.mouse_x < BOARD_X+ 4*8 and 10*8 <= pyxel.mouse_y < 12*8 else 10)
            pyxel.text(12*8+4, 11*8, 'Mode 2', 4 if BOARD_X+ 4*8 <= pyxel.mouse_x < BOARD_X+ 8*8 and 10*8 <= pyxel.mouse_y < 12*8 else 10)
            pyxel.text(16*8+4, 11*8, 'Mode 3', 4 if BOARD_X+ 8*8 <= pyxel.mouse_x < BOARD_X+12*8 and 10*8 <= pyxel.mouse_y < 12*8 else 10)
            pyxel.text(20*8+4, 11*8, 'Mode 4', 4 if BOARD_X+12*8 <= pyxel.mouse_x < BOARD_X+20*8 and 10*8 <= pyxel.mouse_y < 12*8 else 10)
            pyxel.text( 8*8+4, 13*8, 'Mode 5', 4 if BOARD_X      <= pyxel.mouse_x < BOARD_X+ 4*8 and 12*8 <= pyxel.mouse_y < 14*8 else 10)
            pyxel.text(12*8+4, 13*8, 'Mode 6', 4 if BOARD_X+ 4*8 <= pyxel.mouse_x < BOARD_X+ 8*8 and 12*8 <= pyxel.mouse_y < 14*8 else 10)
            pyxel.text(16*8+4, 13*8, 'Mode 7', 4 if BOARD_X+ 8*8 <= pyxel.mouse_x < BOARD_X+12*8 and 12*8 <= pyxel.mouse_y < 14*8 else 10)
            pyxel.text(20*8+4, 13*8, 'Mode 8', 4 if BOARD_X+12*8 <= pyxel.mouse_x < BOARD_X+20*8 and 12*8 <= pyxel.mouse_y < 14*8 else 10)
            return
        self.draw_board()
        pyxel.text(BOARD_X+6, BOARD_Y-7, 'a   b   c   d   e   f   g   h', 10)
        for i in range(1, 9):
            pyxel.text(BOARD_X-5, BOARD_Y+i*16-10, f'{i}', 10)
        if self.player[BLACK] == HUMAN:
            pyxel.text(25*8, BOARD_Y+130, 'HUMAN', 0)
        else:
            pyxel.text(25*8, BOARD_Y+130, 'Computer', 0)
        if self.player[WHITE] == HUMAN:
            pyxel.text(8, BOARD_Y+130, 'HUMAN', 7)
        else:
            pyxel.text(8, BOARD_Y+130, 'Computer', 7)
        if self.both_pass[BLACK]:
            pyxel.text(BOARD_X+96, BOARD_Y+130, 'Pass', 0)
        if self.both_pass[WHITE]:
            pyxel.text(BOARD_X+16, BOARD_Y+130, 'Pass', 7)
        if all(self.both_pass):
            black, white = self.board.count_on_board()
            if black > white:
                pyxel.text(BOARD_X+46, BOARD_Y+130, 'BLACK Win', pyxel.frame_count%5)
            elif black < white:
                pyxel.text(BOARD_X+46, BOARD_Y+130, 'WHITE Win', (pyxel.frame_count%5)+3)
            else:
                pyxel.text(BOARD_X+56, BOARD_Y+130, 'Draw', 8)
        elif self.turn == BLACK:
            pyxel.text(BOARD_X+44, BOARD_Y+130, 'BLACK Turn', 0)
        else:
            pyxel.text(BOARD_X+44, BOARD_Y+130, 'WHITE Turn', 7)
        self.board.display()
        self.stone.display_hand_stone()
        if self.is_drag:
            self.stone.drag(self.turn, pyxel.mouse_x, pyxel.mouse_y)

App()
