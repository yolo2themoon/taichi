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
        self._results = {}

    def run(self):
        for case in self.test_cases:
            print(case.__name__)
            self._results[case.__name__] = case(self._arch)

    def save_as_json(self, arch_dir='./'):
        #folder of suite
        suite_path = os.path.join(arch_dir, self.suite_name)
        os.makedirs(suite_path)
        #all cases in a json file
        results_path = os.path.join(suite_path, f'{self.suite_name}.json')
        with open(results_path, 'w') as f:
            print(dump2json(self._results), file=f)
    
    def save_as_markdown(self, arch_dir='./'):
        return #no need now


if __name__ == '__main__':
    impl = EndToEnd(ti.cuda)
    impl.run()
    print(dump2json(impl._results))
