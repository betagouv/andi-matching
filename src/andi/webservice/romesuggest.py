"""
Initialliy, ANDi directly used the rome suggestion API from LaBonneBoite.

To avoid dependencies, the functionality has been reverse-engineered and improved.
This was done in a Jupyter Notebook, resulting in less modular code, but with
shorter development time.

Basically a Whoosh (full-text matching library) index is built, providing the
text-to-rome suggestion functionnality.

While Whoosh provides a lot more than we used here (suggestions, corrections, ...),
the current functionnality provides a working basis.
"""
import logging
import os
import pathlib
import re
import shutil
import typing as t

import pandas as pd
from slugify import slugify
from whoosh import sorting
from whoosh.analysis import CharsetFilter, StandardAnalyzer
from whoosh.fields import KEYWORD, STORED, TEXT, Schema
from whoosh.index import create_in, exists_in, open_dir
from whoosh.qparser import FuzzyTermPlugin, QueryParser
from whoosh.query import FuzzyTerm
from whoosh.support.charset import accent_map

from .library import words_get
from . import settings

logger = logging.getLogger(__name__)

# Cache pour SUGGEST_STATE
_suggest_state = None


# Attention ! Python 3.7+
def __getattr__(name: str) -> t.Any:
    """
    Lazy globals init
    pseudo globale SUGGEST_STATE
    """
    global _suggest_state  # pylint: disable=global-statement
    if name == "SUGGEST_STATE":
        if _suggest_state is None:
            _suggest_state = init_state(force=settings.config.ROME_SUGGEST_REBUILD)
        return _suggest_state
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def init_state(force=False):
    index_dir = settings.config.ROME_SUGGEST_INDEX_DIR

    if check_table(index_dir) and not force:
        return open_dir(index_dir)

    logger.info('Compiling dataframe references')
    referentiels_dir = pathlib.Path(__file__).resolve().parent / "referentiels"
    # Rome
    rome_labels = pd.read_csv(referentiels_dir / "rome_lbb.csv", sep=',', encoding="utf-8")
    rome_labels.columns = ['rome', 'rome_1', 'rome_2', 'rome_3', 'label', 'slug']
    rome_labels['source'] = 'rome'
    logger.info(f"Obtained {len(rome_labels)} ROME labels")

    # OGR
    ogr_labels = pd.read_csv(referentiels_dir / "ogr_lbb.csv", sep=',', encoding="utf-8")
    ogr_labels.columns = ['code', 'rome_1', 'rome_2', 'rome_3', 'label', 'rome']
    ogr_labels['source'] = 'ogr'
    ogr_labels['slug'] = ogr_labels['label'].apply(lambda x: slugify(x))
    logger.info(f"Obtained {len(ogr_labels)} OGR labels")

    # ONISEP
    onisep_labels = pd.read_csv(referentiels_dir / "metiers_onisep.csv", sep=',', encoding="utf-8")
    onisep_labels.columns = [
        'label', 'url_onisep', 'pub_name',
        'collection', 'year', 'gencod', 'gfe',
        'rome', 'rome_label', 'rome_url']
    onisep_labels['source'] = 'onisep'
    onisep_labels['slug'] = onisep_labels['label'].apply(lambda x: slugify(x))
    logger.info(f"Obtained {len(onisep_labels)} ONISEP labels")

    # Préparation et écriture des données
    # rome_prep = rome_labels[['rome', 'label', 'source', 'slug']].copy()
    # rome_prep['label'] = rome_prep['label'].str.lower()
    # rome_prep = rome_prep.drop_duplicates(subset=['slug', 'rome'])
    #
    # ogr_prep = ogr_labels[['rome', 'label', 'source', 'slug']].copy()
    # ogr_prep['label'] = ogr_prep['label'].str.lower()
    # ogr_prep = ogr_prep.drop_duplicates(subset=['slug', 'rome'])
    #
    # onisep_prep = onisep_labels[['rome', 'label', 'source', 'slug']].copy()
    # onisep_prep['label'] = onisep_prep['label'].str.lower()
    # onisep_prep = onisep_prep.drop_duplicates(subset=['slug', 'rome'])
    def prepared(series: pd.Series) -> pd.Series:
        out = series[["rome", "label", "source", "slug"]].copy()
        out["label"] = series["label"].str.lower()
        return out.drop_duplicates(subset=["slug", "rome"])

    rome_prep = prepared(rome_labels)
    ogr_prep = prepared(ogr_labels)
    onisep_prep = prepared(onisep_labels)

    create_table(index_dir, overwrite=True)
    write_dataframe(index_dir, rome_prep)
    write_dataframe(index_dir, ogr_prep[ogr_prep.rome.notnull()])
    write_dataframe(index_dir, onisep_prep[onisep_prep.rome.notnull()])
    logging.info('Suggestion index tables written')
    return open_dir(index_dir)


