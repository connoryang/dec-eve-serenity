#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\coverage\collector.py
import os, sys, threading
try:
    from coverage.tracer import CTracer
except ImportError:
    if os.getenv('COVERAGE_TEST_TRACER') == 'c':
        sys.stderr.write("*** COVERAGE_TEST_TRACER is 'c' but can't import CTracer!\n")
        sys.exit(1)
    CTracer = None

class PyTracer(object):

    def __init__(self):
        self.data = None
        self.should_trace = None
        self.should_trace_cache = None
        self.warn = None
        self.cur_file_data = None
        self.last_line = 0
        self.data_stack = []
        self.last_exc_back = None
        self.last_exc_firstlineno = 0
        self.arcs = False
        self.thread = None
        self.stopped = False

    def _trace(self, frame, event, arg_unused):
        if self.stopped:
            return
        if self.last_exc_back:
            if frame == self.last_exc_back:
                if self.arcs and self.cur_file_data:
                    pair = (self.last_line, -self.last_exc_firstlineno)
                    self.cur_file_data[pair] = None
                self.cur_file_data, self.last_line = self.data_stack.pop()
            self.last_exc_back = None
        if event == 'call':
            self.data_stack.append((self.cur_file_data, self.last_line))
            filename = frame.f_code.co_filename
            if filename not in self.should_trace_cache:
                tracename = self.should_trace(filename, frame)
                self.should_trace_cache[filename] = tracename
            else:
                tracename = self.should_trace_cache[filename]
            if tracename:
                if tracename not in self.data:
                    self.data[tracename] = {}
                self.cur_file_data = self.data[tracename]
            else:
                self.cur_file_data = None
            self.last_line = -1
        elif event == 'line':
            if self.cur_file_data is not None:
                if self.arcs:
                    self.cur_file_data[self.last_line, frame.f_lineno] = None
                else:
                    self.cur_file_data[frame.f_lineno] = None
            self.last_line = frame.f_lineno
        elif event == 'return':
            if self.arcs and self.cur_file_data:
                first = frame.f_code.co_firstlineno
                self.cur_file_data[self.last_line, -first] = None
            self.cur_file_data, self.last_line = self.data_stack.pop()
        elif event == 'exception':
            self.last_exc_back = frame.f_back
            self.last_exc_firstlineno = frame.f_code.co_firstlineno
        return self._trace

    def start(self):
        self.thread = threading.currentThread()
        sys.settrace(self._trace)
        return self._trace

    def stop(self):
        self.stopped = True
        if self.thread != threading.currentThread():
            return
        if hasattr(sys, 'gettrace') and self.warn:
            if sys.gettrace() != self._trace:
                msg = 'Trace function changed, measurement is likely wrong: %r'
                self.warn(msg % (sys.gettrace(),))
        sys.settrace(None)

    def get_stats(self):
        return None


class Collector(object):
    _collectors = []

    def __init__(self, should_trace, timid, branch, warn):
        self.should_trace = should_trace
        self.warn = warn
        self.branch = branch
        self.reset()
        if timid:
            self._trace_class = PyTracer
        else:
            self._trace_class = CTracer or PyTracer

    def __repr__(self):
        return '<Collector at 0x%x>' % id(self)

    def tracer_name(self):
        return self._trace_class.__name__

    def reset(self):
        self.data = {}
        self.should_trace_cache = {}
        self.tracers = []

    def _start_tracer(self):
        tracer = self._trace_class()
        tracer.data = self.data
        tracer.arcs = self.branch
        tracer.should_trace = self.should_trace
        tracer.should_trace_cache = self.should_trace_cache
        tracer.warn = self.warn
        fn = tracer.start()
        self.tracers.append(tracer)
        return fn

    def _installation_trace(self, frame_unused, event_unused, arg_unused):
        sys.settrace(None)
        fn = self._start_tracer()
        if fn:
            fn = fn(frame_unused, event_unused, arg_unused)
        return fn

    def start(self):
        if self._collectors:
            self._collectors[-1].pause()
        self._collectors.append(self)
        traces0 = []
        if hasattr(sys, 'gettrace'):
            fn0 = sys.gettrace()
            if fn0:
                tracer0 = getattr(fn0, '__self__', None)
                if tracer0:
                    traces0 = getattr(tracer0, 'traces', [])
        fn = self._start_tracer()
        for args in traces0:
            (frame, event, arg), lineno = args
            try:
                fn(frame, event, arg, lineno=lineno)
            except TypeError:
                raise Exception('fullcoverage must be run with the C trace function.')

        threading.settrace(self._installation_trace)

    def stop(self):
        self.pause()
        self.tracers = []
        self._collectors.pop()
        if self._collectors:
            self._collectors[-1].resume()

    def pause(self):
        for tracer in self.tracers:
            tracer.stop()
            stats = tracer.get_stats()
            if stats:
                print '\nCoverage.py tracer stats:'
                for k in sorted(stats.keys()):
                    print '%16s: %s' % (k, stats[k])

        threading.settrace(None)

    def resume(self):
        for tracer in self.tracers:
            tracer.start()

        threading.settrace(self._installation_trace)

    def get_line_data(self):
        if self.branch:
            line_data = {}
            for f, arcs in self.data.items():
                line_data[f] = ldf = {}
                for l1, _ in list(arcs.keys()):
                    if l1:
                        ldf[l1] = None

            return line_data
        else:
            return self.data

    def get_arc_data(self):
        if self.branch:
            return self.data
        else:
            return {}
