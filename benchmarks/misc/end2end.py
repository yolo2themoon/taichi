import os
import time

from end2end_cases import end2end_cases_list

from utils import dump2json

import taichi as ti


class EndToEnd:
    suite_name = 'end2end'
    supported_archs = [ti.x64, ti.cuda]
    test_cases = end2end_cases_list

    def __init__(self, arch):
        self._arch = arch
        self._resualts = {}

    def run(self):
        for case in self.test_cases:
            print(case.__name__)
            self._resualts[case.__name__] = case(self._arch)


if __name__ == '__main__':
    impl = EndToEnd(ti.cuda)
    impl.run()
    print(dump2json(impl._resualts))
