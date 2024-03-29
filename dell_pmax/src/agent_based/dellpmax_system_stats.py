#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
# +------------------------------------------------------------+
# |                                                            |
# |             | |             | |            | |             |
# |          ___| |__   ___  ___| | ___ __ ___ | | __          |
# |         / __| '_ \ / _ \/ __| |/ / '_ ` _ \| |/ /          |
# |        | (__| | | |  __/ (__|   <| | | | | |   <           |
# |         \___|_| |_|\___|\___|_|\_\_| |_| |_|_|\_\          |
# |                                   custom code by Nagarro   |
# |                                                            |
# +------------------------------------------------------------+
#
# Copyright (C)  2022  DevOps InfrastructureServices@nagarro-es.com
# for Nagarro ES GmbH

from .agent_based_api.v1 import (
    register,
    Result,
    Service,
    State,
    get_value_store,
)
from .utils import memory
from .utils.cpu_util import check_cpu_util

import time

"""
Example output:
<<<dellpmax_systemstats:sep(124)>>>
systemStatistics|1073741824|4260102144|3627622616|0.5366449|12533428224|11737571328

name|heap|heap.max|heap.used|cpu.usage|mem.total|mem.used
"""


# HEAP

def discover_dellpmax_systemstats_heap(section):
    yield Service()


def check_dellpmax_systemstats_heap(params, section):
    if section:
        heap_max = int(section[0][2])
        heap_used = int(section[0][3])
        yield from memory.check_element("Heap", heap_used, heap_max, params.get("levels"))
    else:
        yield Result(state=State.CRIT, summary="No heap data available")


register.check_plugin(
    name="dellpmax_systemstats_heap",
    sections=["dellpmax_systemstats"],
    service_name="Heap",
    discovery_function=discover_dellpmax_systemstats_heap,
    check_function=check_dellpmax_systemstats_heap,
    check_ruleset_name="memory_simple",
    check_default_parameters={
        "levels": ("perc_used", (80.0, 90.0)),
    },
)


# CPU

def discover_dellpmax_systemstats_cpu(section):
    yield Service()


def check_dellpmax_systemstats_cpu(params, section):
    if section:
        cpu_util = float(section[0][4])
        yield from check_cpu_util(
                util=cpu_util,
                params=params,
                value_store=get_value_store(),
                this_time=time.time()
            )
    else:
        yield Result(state=State.CRIT, summary="No cpu data available")


register.check_plugin(
    name="dellpmax_systemstats_cpu",
    sections=["dellpmax_systemstats"],
    service_name="CPU",
    discovery_function=discover_dellpmax_systemstats_cpu,
    check_function=check_dellpmax_systemstats_cpu,
    check_ruleset_name="cpu_utilization",
    check_default_parameters={
        "util": (80.0, 90.0),
    }
)


# MEMORY

def discover_dellpmax_systemstats_memory(section):
    yield Service()


def check_dellpmax_systemstats_mem(params, section):
    if section:
        mem_max = int(section[0][5])
        mem_used = int(section[0][6])
        yield from memory.check_element("Memory", mem_used, mem_max, params.get("levels"))
    else:
        yield Result(state=State.CRIT, summary="No memory data available")


register.check_plugin(
    name="dellpmax_systemstats_mem",
    sections=["dellpmax_systemstats"],
    service_name="Memory",
    discovery_function=discover_dellpmax_systemstats_memory,
    check_function=check_dellpmax_systemstats_mem,
    check_ruleset_name="memory_simple",
    check_default_parameters={
        "levels": ("perc_used", (80.0, 90.0)),
    },
)
