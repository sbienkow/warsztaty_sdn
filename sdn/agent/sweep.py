import re
import subprocess


class PingSweep(object):
    SWEEP_CMD = 'sudo nmap -v -sn -PE -n -oG - %s'
    HOSTS_UP = re.compile(r"([0-9]+) hosts up")

    def sweep(self, target):
        output = self.exec_command(self.SWEEP_CMD % target)
        if not output:
            return 0

        match = self.HOSTS_UP.search(output)
        if not match:
            return 0

        if len(match.groups()) > 0:
            return int(match.groups()[0])
        else:
            return 0

    @staticmethod
    def exec_command(cmd):
        return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, close_fds=True).stdout.read().decode('utf-8')