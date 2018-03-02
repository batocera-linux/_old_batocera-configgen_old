#!/usr/bin/env python
import Command
import recalboxFiles
from generators.Generator import Generator
import dolphinControllers
import dolphinSYSCONF
import shutil
import os.path
from os import environ
import ConfigParser
from settings.unixSettings import UnixSettings

# seem to be only for the gamecube. However, while this is not in a gamecube section
# it may be used for something else, so set it anyway

def getDolphinLangFromEnvironment():
    lang = environ['LANG'][:5]
    availableLanguages = { "en_US": 0, "de_DE": 1, "fr_FR": 2, "es_ES": 3, "it_IT": 4, "nl_NL": 5 }
    if lang in availableLanguages:
        return availableLanguages[lang]
    else:
        return availableLanguages["en_US"]

class DolphinGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):
        dolphinControllers.generateControllerConfig(system, playersControllers, rom)

        dolphinSettings = UnixSettings(recalboxFiles.dolphinIni, separator=' ')
        #Draw or not FPS
	if system.config['showFPS'] == 'true':
            dolphinSettings.save("ShowLag", "True")
            dolphinSettings.save("ShowFrameCount", "True")
        else:
            dolphinSettings.save("ShowLag", "False")
            dolphinSettings.save("ShowFrameCount", "False")

        # don't ask about statistics
        dolphinSettings.save("PermissionAsked", "True")

        # don't confirm at stop
        dolphinSettings.save("ConfirmStop", "False")

        # language (for gamecube at least)
        dolphinSettings.save("SelectedLanguage", getDolphinLangFromEnvironment())

        # update SYSCONF
        try:
            dolphinSYSCONF.update(system.config, recalboxFiles.dolphinSYSCONF, gameResolution)
        except Exception:
            pass # don't fail in case of SYSCONF update

        commandArray = [recalboxFiles.recalboxBins[system.config['emulator']], "-e", rom]
        if 'args' in system.config and system.config['args'] is not None:
             commandArray.extend(system.config['args'])
        return Command.Command(array=commandArray, env={"XDG_CONFIG_HOME":recalboxFiles.CONF, "XDG_DATA_HOME":recalboxFiles.SAVES})
