from copy import copy
from Model import ModelState
import argparse


def create_args_parser():
    parser = argparse.ArgumentParser(
        description='System simulator'
    )
    required_args = parser.add_argument_group('required named arguments')
    required_args.add_argument('--t', type=int, help='Count tacts before source gives new request', required=True)
    required_args.add_argument('--c', type=int, help='Queue size', required=True)
    required_args.add_argument('--p1', type=float, help='Probability that request will not be processed by first channel', required=True)
    required_args.add_argument('--p2', type=float, help='Probability that request will not be processed by second channel', required=True)
    required_args.add_argument('--n', type=int, help='Count tacts to simulate', required=True)
    return parser


class ModelState15(ModelState):

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
        if isinstance(other, ModelState15):
            return self.count_tacts_before_new_request == other.count_tacts_before_new_request and\
                   self.queue_size == other.queue_size and\
                   self.first_channel_is_busy == other.first_channel_is_busy and\
                   self.second_channel_is_busy == other.second_channel_is_busy
        return NotImplemented

    def to_string(self):
        return str(self.count_tacts_before_new_request) +\
               str(self.queue_size) +\
               ('1' if self.first_channel_is_busy else '0') +\
               ('1' if self.second_channel_is_busy else '0')


start_state = ModelState15('2000')


def get_next_state(state, params, first_channel_should_change_state, second_channel_should_change_state):
    source_generated_request = \
        ((state.count_tacts_before_new_request - 1) == 0)

    next_state = copy(state)

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
                ##First channel is busy, so go to queue
                next_state.queue_size += 1
            else:
                ##First channel not busy, so go make it busy
                next_state.first_channel_is_busy = True
            next_state.count_tacts_before_new_request = params.t
        else:
            if (next_state.queue_size < params.c):
                ##Some queue exists, but queue is not full, so we queue new request
                next_state.queue_size += 1
                next_state.count_tacts_before_new_request = params.t
            else:
                ##Source blocked
                pass
    else:
        next_state.count_tacts_before_new_request -= 1

    return next_state
