"""
Paramètres de configuration hardcodés
(ne pouvant être personnalisés au contraire de ceux de ``defaultsettings``)
"""
import datetime
import pytz

# Version API actuelle
ALLOWED_API_VERSIONS = {"1.0"}

CONFIG_FILE_ENNVAR = "AN4_CONFIG_FILE"

START_TIME = datetime.datetime.now(pytz.utc)

# Fichier CSV à utiliser pour les conversions ROME -> NAF
ROME2NAF_CSV_FILE = 'andi_rome2naf_20200130.csv'
MAX_VALUE_GROUP = '5'
