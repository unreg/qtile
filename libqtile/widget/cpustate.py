from . import base
from libqtile.log_utils import logger

import Pyro4


Pyro4.config.COMMTIMEOUT = 0.5


def bar(value, max_size, max_value=100):
    """
    """
    if max_value == 100:
        size = int(value * max_size / 100)
        return '\u25a0' * int(size)


class CpuState(base.ThreadedPollText):

    """
        Displays interface down and up speed.
    """
    orientations = base.ORIENTATION_BOTH
    defaults = [
            ('update_interval', 1, 'The update interval.'),
    ]

    def __init__(self, **config):
        base.ThreadedPollText.__init__(self, **config)
        self.add_defaults(CpuState.defaults)
        self.remote = Pyro4.Proxy('PYRO:example.incubus@localhost:9999')

    def poll(self):
        tmp = self.text
        res = '  GHz         4 core              %'
        try:
            count, data = self.remote.status()
            for cpu in count:
                res += ('\n{:>5.2f} '
                        '{:<22} '
                        '{:>6.2f}').format(data[cpu]['frq'],
                                           bar(data[cpu]['c0'], 22),
                                           data[cpu]['c0'])
            return res
        except Exception as e:
            logger.error(e)
            return tmp
