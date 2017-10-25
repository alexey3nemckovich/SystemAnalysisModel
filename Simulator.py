import sys
from random import random
from Model import ModelTransition
from AttribtutedObject import AttributedObject
##option specific
from option33 import get_next_state
from option33 import start_state


def simulate(simulation_params):
    res = AttributedObject()

    state = start_state

    print(start_state.to_string())

    for i in range(simulation_params.n):
        first_channel_should_change_state = random() <= simulation_params.p1
        second_channel_should_change_state = random() <= simulation_params.p2

        state = get_next_state(state, first_channel_should_change_state, second_channel_should_change_state, 2, simulation_params.c)
        print(state.to_string())

    return res


def find_all_transitions(state, params, transitions, all_states):
    next_states = set()

    if state.first_channel_is_busy and state.second_channel_is_busy:
        ff = get_next_state(state, params, False, False)
        ft = get_next_state(state, params, False, True)
        tf = get_next_state(state, params, True, False)
        tt = get_next_state(state, params, True, True)

        transitions.append(ModelTransition(state, ff, "p1 * p2"))
        transitions.append(ModelTransition(state, ft, "p1 * (1 - p2)"))
        transitions.append(ModelTransition(state, tf, "(1 - p1) * p2"))
        transitions.append(ModelTransition(state, tt, "(1 - p1) * (1 - p2)"))

        next_states = {ff, ft, tf, tt}
    else:
        if state.first_channel_is_busy:
            ff = get_next_state(state, params, False, False)
            tf = get_next_state(state, params, True, False)

            transitions.append(ModelTransition(state, ff, "p1"))
            transitions.append(ModelTransition(state, tf, "1 - p1"))

            next_states = {ff, tf}
        else:
            if state.second_channel_is_busy:
                ff = get_next_state(state, params, False, False)
                ft = get_next_state(state, params, False, True)

                transitions.append(ModelTransition(state, ff, "p2"))
                transitions.append(ModelTransition(state, ft, "1 - p2"))

                next_states = {ff, ft}
            else:
                ff = get_next_state(state, params, False, False)

                transitions.append(ModelTransition(state, ff, "1"))

                next_states = {ff}

    new_states = next_states - all_states

    for new_state in new_states:
        all_states.add(new_state)

    for new_state in new_states:
        find_all_transitions(new_state, params, transitions, all_states)


def build_model_graph(simulation_params):
    res = AttributedObject()

    transitions = []
    all_states = {start_state}
    find_all_transitions(start_state, simulation_params, transitions, all_states)

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
