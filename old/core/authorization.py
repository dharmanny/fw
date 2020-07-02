from pykeepass import PyKeePass
from fw.old.core import Util
import logging


class NoKeyVault:
    def __init__(self, *args, **kwargs):
        pass


class KeePass:
    def __init__(self, fwo):
        kdbx = fwo.fw_settings.KEEPASS_DB_FILE
        key = fwo.fw_settings.KEEPASS_KEY

        if kdbx is not None:
            logging.debug('A keyfile was passed as authorization method for Keepass.')
            self._kp = PyKeePass(kdbx, keyfile=key, transformed_key=None)
        if fwo.env.ENV_NAME:
            self._env = fwo.env.ENV_NAME
        else:
            self._env = ('',)

        logging.debug('Environment used for Keepass is: "{}"'.format('/'.join(map(str, self._env))))

    def _get_keypair(self, title, env=None):
        env = self._env if env is None else env
        entries = self._kp.find_entries_by_title(title)
        filtered_entries = [e for e in entries if '/'.join(env) in str(e)]
        if len(filtered_entries) == 0:
            if len(env) == 1:       # if environment has only one part left, raise error
                raise ValueError('No matching keepass entries were found for "{t}" '
                                 'for the indicated environment or its super environments ({e}).'
                                 .format(t=title, e='/'.join(self._env)))
            else:                   # else try a more generic key
                filtered_entries = [self._get_keypair(title, env=env[:-1])]
        elif len(filtered_entries) > 1:
            logging.warning('Multiple keys were found. The first result will be returned only.')
        return filtered_entries[0]

    def get_username(self, title):
        result = self._get_keypair(title)
        logging.info('Returning username {un} for title {t}.'.format(un=result.username, t=title))
        return result.username

    def get_password(self, title):
        result = self._get_keypair(title)
        logging.info('Returning password {un} for title {t}.'.format(un='*'*len(result.password), t=title))
        return result.password


class KeyVaultPicker:
    mapper = {'keepass': KeePass}

    def get_key_vault_class(self):
        try:
            kvs = Util().settings().KEYVAULT_SYSTEM
        except AttributeError:
            kvs = 'none'
        logging.debug('The requested key vault system is {}'.format(kvs))
        kvs_cls = self.mapper.get(kvs.lower())
        if kvs_cls is None:
            logging.warning('The indicated key vault system: "{}", is not supported.'.format(kvs))
            kvs_cls = NoKeyVault
        return [kvs_cls]


class Authorization(*KeyVaultPicker().get_key_vault_class()):
    pass
