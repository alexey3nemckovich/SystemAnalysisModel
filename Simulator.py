import sys
import copy
from AttribtutedObject import AttributedObject
from random import random


class ModelState:
    def __init__(self, state_code):
        self.count_tacts_before_new_request = int(state_code[0])
        self.queue_size = int(state_code[1])
        self.first_channel_is_busy = True if state_code[2] == '1' else False
        self.second_channel_is_busy = True if state_code[3] == '1' else False

    def __hash__(self):
        return hash(
            self.count_tacts_before_new_request +
            self.queue_size +
            self.first_channel_is_busy +
            self.second_channel_is_busy
        )

    def __eq__(self, other):
        if isinstance(other, ModelState):
            return self.count_tacts_before_new_request == other.count_tacts_before_new_request and\
                   self.queue_size == other.queue_size and\
                   self.first_channel_is_busy == other.first_channel_is_busy and\
                   self.second_channel_is_busy == other.second_channel_is_busy
        return NotImplemented

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    def __str__(self):
        return self.to_string()

    def to_string(self):
        return str(self.count_tacts_before_new_request) + str(self.queue_size) + ('1' if self.first_channel_is_busy else '0') + ('1' if self.second_channel_is_busy else '0')


class ModelTransition:
    def __init__(self, curr_state, next_state, description):
        self.curr_state = curr_state
        self.next_state = next_state
        self.description = description

    def to_string(self):
        return self.curr_state.to_string() + "->" + self.next_state.to_string() + " with probability = " + self.description


def get_next_state(state, first_channel_should_change_state, second_channel_should_change_state, queue_size, count_tacts_before_new_request):
    source_generated_request = \
        ((state.count_tacts_before_new_request - 1) == 0)

    next_state = copy.copy(state)

    if next_state.second_channel_is_busy and second_channel_should_change_state:
        ##Some request was finally processed by second(last) channel
        next_state.second_channel_is_busy = False

    if next_state.first_channel_is_busy and first_channel_should_change_state:
        next_state.first_channel_is_busy = False
        if not next_state.second_channel_is_busy:
            next_state.second_channel_is_busy = True
        else:
            ##Some request was rejected by second channel
            pass

    if next_state.queue_size > 0:
        if not next_state.first_channel_is_busy:
            ##Took request from queue to first channel
            next_state.first_channel_is_busy = True
            next_state.queue_size -= 1

    if source_generated_request:
        if (next_state.queue_size == 0):
            ##Empty queue
            if next_state.first_channel_is_busy:
                ##First channel not busy, so go make it busy
                next_state.queue_size += 1
            else:
                ##First channel is busy, so go to queue
                next_state.first_channel_is_busy = True
            next_state.count_tacts_before_new_request = count_tacts_before_new_request
        else:
            if (next_state.queue_size < queue_size):
                ##Some queue exists, but queue is not full, so we queue new request
                next_state.queue_size += 1
                next_state.count_tacts_before_new_request = count_tacts_before_new_request
            else:
                ##Source blocked
                pass
    else:
        next_state.count_tacts_before_new_request -= 1

    return next_state


def simulate(simulation_params):
    res = AttributedObject()

    start_state = ModelState('2000')
    state = start_state

    print(start_state.to_string())

    for i in range(simulation_params.n):
        first_channel_should_change_state = random() <= simulation_params.p1
        second_channel_should_change_state = random() <= simulation_params.p2

        state = get_next_state(state, first_channel_should_change_state, second_channel_should_change_state, 2, simulation_params.c)
        print(state.to_string())

    return res


def find_all_transitions(state, queue_size, count_tacts_before_new_request, p1, p2, transitions, all_states):
    next_states = set()

    if state.first_channel_is_busy and state.second_channel_is_busy:
        ff = get_next_state(state, False, False, queue_size, count_tacts_before_new_request)
        ft = get_next_state(state, False, True, queue_size, count_tacts_before_new_request)
        tf = get_next_state(state, True, False, queue_size, count_tacts_before_new_request)
        tt = get_next_state(state, True, True, queue_size, count_tacts_before_new_request)

        transitions.append(ModelTransition(state, ff, "p1 * p2"))
        transitions.append(ModelTransition(state, ft, "p1 * (1 - p2)"))
        transitions.append(ModelTransition(state, tf, "(1 - p1) * p2"))
        transitions.append(ModelTransition(state, tt,"(1 - p1) * (1 - p2)"))

        next_states = {ff, ft, tf, tt}
    else:
        if state.first_channel_is_busy:
            ff = get_next_state(state, False, False, queue_size, count_tacts_before_new_request)
            tf = get_next_state(state, True, False, queue_size, count_tacts_before_new_request)

            transitions.append(ModelTransition(state, ff, "p1"))
            transitions.append(ModelTransition(state, tf, "1 - p1"))

            next_states = {ff, tf}
        else:
            if state.second_channel_is_busy:
                ff = get_next_state(state, False, False, queue_size, count_tacts_before_new_request)
                ft = get_next_state(state, False, True, queue_size, count_tacts_before_new_request)

                transitions.append(ModelTransition(state, ff, "p2"))
                transitions.append(ModelTransition(state, ft, "1 - p2"))

                next_states = {ff, ft}
            else:
                ff = get_next_state(state, False, False, queue_size, count_tacts_before_new_request)

                transitions.append(ModelTransition(state, ff, "1"))

                next_states = {ff}

    new_states = next_states - all_states

    for new_state in new_states:
        all_states.add(new_state)

    for new_state in new_states:
        find_all_transitions(new_state, 2, count_tacts_before_new_request, p1, p2, transitions, all_states)


def build_model_graph(simulation_params):
    res = AttributedObject()

    start_state = ModelState('2000')

    transitions = []
    all_states = {start_state}
    find_all_transitions(start_state, 2, simulation_params.c, simulation_params.p1, simulation_params.p2, transitions, all_states)

    print("Graph")
    for state in all_states:
        print("State = " + state.to_string())
        for transition in transitions:
            if state == transition.curr_state:
                print(transition.to_string())
        print("-------------------------------------------------------------------------------------------------------------")

    print("|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||")

    print("Equation system")
    for state in all_states:
        print("State = " + state.to_string())
        sys.stdout.write("Probability = ")

        count = 0
        for transition in transitions:
            if state == transition.next_state:
                if "*" in transition.description:
                    str = "P" + transition.curr_state.to_string() + " * " + transition.description
                else:
                    str = "P" + transition.curr_state.to_string() + " * (" + transition.description + ")"

                if count == 0:
                    sys.stdout.write(str)
                else:
                    sys.stdout.write(" + " + str)

                count += 1

        if count == 0:
            sys.stdout.write('0')

        sys.stdout.write('\n\r')
        sys.stdout.flush()

        print("-------------------------------------------------------------------------------------------------------------")
