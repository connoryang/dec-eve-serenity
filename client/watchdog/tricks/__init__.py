#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\watchdog\tricks\__init__.py
import os
import signal
import subprocess
import time
from watchdog.utils import echo, has_attribute
from watchdog.events import PatternMatchingEventHandler

class Trick(PatternMatchingEventHandler):

    @classmethod
    def generate_yaml(cls):
        context = dict(module_name=cls.__module__, klass_name=cls.__name__)
        template_yaml = '- %(module_name)s.%(klass_name)s:\n  args:\n  - argument1\n  - argument2\n  kwargs:\n    patterns:\n    - "*.py"\n    - "*.js"\n    ignore_patterns:\n    - "version.py"\n    ignore_directories: false\n'
        return template_yaml % context


class LoggerTrick(Trick):

    def on_any_event(self, event):
        pass

    @echo.echo
    def on_modified(self, event):
        pass

    @echo.echo
    def on_deleted(self, event):
        pass

    @echo.echo
    def on_created(self, event):
        pass

    @echo.echo
    def on_moved(self, event):
        pass


class ShellCommandTrick(Trick):

    def __init__(self, shell_command = None, patterns = None, ignore_patterns = None, ignore_directories = False, wait_for_process = False, drop_during_process = False):
        super(ShellCommandTrick, self).__init__(patterns, ignore_patterns, ignore_directories)
        self.shell_command = shell_command
        self.wait_for_process = wait_for_process
        self.drop_during_process = drop_during_process
        self.process = None

    def on_any_event(self, event):
        from string import Template
        if self.drop_during_process and self.process and self.process.poll() is None:
            return
        if event.is_directory:
            object_type = 'directory'
        else:
            object_type = 'file'
        context = {'watch_src_path': event.src_path,
         'watch_dest_path': '',
         'watch_event_type': event.event_type,
         'watch_object': object_type}
        if self.shell_command is None:
            if has_attribute(event, 'dest_path'):
                context.update({'dest_path': event.dest_path})
                command = 'echo "${watch_event_type} ${watch_object} from ${watch_src_path} to ${watch_dest_path}"'
            else:
                command = 'echo "${watch_event_type} ${watch_object} ${watch_src_path}"'
        else:
            if has_attribute(event, 'dest_path'):
                context.update({'watch_dest_path': event.dest_path})
            command = self.shell_command
        command = Template(command).safe_substitute(**context)
        self.process = subprocess.Popen(command, shell=True)
        if self.wait_for_process:
            self.process.wait()


class AutoRestartTrick(Trick):

    def __init__(self, command, patterns = None, ignore_patterns = None, ignore_directories = False, stop_signal = signal.SIGINT, kill_after = 10):
        super(AutoRestartTrick, self).__init__(patterns, ignore_patterns, ignore_directories)
        self.command = ['setsid'] + command
        self.stop_signal = stop_signal
        self.kill_after = kill_after
        self.process = None

    def start(self):
        self.process = subprocess.Popen(self.command)

    def stop(self):
        if self.process is None:
            return
        try:
            os.killpg(os.getpgid(self.process.pid), self.stop_signal)
        except OSError:
            pass
        else:
            kill_time = time.time() + self.kill_after
            while time.time() < kill_time:
                if self.process.poll() is not None:
                    break
                time.sleep(0.25)
            else:
                try:
                    os.killpg(os.getpgid(self.process.pid), 9)
                except OSError:
                    pass

        self.process = None

    @echo.echo
    def on_any_event(self, event):
        self.stop()
        self.start()
