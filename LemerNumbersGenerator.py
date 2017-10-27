class LemerNumbersGenerator:

    def __init__(self, r0=0, a=0, m=0):
        self.__r0 = r0
        self.__a = a
        self.__m = m

        self.__seed = self.__r0

    def reset(self):
        self.__seed = self.__r0

    def set_generator_parameters(self, r0, a, m):
        self.__r0 = r0
        self.__a = a
        self.__m = m

    def next_number(self):
        self.__seed = (self.__seed * self.__a) % self.__m
        return self.__seed / self.__m


edGenerator = LemerNumbersGenerator(1, 16807, 2 ** 32 - 1)
