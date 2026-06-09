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

        # 블록 자체 점수
        self.score += int(np.sum(block.shape))

        # 줄 삭제 점수
        self.score += self.board.clear_lines()

        # 사용한 블록 제거
        self.blocks[self.selected] = None

        # 3개 모두 사용하면 새로 지급
        if all(b is None for b in self.blocks):
            self.blocks = [
                random.choice(self.BLOCK_POOL)
                for _ in range(3)
            ]

        # 선택된 블록이 없어졌다면 남은 블록 선택
        if self.blocks[self.selected] is None:

            for idx, b in enumerate(self.blocks):
                if b is not None:
                    self.selected = idx
                    break

        return True

    def is_game_over(self):

        for block in self.blocks:

            if block is None:
                continue

            h, w = block.shape.shape

            for r in range(
                self.board.size - h + 1
            ):
                for c in range(
                    self.board.size - w + 1
                ):

                    if self.board.can_place(
                        block,
                        r,
                        c
                    ):
                        return False

        return True


# -----------------------
# UI
# -----------------------
class StreamlitUI:

    def __init__(self, game):
        self.game = game

    def get_shadow_map(self, block, row, col):

        shadow_map = {}

        h, w = block.shape.shape

        for i in range(h):
            for j in range(w):

                if block.shape[i, j] == 0:
                    continue

                x = row + i
                y = col + j

                # 보드 밖
                if (
                    x >= self.game.board.size
                    or y >= self.game.board.size
                ):
                    shadow_map[(x, y)] = "bad"

                # 기존 블록과 충돌
                elif self.game.board.grid[x, y] == 1:
                    shadow_map[(x, y)] = "overlap"

                # 정상 배치
                else:
                    shadow_map[(x, y)] = "ok"

        return shadow_map

    def render_board(self, row, col):

        block = self.game.blocks[self.game.selected]

        shadow_map = self.get_shadow_map(
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

        .empty{
            background:#2b2b2b;
        }

        .filled{
            background:#4fc3f7;
        }

        /* 정상 배치 가능 */
        .shadow_ok{
            background:#66bb6a;
            opacity:.7;
        }

        /* 기존 블록과 충돌 */
        .shadow_overlap{
            background:#ffa726;
            opacity:.9;
        }

        /* 보드 밖 또는 불가능 */
        .shadow_bad{
            background:#e53935;
            opacity:.9;
        }
        </style>

        <div class="board">
        """

        for r in range(10):
            for c in range(10):

                occupied = self.game.board.grid[r, c] == 1

                if (r, c) in shadow_map:

                    state = shadow_map[(r, c)]

                    if state == "ok":
                        cls = "shadow_ok"

                    elif state == "overlap":
                        cls = "shadow_overlap"

                    else:
                        cls = "shadow_bad"

                else:

                    cls = (
                        "filled"
                        if occupied
                        else "empty"
                    )

                html += f'<div class="cell {cls}"></div>'

        html += "</div>"

        st.markdown(html, unsafe_allow_html=True)


# -----------------------
# Session State
# -----------------------
if "game" not in st.session_state:
    st.session_state.game = Game()

game = st.session_state.game
if "preview_row" not in st.session_state:
    st.session_state.preview_row = 0

if "preview_col" not in st.session_state:
    st.session_state.preview_col = 0
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

        if game.blocks[i] is None:

            st.markdown("✅ 사용 완료")

        else:

            st.markdown(
                game.blocks[i].render(),
                unsafe_allow_html=True
            )

        if game.blocks[i] is not None:

            if st.button(f"Select {i}"):

                game.selected = i

                st.session_state.preview_row = 0
                st.session_state.preview_col = 0

                st.rerun()

# -----------------------
# Placement
# -----------------------
st.subheader("🎯 Placement Preview")

selected_block = game.blocks[game.selected]

if selected_block is not None:

    h, w = selected_block.shape.shape

    row_options = list(
        range(
            game.board.size - h + 1
        )
    )

    col_options = list(
        range(
            game.board.size - w + 1
        )
    )

    row = st.selectbox(
        "Row",
        row_options,
        key="preview_row"
    )

    col = st.selectbox(
        "Col",
        col_options,
        key="preview_col"
    )

    ui.render_board(row, col)

else:

    st.info("블록을 선택하세요")

# -----------------------
# Place Button
# -----------------------
if selected_block is not None:

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