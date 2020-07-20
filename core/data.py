import re
import pandas as pd
import copy
import datetime as dt

from fw.core.datetime import DateParser
import fw.core.settings as sets


class DataLoader:
    def __init__(self, keywords):
        self._kws = keywords
        self._add_relevant_settings_to_self()

    def _add_relevant_settings_to_self(self):
        self._eval_ind = sets.EVAL_INDICATOR
        self._eval_len = len(self._eval_ind)

    def _add_args_to_kwargs(self, name, args, kwargs):
        if len(args) == 0:
            return kwargs
        vrs = []

        # identify arguments indicated in the name (e.g. 'do_${arg1}_to_${arg2}') and add to vrs.
        # TODO: find a replacement for \w+
        # vrs.extend([re.findall('\w+', x)[0].lower() for x in re.findall('\${\w+}', name)])
        try:
            man_vars = self._kws.get_mandatory_fields(name)
            for name_var, man_var in zip(vrs, tuple(man_vars)):
                if name_var.upper() == man_var.upper():
                    man_vars.remove(man_var)
            vrs.extend(man_vars)
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

    @staticmethod
    def _combine_data_object_and_file_data(data, file_data):
        if file_data is None:
            return data
        else:
            return file_data

    @staticmethod
    def _transform_read_datetime(val):
        if not isinstance(val, str):
            return val
        try:
            return dt.datetime.strptime(val, '%Y-%m-%d %H:%M:%S%z')
        except ValueError:
            return val

    def _reduce_rows(self, data, rows):
        if rows is None:
            return data
        rows = str(rows)
        if rows[0:self._eval_len] == self._eval_ind:
            context = {}
            fltr = data.apply(lambda r: self._evaluate_cell(rows, r, context), axis=1)
            data = data[fltr]
        elif rows is not None or rows.upper() not in ('ALL', 'NONE'):
            rows_int = [int(x) - 1 for x in rows.split(',')]
            data = data.loc[rows_int]
        return data

    def _extract_data(self, kwargs):
        data = kwargs.get('DATA')
        if data is not None:
            kwargs.pop('DATA')
        data_file = kwargs.get('DATA_FILE')
        if data_file is not None:
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
            file_data = file_data.applymap(self._transform_read_datetime)
            result = self._combine_data_object_and_file_data(data, file_data)
        else:
            result = data
        return result, kwargs

    def _eval_needed(self, val):
        if not isinstance(val, str):
            return False
        if val[0:self._eval_len] != self._eval_ind:
            return False
        return True

    def _evaluate_data(self, data):
        context_clean = {}

        def per_cell(val, row, context):
            if self._eval_needed(val) is True:
                return self._evaluate_cell(val, row, context)
            else:
                return val

        def per_row(row):
            context_row = copy.deepcopy(context_clean)
            return row.apply(per_cell, row=row, context=context_row)

        eval_rows = data.applymap(self._eval_needed).apply(any, axis=1)
        data.loc[eval_rows] = data.loc[eval_rows].apply(per_row, axis=1)
        return data

    def _eval_till_error(self, val, row, context):
        try:
            result = eval(val, context)
        except NameError as e:
            try:
                missing = e.args[0].split("'")[1]
                context[missing] = self._evaluate_cell(row[missing], row, context)
                result = self._eval_till_error(val, row, context)
            except KeyError:
                raise e
        return result

    def _evaluate_cell(self, val, row, context):
        if not self._eval_needed(val):
            return val
        val = val.replace(self._eval_ind, '')
        return self._eval_till_error(val, row, context)

    def load_csv(self, filename, **options):
        options['sep'] = options.get('sep', sets.CSV_SEP)
        options['header'] = options.get('header', 0)
        file_data = pd.read_csv(filename, **options)
        return file_data

    def load_json(self, filename, **options):
        raise TypeError('Json files not supported yet.')

    def load_excel(self, filename, **options):
        raise TypeError('Excel files not supported yet.')

    def get_data(self, name=None, *args, **kwargs):
        kwargs = self._add_args_to_kwargs(name, args, kwargs)
        kwargs = {k.upper(): v for k, v in kwargs.items()}

        kwargs = self._extract_and_add_settings(kwargs)
        rows = kwargs.get('ROWS')
        data, kwargs = self._extract_data(kwargs)
        if data is not None:
            data = data.assign(**kwargs)
            data = self._reduce_rows(data, rows)
        elif len(kwargs) > 0:
            kwargs = {k: [v] for k, v in kwargs.items()}
            data = pd.DataFrame(kwargs)
        if data is not None:
            dp = DateParser()
            data = data.applymap(dp.make_date_or_return)
            data = self._evaluate_data(data)
        return data

    def _extract_and_add_settings(self, kwargs):
        prefix = sets.SETTING_PREFIX
        p_len = len(prefix)
        setting_kwargs = {k[p_len:]: v for k, v in kwargs.items() if prefix == k[0:p_len]}
        for key in setting_kwargs.keys():
            kwargs.pop('{}{}'.format(prefix, key))
        sets.update_settings(**setting_kwargs)
        return kwargs