def check_table(index_dir: t.Union[str, pathlib.Path]) -> bool:
    """
    Vérifie l'existence des fichiers d'index Whoosh
    Args:
        index_dir: Directory supposée contenir l'index

    Returns:
        True si l'index Whoosh existe
    """
    index_dir = str(index_dir)
    return os.path.exists(index_dir) and exists_in(index_dir)


def create_table(index_dir, *, overwrite=False):
    analyzer = StandardAnalyzer() | CharsetFilter(accent_map)
    schema = Schema(
        label=TEXT(stored=True, analyzer=analyzer, lang='fr'),
        rome=TEXT(stored=True, sortable=True),
        source=KEYWORD(stored=True, sortable=True),
        slug=STORED
    )

    if not os.path.exists(index_dir):
        os.mkdir(index_dir)
    elif exists_in(index_dir):
        if not overwrite:
            logger.critical('An index already exists in %s; overwrite flag not set; abandonning', index_dir)
            raise RuntimeError('Index already exists')
        logger.warning('Index already found, deleting %s to start anew', index_dir)
        shutil.rmtree(index_dir, ignore_errors=True, onerror=None)

        os.mkdir(index_dir)

    logger.info('Whoosh index %s ready for use', index_dir)
    create_in(index_dir, schema)
    return index_dir


# FIXME: Apparemment inutilisé
def write_record(idx, **fields):
    writer = idx.writer()
    writer.add_document(**fields)


def write_dataframe(idx_name, df):
    idx = open_dir(idx_name)
    writer = idx.writer()
    try:
        logger.info("Writing dataframe to index")
        for _, row in df.iterrows():
            writer.add_document(**row.to_dict())
        writer.commit()
        logger.info("Done writing dataframe to index")
    except Exception:
        writer.cancel()
        raise RuntimeError('Failed writing')


class CustomFuzzyTerm(FuzzyTerm):
    def __init__(self, fieldname, text, boost=1.0, maxdist=2,  # pylint: disable=too-many-arguments
                 prefixlength=3, constantscore=True):
        super().__init__(fieldname, text, boost, maxdist, prefixlength, constantscore)


def match(query_str, idx, limit=40):
    ret_results = []

    query_words = words_get(query_str)
    if len(query_words) == 0:
        return ret_results

    with idx.searcher() as searcher:
        rome_facet = sorting.FieldFacet('rome')

        # Strict search, with forced correction
        parser = QueryParser('label', idx.schema)
        query = parser.parse(f'{query_str}')
        cor = searcher.correct_query(query, query_str)
        results = searcher.search(cor.query, limit=20, collapse=rome_facet)

        # Word-joker search
        parser = QueryParser('label', idx.schema)
        query = parser.parse(f'{query_str}*')
        results_partial = searcher.search(query, limit=20, collapse=rome_facet)
        results.upgrade_and_extend(results_partial)

        # Fuzzy search
        parser = QueryParser('label', idx.schema, termclass=CustomFuzzyTerm)
        parser.add_plugin(FuzzyTermPlugin())

        shortword = re.compile(r'\W*\b\w{1,3}\b')
        query_prep = shortword.sub('', query_str)
        query = parser.parse(query_prep)
        results_fuzzy = searcher.search(query, limit=limit, collapse=rome_facet)

        results.upgrade_and_extend(results_fuzzy)
        for res in results:
            ret_results.append({
                'id': res['rome'],
                'label': res['label'],
                'value': res['label'],
                'occupation': res['slug'],
                'source': res['source'],
                'score': res.score
            })

    return sorted(ret_results, key=lambda e: e['score'], reverse=True)
