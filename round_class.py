MAX_WIN = 250000
class block:
    def __init__(self, ID, block_type="empty", block_value=0):
        self.ID = ID
        self.block_type = block_type
        self.block_value = block_value
    def get_value(self):
        if self.block_type == "coin" or self.block_value == "special_coin":
            return self.block_value
        return 0
    def multiply(self, multiplier):
        if self.block_type == "coin" or self.block_value == "special_coin":
            self.block_value *= multiplier
    def erase(self):
        self.block_type = "empty"
        self.block_value = 0
    def get_string(self):
        if self.block_type == "empty":
            return ""
        if self.block_type == "coin":
            return f"{self.block_value:,}"
        if self.block_type == "special_coin":
            return f"[{self.block_value:,}]"
        if self.block_type == "multiplier":
            return f"x{self.block_value}"
        if self.block_type == "collect":
            return f"[ C ]"


class board_state:
    def __init__(self, math_model, seed, copy_from_board=None, event="spin"):
        # if copy_from_board is not None, deep copy it
        self.math_model = math_model
        self.seed = seed
        self.board = [block] * 25
        if copy_from_board is not None:
            self.board = copy.deepcopy(copy_from_board.board)
    def is_finished_state(self):
        # if the sum of all block's value is no less than than MAX_WIN, return True
        sum = 0
        for block in self.board:
            sum += block.get_value()
        if sum >= MAX_WIN:
            return True
        # if every block is either coin or special_coin, return True
        for block in self.board:
            if block.block_type != "coin" and block.block_type != "special_coin":
                return False
        return True
    def next_step(self):

        if self.is_finished_state():
            return "already_finished_state"
        # 1. 如果存在type为multiplier的block, 则对于每个block, 调用其multiply方法, 参数为type为multiplier的block的value. 然后对于type为multiplier的block, 调用erase方法
        flag_event = False
        for block in self.board:
            if block.block_type == "multiplier":
                for block2 in self.board:
                    block2.multiply(block.block_value)
                block.erase()
                flag_event = True
        if flag_event:
            return "activated_multiplier"
        # 2. 如果存在type为collect的block, 则对于每个type为coin或special_coin的block,
        # 将其value加到这个(type为collect的block)上, 然后将自己的type从collect转为special_coin, 并对于每个其他不是special_coin的block, 调用erase方法.
        for block in self.board:
            if block.block_type == "collect":
                for block2 in self.board:
                    if block2.block_type == "coin" or block2.block_type == "special_coin":
                        block.block_value += block2.block_value
                        if block2.block_type != "special_coin":
                            block2.erase()
                block.block_type = "special_coin"
                flag_event = True
        if flag_event:
            return "activated_collect"
        # 3. 如果仍有至少1个空格(type为empty)的block, 调用spin方法, 参数为self.math_model
        for block in self.board:
            if block.block_type == "empty":
                self.spin(self.math_model, self.seed)
                return "activated_spin"

        return "ERROR: nothing happened"

    def spin(self, math_model, seed):
        return 0

class round:
    def __init__(self, math_model=1, assigned_seed=-1):
        self.math_model = math_model
        self.seed = assigned_seed
        if assigned_seed < 0:
            self.seed = random.randint(0, 10000)
        self.current_board = board_state(self.math_model, self.seed)
        self.board_history = []
    def get_latest_board(self):
        return self.board_history[-1]

