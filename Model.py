class ModelState:
    def __hash__(self):
        return NotImplemented

    def __eq__(self, other):
        return NotImplemented

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    def __str__(self):
        return self.to_string()

    def to_string(self):
        raise NotImplementedError()


class ModelTransition:
    def __init__(self, curr_state, next_state, description):
        self.curr_state = curr_state
        self.next_state = next_state
        self.description = description

    def to_string(self):
        return self.curr_state.to_string() + "->" + self.next_state.to_string() + " with probability = " + self.description