def validate_data(data, mandatory, conditional):
    cols = get_cols(data)
    missing = [var for var in mandatory if var not in cols]
    if len(missing) != 0:
        raise ImportError('Not all mandatory variables where passed ("{}", is/are missing).'
                          .format('","'.join(missing)))


def get_cols(data=None):
    if isinstance(data, pd.DataFrame):
        return data.columns
    elif isinstance(data, pd.Series):
        return data.index
    elif data is None:
        return []
    else:
        raise TypeError('Data is of non-supported type: "{}".'.format(data.__class__))


# class DataLibrary:
#     def __init__(self, fwo):
#         self._fwo = fwo
#
#     def _safe_assign_df(self, data, **kwargs):
#         edit_cols = tuple(set(data.columns) & set(kwargs.keys()))
#         new_cols = {col: val for col, val in kwargs.items() if col not in edit_cols}
#         data = data.assign(**new_cols)
#
#         def_spec = self._fwo.fw_settings.DEFAULT_SPECIFIER
#         for col in edit_cols:
#             if def_spec in data[col].to_list():
#                 new_data = data[[col]].assign(**{col: kwargs.get(col)})
#                 new_list = []
#                 for old, new in zip(data[col], new_data[col]):
#                     if old == def_spec:
#                         new_list.append(new)
#                     else:
#                         new_list.append(old)
#                 data = data.assign(**{col: new_list})
#         return data
#
#     def _safe_assign_series(self, data, **kwargs):
#         edit_cols = tuple(set(data.index) & set(kwargs.keys()))
#         new_cols = {col: val for col, val in kwargs.items() if col not in edit_cols}
#         data = data.append(pd.Series(new_cols))
#         def_spec = self._fwo.fw_settings.DEFAULT_SPECIFIER
#         for col in edit_cols:
#             if def_spec == data[col]:
#                 data[col] = kwargs.get(col)
#         return data
#
#     def _use_default_data(self, data):
#         if data is None:
#             try:
#                 data = self._fwo.DATA
#             except AttributeError:
#                 raise ImportError('No data was passed, and no data was present in the framework object either.')
#         return data
#
#     def safe_assign(self, data=None, **kwargs):
#         data = self._use_default_data(data)
#         if isinstance(data, pd.DataFrame):
#             result = self._safe_assign_df(data, **kwargs)
#         elif isinstance(data, pd.Series):
#             result = self._safe_assign_series(data, **kwargs)
#         elif data is None:
#             if kwargs != {}:
#                 result = pd.DataFrame.from_dict(kwargs)
#             else:
#                 result = data
#         else:
#             raise TypeError('The given type of data - "{}" - is not supported, '
#                             'only pandas.DataFrames and pandas.Series are supported.'
#                             .format(data.__class__))
#         return result
#
