from psutil import process_iter, Process

def parse_cmdline_args(cmdline_args):
    cmdline_args_parsed = {}
    for cmdline_arg in cmdline_args:
        if len(cmdline_arg) > 0 and '=' in cmdline_arg:
            key, value = cmdline_arg[2:].split('=')
            cmdline_args_parsed[key] = value
    return cmdline_args_parsed


def find_LCU_process():
    for process in process_iter():
        if process.name() in ['LeagueClientUx.exe', 'LeagueClientUx']:
            return process
    return None
