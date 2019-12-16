import logging


class DataLoader:
    def __init__(self, fw):
        self._fw = fw

    def add_settings(self, kwargs, init=False):
        fw_sets = {k: v for k, v in kwargs.items() if k[0:2] == '--'}
        for st, val in fw_sets.items():
            kwargs.pop(st)
            self._fw.fw_settings[st.upper()[2:]] = val
            logging.info('Added fw_setting "{s}" with value "{v}"'.format(s=st, v=val))

        test_sets = {k: v for k, v in kwargs.items() if k[0] == '-'}
        if not init:
            for st, val in test_sets.items():
                kwargs.pop(st)
                self._fw.test_settings[st.upper()[1:]] = val
                logging.info('Added test_setting "{s}" with value "{v}"'.format(s=st, v=val))
        elif len(test_sets) > 0:
            msg = 'Test variables were imported during initiation of the Framework. This is not supported'
            logging.error(msg)
            raise AssertionError(msg)
        for k, v in kwargs.items():
            logging.debug('Returned variable to calles:"{k}", "{v}".'.format(k=k, v=v))
        return kwargs
