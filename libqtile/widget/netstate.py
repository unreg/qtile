from . import base


def humanize_traffic(value, dec=False):
    """
    """
    if dec:
        suffix = ['B', 'K', 'M', 'G', 'T']
        divide = 10**3
    else:
        suffix = ['  ', 'Ki', 'Mi', 'Gi', 'Ti']
        divide = 2**10

    while (value > divide) and (len(suffix) > 1):
        value /= divide
        suffix.pop(0)

    return '%6.2f%s' % (value, suffix[0])


class NetState(base.ThreadedPollText):

    """
        Displays interface down and up speed.
    """
    orientations = base.ORIENTATION_BOTH
    defaults = [
        ('interface', 'wlan0', 'The interface to monitor'),
        ('update_interval', 1, 'The update interval.'),
    ]

    def __init__(self, **config):
        base.ThreadedPollText.__init__(self, **config)
        self.add_defaults(NetState.defaults)
        self.interfaces = self.get_state()

    def get_state(self):
        lines = []  # type: List[str]
        with open('/proc/net/dev', 'r') as f:
            lines = f.readlines()[2:]
        interfaces = {}
        for s in lines:
            int_s = s.split()
            name = int_s[0][:-1]
            down = float(int_s[1])
            up = float(int_s[-8])
            interfaces[name] = {'down': down, 'up': up}
        return interfaces

    def poll(self):
        try:
            new_int = self.get_state()
            down_s = humanize_traffic(new_int[self.interface]['down'])
            up_s = humanize_traffic(new_int[self.interface]['up'])
            down = new_int[self.interface]['down'] - \
                self.interfaces[self.interface]['down']
            up = new_int[self.interface]['up'] - \
                self.interfaces[self.interface]['up']

            down = down / self.update_interval
            up = up / self.update_interval
            down = humanize_traffic(down)
            up = humanize_traffic(up)
            str_base = ('{:>8}:'
                        ' \u2193 '
                        '{:>9}B/s'
                        '{:>10}B'
                        '\n'
                        '          \u2191 '
                        '{:>9}B/s'
                        '{:>10}B'
                        ).format(self.interface, down, down_s, up, up_s)

            self.interfaces = new_int
            return str_base
        except Exception as e:
            self.qtile.log.error(e)
