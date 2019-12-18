import logging
import re
import fw.core.keyword as kw
import pandas as pd


class DataLoader:
    def __init__(self, fw):
        self._fw = fw

    def _add_args_to_kwargs(self, name, args, kwargs):
        if len(args) == 0:
            return kwargs
        vrs = []
        # identify arguments indicated in the name (e.g. 'do_${arg1}_to_${arg2}') and add to vrs.
        vrs.extend([re.findall('\w+', x)[0].lower() for x in re.findall('\${\w+}', name)])
        try:
            vrs.extend(kw.KeywordArgs().get_mandatory_args(name))
        except AssertionError:
            pass
        if len(args) > len(vrs):
            raise ValueError("More positional arguments where passed "
                             "than possible for this keyword (only variables '{vars}' "
                             "can be passed as positional arguments).".format(vars="', '".join(vrs)))
        for vr, arg in zip(vrs, args):
            if vr.upper() in [v.upper() for v in kwargs.keys()]:
                raise ValueError('Variable "{vr}" was passed twice; once as positional '
                                 'variable (with value "{vl1}") and once as named '
                                 'variable (with value "{vl2}"). Please remove one of two.'
                                 .format(vr=vr, vl1=arg, vl2=kwargs.get(vr)))
            kwargs[vr] = arg
        return kwargs

    def _combine_data_object_and_file_data(self, data, file_data):
        return file_data

    def _extract_data(self, kwargs):
        data = kwargs.get('DATA')
        if not data:
            kwargs.pop('DATA')
        data_file = kwargs.get('DATA_FILE')
        if not data_file:
            kwargs.pop('DATA_FILE')
            try:
                file_data = self.load_csv(data_file)
            except ImportError:
                try:
                    file_data = self.load_csv(data_file)
                except ImportError:
                    try:
                        file_data = self.load_csv(data_file)
                    except ImportError:
                        raise ImportError('Data file was not recognized as a valid data file '
                                          '(csv, json or excel file).')
            result = self._combine_data_object_and_file_data(data, file_data)
        else:
            result = data
        return result, kwargs

    def _reduce_rows(self, data, rows):
        if rows is None:
            return data
        rows = str(rows)
        rows_int = map(int, rows.split(', '))
        return data.iloc[rows_int]

    def load_csv(self, filename, **options):
        options['sep'] = options.get('sep', self._fw.SETTINGS.CSV_SEPERATOR)
        options['header'] = options.get('header', 0)
        options['dtype'] = options.get('dtype', 0)
        file_data = pd.read_csv(filename, **options)
        return file_data

    def load_json(self, filename, **options):
        return filename

    def load_excel(self, filename, **options):
        return filename

    def evaluate(self, data):
        return data

    def get_data(self, name, *args, **kwargs):
        kwargs = self._add_args_to_kwargs(name, args, kwargs)
        kwargs = {k.upper(): v for k, v in kwargs.items()}
        kwargs = self.add_settings(kwargs)
        rows = kwargs.get('ROWS')
        data, kwargs = self._extract_data(kwargs)
        if data is not None:
            data = data.assign(**kwargs)
            data = self._reduce_rows(data, rows)
        elif len(kwargs) > 0:
            kwargs = {k: [v] for k, v in kwargs.items()}
            data = pd.DataFrame(kwargs)
        if data is not None:
            data = self.evaluate(data)
        return data

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
