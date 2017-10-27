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

    if source_generated_request or next_state.count_tacts_before_new_request == 0:
        if (next_state.queue_size == 0):
            ##Empty queue
            if not next_state.first_channel_is_busy:
                ##First channel not busy, so go make it busy
                next_state.first_channel_is_busy = True
            else:
                ##First channel is busy, so go to queue
                next_state.queue_size += 1
            next_state.count_tacts_before_new_request = params.t
        else:
            if (next_state.queue_size < params.c):
                ##Some queue exists, but queue is not full, so we queue new request
                next_state.queue_size += 1
                next_state.count_tacts_before_new_request = params.t
            else:
                ##Source blocked
                next_state.count_tacts_before_new_request = 0
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

    if source_generated_request or next_state.count_tacts_before_new_request == 0:
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
                next_state.count_tacts_before_new_request = 0
    else:
        next_state.count_tacts_before_new_request -= 1

    statistics.total_queue_len += next_state.queue_size

    ##system size
    system_size = 0

    if next_state.first_channel_is_busy:
        system_size += 1

    if next_state.second_channel_is_busy:
        system_size += 1

    system_size += next_state.queue_size
    statistics.system_size_list.append(system_size)

    return next_state


class ModelSimulationStatistics(Model.ModelSimulationStatistics):

    def __init__(self, p1, p2):
        Model.ModelSimulationStatistics.__init__(self, p1, p2)

        self.average_p1 = 1 / (1 - self.__p1)
        self.average_p2 = 1 / (1 - self.__p2)

        self.system_size_list = []

        self.total_queue_len = 0
        self.total_count_requests = 0
        self.total_count_processed_requests = 0

        self.average_queue_len = 0
        self.average_throughput = 0

        self.average_system_size = 0
        self.average_system_time = 0

    def __str__(self):
        return "Lqueue = " + str(self.average_queue_len) + "\n\r" +\
               "A = " + str(self.average_throughput) + "\n\r" + \
               "Wc = " + str(self.average_system_time)

    def calculate(self, tacts_count):
        self.average_queue_len = self.total_queue_len / tacts_count

        self.average_throughput = self.total_count_processed_requests / tacts_count

        self.average_system_size = sum(self.system_size_list) / len(self.system_size_list)
        self.average_system_time = self.average_system_size / self.average_throughput
