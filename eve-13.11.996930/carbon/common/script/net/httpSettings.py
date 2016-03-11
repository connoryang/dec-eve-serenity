#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\script\net\httpSettings.py
import blue
TEMPLATES_DIR = [ blue.paths.ResolvePath(p) for p in ('wwwroot:/assets/views', 'wwwroot:/assets/views/old') ]
exports = {'httpSettings.TEMPLATES_DIR': TEMPLATES_DIR}
