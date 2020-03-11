import logging
import os
import re
import shutil

import pandas as pd
from slugify import slugify
from whoosh import sorting
from whoosh.analysis import CharsetFilter, StandardAnalyzer
from whoosh.fields import KEYWORD, STORED, TEXT, Schema
from whoosh.index import create_in, exists_in, open_dir
from whoosh.qparser import FuzzyTermPlugin, QueryParser
from whoosh.query import FuzzyTerm
from whoosh.support.charset import accent_map

from library import words_get

logger = logging.getLogger(__name__)


def init_state(force=False):
    idx = buildName('index_dir')

    if checkTable(idx) and not force:
        logger.warning('ROME Suggest database found, rebuild not forced: proceeding')
        return get_index(idx)

    logger.info('Compiling dataframe references')
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Rome
    rome_labels = pd.read_csv(f'{current_dir}/referentiels/rome_lbb.csv', sep=',', encoding="utf-8")
    rome_labels.columns = ['rome', 'rome_1', 'rome_2', 'rome_3', 'label', 'slug']
    rome_labels['source'] = 'rome'
    logging.info(f"Obtained {len(rome_labels)} ROME labels")

    # OGR
    ogr_labels = pd.read_csv(f'{current_dir}/referentiels/ogr_lbb.csv', sep=',', encoding="utf-8")
    ogr_labels.columns = ['code', 'rome_1', 'rome_2', 'rome_3', 'label', 'rome']
    ogr_labels['source'] = 'ogr'
    ogr_labels['slug'] = ogr_labels['label'].apply(lambda x: slugify(x))
    logging.info(f"Obtained {len(ogr_labels)} OGR labels")

    # ONISEP
    onisep_labels = pd.read_csv(f'{current_dir}/referentiels/metiers_onisep.csv', sep=',', encoding="utf-8")
    onisep_labels.columns = [
        'label', 'url_onisep', 'pub_name',
        'collection', 'year', 'gencod', 'gfe',
        'rome', 'rome_label', 'rome_url']
    onisep_labels['source'] = 'onisep'
    onisep_labels['slug'] = onisep_labels['label'].apply(lambda x: slugify(x))
    logging.info(f"Obtained {len(onisep_labels)} ONISEP labels")

    # Préparation et écriture des données
    rome_prep = rome_labels[['rome', 'label', 'source', 'slug']].copy()
    rome_prep['label'] = rome_prep['label'].str.lower()
    rome_prep = rome_prep.drop_duplicates(subset=['slug', 'rome'])

    ogr_prep = ogr_labels[['rome', 'label', 'source', 'slug']].copy()
    ogr_prep['label'] = ogr_prep['label'].str.lower()
    ogr_prep = ogr_prep.drop_duplicates(subset=['slug', 'rome'])

    onisep_prep = onisep_labels[['rome', 'label', 'source', 'slug']].copy()
    onisep_prep['label'] = onisep_prep['label'].str.lower()
    onisep_prep = onisep_prep.drop_duplicates(subset=['slug', 'rome'])

    createTable(idx, overwrite=True)
    writeDataframe(idx, rome_prep)
    writeDataframe(idx, ogr_prep[ogr_prep.rome.notnull()])
    writeDataframe(idx, onisep_prep[onisep_prep.rome.notnull()])
    logging.info('Suggestion index tables written')
    return get_index(idx)


def buildName(raw_name):
    return re.sub(r'[^A-Za-z0-9]+', '', raw_name)


def checkTable(idx):
    if os.path.exists(idx) and exists_in(idx):
        return True
    return False


def createTable(name, *, overwrite=False):
    analyzer = StandardAnalyzer() | CharsetFilter(accent_map)
    schema = Schema(
        label=TEXT(stored=True, analyzer=analyzer, lang='fr'),
        rome=TEXT(stored=True, sortable=True),
        source=KEYWORD(stored=True, sortable=True),
        slug=STORED
    )

    if not os.path.exists(name):
        os.mkdir(name)
    elif exists_in(name):
        if not overwrite:
            logger.critical('An index already exists in %s; overwrite flag not set; abandonning', name)
            raise RuntimeError('Index already exists')
        logger.warning('Index already found, deleting %s to start anew', name)
        shutil.rmtree(name, ignore_errors=True, onerror=None)

        os.mkdir(name)

    logger.info('Whoosh index %s ready for use', name)
    create_in(name, schema)
    return name


def writeRecord(idx, **fields):
    writer = idx.writer()
    writer.add_document(**fields)


def writeDataframe(idx_name, df):
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


def get_index(idx_name):
    return open_dir(idx_name)


class FuzzyConfig(FuzzyTerm):
    def __init__(self, fieldname, text, boost=1.0, maxdist=2, prefixlength=3, constantscore=True):
        super(FuzzyConfig, self).__init__(fieldname, text, boost, maxdist, prefixlength, constantscore)


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
        parser = QueryParser('label', idx.schema, termclass=FuzzyConfig)
        parser.add_plugin(FuzzyTermPlugin())

        shortword = re.compile(r'\W*\b\w{1,3}\b')
        query_prep = shortword.sub('', query_str)
        query = parser.parse(query_prep)
        results_fuzzy = searcher.search(query, limit=limit, collapse=rome_facet)

        results.upgrade_and_extend(results_fuzzy)
        for r in results:
            ret_results.append({
                'id': r['rome'],
                'label': r['label'],
                'value': r['label'],
                'occupation': r['slug'],
                'source': r['source'],
                'score': r.score
            })

    return sorted(ret_results, key=lambda e: e['score'], reverse=True)
