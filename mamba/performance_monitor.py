import os.path
import time
from functools import wraps
from newrelic import agent
from twisted.internet import defer
from logging import Logger

class PerformanceMonitor(object):
    def __init__(self, config=None):
        self.custom_logger = None
        if config:
            self.config(config)

    def config(self, config):
        self.active = config.newrelic_active
        if self.active:
            agent.initialize(config.newrelic_ini_path,
                                      config.newrelic_application_env)
            self.newrelic_application = agent.application()

    def set_logger(self, custom_logger):
        self.custom_logger = custom_logger

    def duration(self, custom_metric_name=None,
                 background_task_name="testFunction",
                 background_task_group="testGroup"):
        if self.active:
            return Duration(self, newrelic_application=self.newrelic_application,
                            custom_logger=self.custom_logger,
                            custom_metric_name=custom_metric_name,
                            background_task_name=background_task_name,
                            background_task_group=background_task_group)
        else:
            return ZeroClass()

    def duration_per_arg(self, custom_metric_name=None,
                 background_task_name="testFunction",
                 background_task_group="testGroup",
                 get_arg=None):
        if self.active:
            return DurationPerArg(self, newrelic_application=self.newrelic_application,
                            custom_logger=self.custom_logger,
                            custom_metric_name=custom_metric_name,
                            background_task_name=background_task_name,
                            background_task_group=background_task_group,
                            get_arg=get_arg)
        else:
            return ZeroClass()


class Duration(object):
    def __init__(self, monitor, newrelic_application, custom_logger=None,
                 custom_metric_name=None,
                 background_task_name="testFunction",
                 background_task_group="testGroup"):
        self.monitor = monitor
        self.newrelic_application = newrelic_application
        self.custom_metric_name = custom_metric_name
        self.name = background_task_name
        self.group = background_task_group
        if custom_logger:
            self.logger = custom_logger
        else:
            self.logger = Logger

    def __call__(self, fn):
        @agent.background_task(application=self.newrelic_application,
                                        name=self.name, group=self.group)
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not self.custom_metric_name:
                self.custom_metric_name = fn.func_name

            def send_metric(rs, start):
                _end = time.time()
                _total_duration = _end - start
                custom_metric = "Custom/{}".format(self.custom_metric_name)
                newrelic_application.record_custom_metric(custom_metric, _total_duration)
                return rs

            def calculate_deferred_execute_time(r, start_time):
                return send_metric(r, start_time)

            _start_time = time.time()
            result = fn(*args, **kwargs)
            if isinstance(result, defer.Deferred):
                result.addCallback(calculate_deferred_execute_time, start_time=_start_time)
            else:
                send_metric(result, _start_time)
            return result
        return wrapper


class DurationPerArg(Duration):
    def __init__(self, monitor, newrelic_application, custom_logger=None,
                 custom_metric_name=None, background_task_name='testFunction',
                 background_task_group='test', get_arg=None):
        Duration.__init__(self, monitor=monitor,
                          newrelic_application=newrelic_application,
                          custom_logger=custom_logger,
                          custom_metric_name=custom_metric_name,
                          background_task_name=background_task_name,
                          background_task_group=background_task_group)
        self.arg_to_get = get_arg

    def __call__(self, fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            _merged_custom_metric_name = []

            if self.custom_metric_name:
                _merged_custom_metric_name.append(self.custom_metric_name)
            else:
                _merged_custom_metric_name.append(fn.func_name)

            try:
                if self.arg_to_get and type(self.arg_to_get) is list:
                    for function_params in self.arg_to_get:
                        if function_params in kwargs:
                            _merged_custom_metric_name.append(kwargs[function_params])
                        elif hasattr(args[0], function_params):
                            _merged_custom_metric_name.append(getattr(args[0],
                                function_params))
                elif self.arg_to_get and type(self.arg_to_get) is str:
                    _merged_custom_metric_name.append(kwargs[self.arg_to_get])
            except KeyError, e:
                self.logger.error("Key not found [" + e.message + "]")

            if len(_merged_custom_metric_name):
                _custom_metric_name = ".".join(_merged_custom_metric_name)

                @super.__call__(self, fn)
                def duration_wrapper(fnn, *args, **kwargs):
                    return fnn(*args, **kwargs)

                return duration_wrapper(fn, *args, **kwargs)
        return wrapper


class ZeroClass(object):
    def __call__(self, fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)
        return wrapper
