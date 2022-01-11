from microbenchmarks._utils import add_result, get_ti_arch, make_result_dict

import taichi as ti


class BenchmarkItem:
    def __init__(self):
        self._name = 'item'
        self._items = {}
        # {tag: {impl: xxx, ...}}

    def get(self):
        return self._items

    def get_tags(self):
        return [tag for tag in self._items]

    def items(self):
        return self._items.items()


class BenchmarkPlan:
    def __init__(self):
        self.name = 'plan'
        self.info = {}
        self.plan = {}

    def get_info(self):
        return self.info

    def get_plan(self):
        return self.plan


class BenchamrkTemplate:
    name = 'template'

    def __init__(self, arch):
        self.arch = arch
        self.plan = BenchmarkPlan()
        self.results = {}

    def run(self):
        print(self.name)
        paln_dict = self.plan.get_plan()

        for plan_name, plan_dict, in paln_dict.items():
            tag_list = plan_dict['tags']
            print(f'{tag_list}')
            result_dict = make_result_dict(tag_list)
            ti.init(kernel_profiler=True, arch=get_ti_arch(self.arch))
            for result_tag in plan_dict['results']:
                _ms = plan_dict['func'](result_tag, *plan_dict['args'])
                if _ms is not None:
                    print(f'    {result_tag}={_ms}')
                    add_result(result_dict, result_tag, _ms)
            if len(result_dict['results']) > 0:
                self.results[plan_name] = result_dict
            ti.reset()

        rdict = {'results': self.results, 'info': self.plan.get_info()}
        return rdict
