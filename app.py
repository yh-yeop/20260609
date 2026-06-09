
import streamlit as st
import numpy as np
import random

# -----------------------
# Block
# -----------------------
class Block:
    """블록 데이터"""

    def __init__(self, shape):
        self.shape = np.array(shape, dtype=int)

    def render(self):
        text = ""
        for row in self.shape:
            for cell in row:
                text += "🟦" if cell else "⬜"
            text += "<br>"
        return text


# -----------------------
# Block Factory
# -----------------------
class BlockFactory:

    @staticmethod
    def generate_rotations(shape):
        rotations = []
        current = np.array(shape)

        for _ in range(4):
            if not any(np.array_equal(current, r) for r in rotations):
                rotations.append(current.copy())
            current = np.rot90(current)

        return rotations

    @classmethod
    def build_pool(cls):

        base_blocks = [

            [[1]],

            [[1, 1]],
            [[1, 1, 1]],
            [[1, 1, 1, 1]],
            [[1, 1, 1, 1, 1]],

            [[1, 1],
             [1, 1]],

            [[1, 1, 1],
             [1, 1, 1]],

            [[1, 1],
             [1, 1],
             [1, 1]],

            [[1, 0],
             [1, 0],
             [1, 1]],

            [[0, 1],
             [0, 1],
             [1, 1]],

            [[1, 0, 0],
             [1, 0, 0],
             [1, 1, 1]],

            [[0, 0, 1],
             [0, 0, 1],
             [1, 1, 1]],

            [[1, 1, 1],
             [0, 1, 0]],

            [[0, 1, 1],
             [1, 1, 0]],

            [[1, 1, 0],
             [0, 1, 1]],

            [[0, 1, 1, 1],
             [1, 1, 1, 0]],

            [[1, 1, 1, 0],
             [0, 1, 1, 1]],

            [[0, 1, 0],
             [1, 1, 1],
             [0, 1, 0]],

            [[1, 0, 1],
             [1, 1, 1]],

            [[1, 1],
             [1, 1],
             [1, 0]],

            [[1, 1, 1],
             [1, 0, 1]],

            [[1, 1, 0],
             [0, 1, 1],
             [0, 0, 1]],

            [[0, 1, 1],
             [1, 1, 0],
             [1, 0, 0]],
        ]

        pool = []

        for shape in base_blocks:
            for rot in cls.generate_rotations(shape):
                pool.append(Block(rot))

        return pool


# -----------------------
# Board
# -----------------------
class Board:

    def __init__(self, size=10):
        self.size = size
        self.grid = np.zeros((size, size), dtype=int)

    def can_place(self, block, row, col):

        h, w = block.shape.shape

        if row + h > self.size:
            return False

        if col + w > self.size:
            return False

        return np.all(
            self.grid[row:row+h, col:col+w] + block.shape <= 1
        )

    def place(self, block, row, col):

        h, w = block.shape.shape

        self.grid[row:row+h, col:col+w] += block.shape

    def clear_lines(self):

        score = 0

        rows = np.where(np.all(self.grid == 1, axis=1))[0]
        cols = np.where(np.all(self.grid == 1, axis=0))[0]

        if len(rows):
            self.grid[rows, :] = 0
            score += len(rows) * 10

        if len(cols):
            self.grid[:, cols] = 0
            score += len(cols) * 10

        return score


# -----------------------
# Game
# -----------------------
class Game:

    BLOCK_POOL = BlockFactory.build_pool()

    def __init__(self):

        self.board = Board()
        self.score = 0
        self.selected = 0

        self.blocks = [
            random.choice(self.BLOCK_POOL)
            for _ in range(3)
        ]

    def place_block(self, row, col):

        block = self.blocks[self.selected]

        if not self.board.can_place(block, row, col):
            return False

        self.board.place(block, row, col)

        self.score += self.board.clear_lines()

        self.blocks[self.selected] = random.choice(
            self.BLOCK_POOL
        )

        return True

    def is_game_over(self):

        for block in self.blocks:

            for r in range(self.board.size):
                for c in range(self.board.size):

                    if self.board.can_place(block, r, c):
                        return False

        return True


# -----------------------
# UI
# -----------------------
class StreamlitUI:

    def __init__(self, game):
        self.game = game

    def get_shadow_cells(self, block, row, col):

        cells = []

        h, w = block.shape.shape

        for i in range(h):
            for j in range(w):

                if block.shape[i, j] == 1:
                    cells.append((row + i, col + j))

        return set(cells)

    def render_board(self, row, col):

        block = self.game.blocks[self.game.selected]

        valid = self.game.board.can_place(
            block,
            row,
            col
        )

        shadow_cells = self.get_shadow_cells(
            block,
            row,
            col
        )

        html = """
        <style>
        .board {
            display:grid;
            grid-template-columns:repeat(10,26px);
            gap:2px;
        }
        .cell{
            width:26px;
            height:26px;
            border-radius:4px;
        }
        .empty{background:#2b2b2b;}
        .filled{background:#4fc3f7;}
        .shadow_ok{background:#ff6b6b;opacity:.4;}
        .shadow_bad{background:#b00020;opacity:.4;}
        </style>

        <div class="board">
        """

        for r in range(10):
            for c in range(10):

                if self.game.board.grid[r, c] == 1:
                    cls = "filled"

                elif (r, c) in shadow_cells:
                    cls = "shadow_ok" if valid else "shadow_bad"

                else:
                    cls = "empty"

                html += f'<div class="cell {cls}"></div>'

        html += "</div>"

        st.markdown(html, unsafe_allow_html=True)


# -----------------------
# Session State
# -----------------------
if "game" not in st.session_state:
    st.session_state.game = Game()

game = st.session_state.game
ui = StreamlitUI(game)

# -----------------------
# Header
# -----------------------
st.title("🧩 Block Blast OOP Edition")
st.write(f"⭐ Score : {game.score}")

# -----------------------
# Block Select
# -----------------------
cols = st.columns(3)

for i in range(3):

    with cols[i]:

        st.write(f"Block {i}")

        st.markdown(
            game.blocks[i].render(),
            unsafe_allow_html=True
        )

        if st.button(f"Select {i}"):
            game.selected = i
            st.rerun()

# -----------------------
# Placement
# -----------------------
st.subheader("🎯 Placement Preview")

row = st.selectbox("Row", range(10))
col = st.selectbox("Col", range(10))

ui.render_board(row, col)

# -----------------------
# Place Button
# -----------------------
if st.button("🟢 PLACE BLOCK"):

    if game.place_block(row, col):
        st.rerun()
    else:
        st.warning("❌ Cannot place block here")

# -----------------------
# Game Over
# -----------------------
if game.is_game_over():

    st.error("💀 GAME OVER")

    if st.button("Restart"):
        st.session_state.game = Game()
        st.rerun()