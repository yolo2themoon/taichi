import itertools

from microbenchmarks._metric import MetricType
from microbenchmarks._utils import get_ti_arch, tags2name

import taichi as ti


class BenchmarkPlan:
    def __init__(self, name='plan', arch='x64', basic_repeat_times=1):
        self.name = name
        self.arch = arch
        self.basic_repeat_times = basic_repeat_times
        self.info = {'name': self.name}
        self.plan = {}  # {'tags': [...], 'result': None}
        self.items = []
        self.func_lut = None

    def create_plan(self, *items):
        self.items = list(items)
        items_list = [[self.name]]
        for item in self.items:
            items_list.append(item.get_tags())
            self.info[item.name] = item.get_tags()
        case_list = list(itertools.product(*items_list))  #items generate cases
        for tags in case_list:
            self.plan[tags2name(tags)] = {'tags': tags, 'result': None}

    def set_func(self, func_lut):
        self.func_lut = func_lut

    def run(self):
        for case, plan in self.plan.items():
            tag_list = plan['tags']
            self._init_taichi(self.arch, tag_list)
            _ms = self._run_func(tag_list)
            plan['result'] = _ms
            print(f'{tag_list}={_ms}')
            ti.reset()
        rdict = {'results': self.plan, 'info': self.info}
        return rdict

    def _get_kwargs(self, tags):
        kwargs = {}
        tags = tags[1:]  # tags = [case_name, item1_tag, item2_tag, ...]
        for item, tag in zip(self.items, tags):
            kwargs[item.name] = item.impl(tag)
        return kwargs

    def _init_taichi(self, arch, tags):
        for tag in tags:
            if MetricType.init_taichi(arch, tag):
                return True
        return False

    def _run_func(self, tags: list):
        for tag in tags:
            if tag in self.func_lut:
                return self.func_lut[tag](self.arch, self.basic_repeat_times,
                                          **self._get_kwargs(tags))
        return None
