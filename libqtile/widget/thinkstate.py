from . import base
import logging


bat_info_off = {
    'c_design': (3,  2),
    'c_remaining': (1, 14),
    'c_last_full': (2,  2),
    'rt_now': (2,  4),
    'rt': (2,  6),
    'temperature': (1,  4),
    'voltage': (1,  6),
    'current_now': (1,  8),
    'current_avg': (1, 10),
    'percent': (1, 12),
    'cycle': (2, 12),
    'state': (1,  1),
}

charge_status = {
    1216: '',
    1232: '\u2193',
    1248: '\u2191'
}


def whours(minute):
    """
    """
    if minute == 65535:
        return '--:--'
    return '{:>2}:{:>02}'.format(minute//60, minute-(minute//60)*60)


def set_value(raw, arr):
        """
        """
        return int('0x%s%s' % (raw[16 * arr[0] + arr[1] + 1],
                               raw[16 * arr[0] + arr[1]]),
                   16)


class ThinkBatState(base.ThreadedPollText):

    """
        Displays interface down and up speed.
    """
    orientations = base.ORIENTATION_BOTH
    defaults = [
            ('update_interval', 5, 'The update interval.'),
    ]

    def __init__(self, **config):
        base.ThreadedPollText.__init__(self, **config)
        self.add_defaults(ThinkBatState.defaults)

    def get_state(self):
        """
        """
        try:
            with open('/sys/devices/platform/smapi/BAT0/dump', 'r') as f:
                return f.read().split()
        except Exception as e:
            self.qtile.log.error(e)

    def poll(self):
        try:
            raw = self.get_state()
            state = {}
            state['state'] = set_value(raw, bat_info_off['state'])
            for k in bat_info_off.keys():
                if (k in ('current_now', 'current_avg')) and \
                   (state['state'] == 0x4d0):
                    state[k] = (65535 - set_value(raw, bat_info_off[k]) + 1)
                else:
                    state[k] = set_value(raw, bat_info_off[k])
            state['power_now'] = state['current_now'] * state['voltage']/1000
            state['power_avg'] = state['current_avg'] * state['voltage']/1000

            status = state['c_last_full']*100//state['c_design']

            res = ('\uf241            \uf0e7                             '
                   '\n'
                   '{:>4}'
                   '{:0>2}%'
                   '{:>7.1f}W'
                   '{:>7}'
                   '{:>7.2f}Wh'
                   '{:>3}%'
                   '').format(charge_status[state['state']], state['percent'],
                              state['power_avg']/1000,
                              whours(state['rt']),
                              state['c_last_full']/100, status)
            return res
        except Exception as e:
            self.qtile.log.error(e)
