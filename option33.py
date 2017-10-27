from copy import copy
from Model import ModelState
import argparse
import Model


def create_args_parser():
    parser = argparse.ArgumentParser(
        description='System simulator'
    )
    required_args = parser.add_argument_group('required named arguments')
    required_args.add_argument('--t', type=int, help='Count tacts before source gives new request', required=True)
    required_args.add_argument('--c1', type=int, help='First queue size', required=True)
    required_args.add_argument('--c2', type=int, help='Second queue size', required=True)
    required_args.add_argument('--p1', type=float, help='Probability that request will not be processed by first channel', required=True)
    required_args.add_argument('--p2', type=float, help='Probability that request will not be processed by second channel', required=True)
    required_args.add_argument('--n', type=int, help='Count tacts to simulate', required=True)
    return parser


class ModelState33(ModelState):

    def __init__(self, state_code):
        self.count_tacts_before_new_request = int(state_code[0])
        self.first_queue_size = int(state_code[1])
        self.first_channel_is_busy = True if state_code[2] == '1' else False
        self.second_queue_size = int(state_code[3])
        self.second_channel_is_busy = True if state_code[4] == '1' else False

    def __hash__(self):
        return hash(
            self.count_tacts_before_new_request +
            self.first_queue_size +
            self.first_channel_is_busy +
            self.second_queue_size +
            self.second_channel_is_busy
        )

    def __eq__(self, other):
        if isinstance(other, ModelState33):
            return self.count_tacts_before_new_request == other.count_tacts_before_new_request and\
                   self.first_queue_size == other.first_queue_size and\
                   self.first_channel_is_busy == other.first_channel_is_busy and\
                   self.second_queue_size == other.second_queue_size and\
                   self.second_channel_is_busy == other.second_channel_is_busy
        return NotImplemented

    def to_string(self):
        return str(self.count_tacts_before_new_request) +\
               str(self.first_queue_size) +\
               ('1' if self.first_channel_is_busy else '0') +\
               str(self.second_queue_size) +\
               ('1' if self.second_channel_is_busy else '0')


start_state = ModelState33('20000')


def get_next_state(state, params, first_channel_should_change_state, second_channel_should_change_state):
    source_generated_request = \
        ((state.count_tacts_before_new_request - 1) == 0)

    next_state = copy(state)

    if next_state.second_channel_is_busy and second_channel_should_change_state:
        ##Some request was finally processed by second(last) channel
        next_state.second_channel_is_busy = False

    if next_state.second_queue_size > 0:
        if not next_state.second_channel_is_busy:
            ##Took request from second queue to second channel
            next_state.second_channel_is_busy = True
            next_state.second_queue_size -= 1

    if next_state.first_channel_is_busy and first_channel_should_change_state:
        ##First channel processed request
        next_state.first_channel_is_busy = False
        if not next_state.second_channel_is_busy:
            ##Second channel is free, so make it busy
            next_state.second_channel_is_busy = True
        else:
            if next_state.second_queue_size < params.c2:
                ##Put request to second queue
                next_state.second_queue_size += 1
            else:
                ##Request is going out from first channel
                pass

    if next_state.first_queue_size > 0:
        if not next_state.first_channel_is_busy:
            ##Took request from queue to first channel
            next_state.first_channel_is_busy = True
            next_state.first_queue_size -= 1

    if source_generated_request:
        if not next_state.first_channel_is_busy:
            ##New request is going to free first channel
            next_state.first_channel_is_busy = True
        else:
            if next_state.first_queue_size < params.c1:
                ##New request is queued
                next_state.first_queue_size += 1
            else:
                ##Request is going out
                pass
        next_state.count_tacts_before_new_request = params.t
    else:
        next_state.count_tacts_before_new_request -= 1

    return next_state


def get_next_state_with_statistics(state, params, first_channel_should_change_state, second_channel_should_change_state, statistics):
    source_generated_request = \
        ((state.count_tacts_before_new_request - 1) == 0)

    if source_generated_request:
        statistics.total_count_requests += 1

    next_state = copy(state)

    if next_state.second_channel_is_busy and second_channel_should_change_state:
        ##Some request was finally processed by second(last) channel
        next_state.second_channel_is_busy = False

        statistics.total_count_processed_requests += 1

    if next_state.second_queue_size > 0:
        if not next_state.second_channel_is_busy:
            ##Took request from second queue to second channel
            next_state.second_channel_is_busy = True
            next_state.second_queue_size -= 1

    if next_state.first_channel_is_busy and first_channel_should_change_state:
        ##First channel processed request
        next_state.first_channel_is_busy = False
        if not next_state.second_channel_is_busy:
            ##Second channel is free, so make it busy
            next_state.second_channel_is_busy = True
        else:
            if next_state.second_queue_size < params.c2:
                ##Put request to second queue
                next_state.second_queue_size += 1
            else:
                ##Request is going out from first channel
                statistics.total_count_rejected_requests += 1

    if next_state.first_queue_size > 0:
        if not next_state.first_channel_is_busy:
            ##Took request from queue to first channel
            next_state.first_channel_is_busy = True
            next_state.first_queue_size -= 1

    if source_generated_request:
        if not next_state.first_channel_is_busy:
            ##New request is going to free first channel
            next_state.first_channel_is_busy = True
        else:
            if next_state.first_queue_size < params.c1:
                ##New request is queued
                next_state.first_queue_size += 1
            else:
                ##Request is going out
                statistics.total_count_rejected_requests += 1

        next_state.count_tacts_before_new_request = params.t
    else:
        next_state.count_tacts_before_new_request -= 1

    ##system size
    system_size = 0

    if next_state.first_channel_is_busy:
        system_size += 1

    if next_state.second_channel_is_busy:
        system_size += 1

    system_size += next_state.first_queue_size
    system_size += next_state.second_queue_size

    statistics.system_size_list.append(system_size)

    return next_state


get_next_state_with_statistics.first_channel_time = 0
get_next_state_with_statistics.second_channel_time = 0


class ModelSimulationStatistics(Model.ModelSimulationStatistics):

    def __init__(self, p1, p2):
        Model.ModelSimulationStatistics.__init__(self, p1, p2)

        self.average_p1 = 1 / (1 - self.__p1)
        self.average_p2 = 1 / (1 - self.__p2)

        self.system_size_list = []

        self.total_count_requests = 0
        self.total_count_rejected_requests = 0
        self.total_count_processed_requests = 0

        self.average_throughput = 0
        self.average_relative_throughput = 0

        self.average_system_size = 0
        self.average_system_time = 0

    def __str__(self):
        return "Q = " + str(self.average_relative_throughput) + "\n\r" + \
               "Wc = " + str(self.average_system_time) + "\n\r" +\
               "A = " + str(self.average_throughput) + "\n\r"

    def calculate(self, tacts_count):
        self.average_relative_throughput = \
            1 - (self.total_count_rejected_requests / tacts_count)

        self.average_throughput = self.total_count_processed_requests / tacts_count

        self.average_system_size = sum(self.system_size_list) / len(self.system_size_list)
        self.average_system_time = self.average_system_size / self.average_throughput
