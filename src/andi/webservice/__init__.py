import logging

import pkg_resources

# Custom logger
LOG = logging.getLogger(name=__name__)

# PEP 396 style version marker
try:
    __version__ = pkg_resources.get_distribution('andi-matching').version
except pkg_resources.DistributionNotFound:
    LOG.warning("Could not get the package version from pkg_resources")
    __version__ = "unknown"

__author__ = "ANDI team - Caisse des Dépôts et Consignations"
__author_email__ = 'andi@caissedesdepots.fr'
__license__ = 'GNU Affero General Public License v3'
