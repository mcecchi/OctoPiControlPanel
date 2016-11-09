import os
from ConfigParser import RawConfigParser

class OctoPiControlPanelConfig:

    @staticmethod
    def load_from_file():
        config = OctoPiControlPanelConfig()

        cfg = RawConfigParser()
        config.script_directory = os.path.dirname(os.path.realpath(__file__))
        settings_file_path = os.path.join(config.script_directory, "OctoPiControlPanelConfig.cfg")
        cfg.readfp(open(settings_file_path, "r"))

        config.api_baseurl = cfg.get('settings', 'baseurl')
        config.apikey = cfg.get('settings', 'apikey')
        config.updatetime = cfg.getint('settings', 'updatetime')
        config.backlightofftime = cfg.getint('settings', 'backlightofftime')

        if cfg.has_option('settings', 'width'):
            config.width = cfg.getint('settings', 'width')
        else:
            config.width = 320

        if cfg.has_option('settings', 'height'):
            config.height = cfg.getint('settings', 'height')
        else:
            config.height = 240

        if cfg.has_option('settings', 'caption'):
            config.caption = cfg.get('settings', 'caption')
        else:
            config.caption = "OctoPiControlPanelConfig"

        return config

