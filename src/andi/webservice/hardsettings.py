"""
Paramètres de configuration hardcodés
(ne pouvant être personnalisés au contraire de ceux de ``defaultsettings``)
"""
import datetime
import pytz

# Version API actuelle
# FIXME: c'est vraiment cracra. Le versionnage devrait se faire par URLs
API_VERSION = 1

CONFIG_FILE_ENNVAR = "AN4_CONFIG_FILE"

START_TIME = datetime.datetime.now(pytz.utc)

# Maxi de threads utilisées pour rendre asynchrones les exécutions synchrones
# voir library.call_blocking
AWAITABLE_BLOCKING_POOL_MAX_THREADS = 10

# Fichier CSV à utiliser pour les concersions ROME -> NAF
ROME2NAF_CSV_FILE = 'andi_rome2naf_20200130.csv'
MAX_VALUE_GROUP = '5'
