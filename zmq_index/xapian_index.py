# -*- coding: utf-8 -*-

import cPickle as pickle
import zlib
import xapian
import os
import sys
sys.path.append("..")
from xapian_case.xapian_backend import _database, Schema, DOCUMENT_ID_TERM_PREFIX, \
    DOCUMENT_CUSTOM_TERM_PREFIX, InvalidIndexError
from utils import log_to_stub
from consts import XAPIAN_DATA_DIR, XAPIAN_STUB_FILE_DIR
from datetime import datetime


class XapianIndex(object):
    def __init__(self, dbpath, schema_version, remote_stub):
        self.dbpath = dbpath
        self.remote_stub = remote_stub
        self.schema_version = schema_version
        self.schema = getattr(Schema, 'v%s' % schema_version)
        if schema_version == 1:
            from consts import XAPIAN_DB_FOLDER_PREFIX
            db_folder = os.path.join(XAPIAN_DB_FOLDER_PREFIX, '_%s' % dbpath)
        else:
            pid = os.getpid()
            db_folder = os.path.join(XAPIAN_DATA_DIR, '%s_%s' % (dbpath, pid))
        self.db_folder = db_folder
        self.db = _database(db_folder, writable=True)

        self.term_gen = xapian.TermGenerator()
        self.iter_keys = self.schema['origin_data_iter_keys']
        self.pre_func = self.schema.get('pre_func', {})

    def document_count(self):
        try:
            return _database(self.db_folder).get_doccount()
        except InvalidIndexError:
            return 0

    def add_or_update(self, item):
        document = xapian.Document()
        document_id = DOCUMENT_ID_TERM_PREFIX + str(item[self.schema['obj_id']])
        for field in self.schema['idx_fields']:
            self.index_field(field, document, item)

        # print item

        # origin_data跟term和value的处理方式不一样
        item = dict(filter(lambda x: x[1] is not None, [(k, self.pre_func[k](item.get(k)) if k in self.pre_func and item.get(k) else item.get(k))
                    for k in self.iter_keys]))

        # print item

        document.set_data(zlib.compress(pickle.dumps(item, pickle.HIGHEST_PROTOCOL), zlib.Z_BEST_COMPRESSION))
        document.add_term(document_id)
        if self.schema_version == 1:
            self.db.replace_document(document_id, document)
        else:
            self.db.add_document(document)

    def index_field(self, field, document, item):
        _index_field(field, document, item, self.schema_version, self.schema, self.term_gen)

    def _log_to_stub(self):
        log_to_stub(XAPIAN_STUB_FILE_DIR, self.dbpath, self.db_folder, remote_stub=self.remote_stub)

    def close(self):
        self.db.close()
        # user 不需要更新stub
        if self.schema_version != 1:
            self._log_to_stub()
        print 'total index', self.document_count()


def _marshal_value(value, pre_func=None):
    """
    Private utility method that converts Python values to a string for Xapian values.
    """
    if pre_func:
        value = pre_func(value)
    # value 默认为int, long, float
    value = xapian.sortable_serialise(value)
    return value


def _marshal_term(term, pre_func=None):
    """
    Private utility method that converts Python terms to a string for Xapian terms.
    """
    if pre_func:
        term = pre_func(term)
    if isinstance(term, (int, long)):
        term = str(term)
    return term


def _index_field(field, document, item, schema_version, schema, term_gen):
    prefix = DOCUMENT_CUSTOM_TERM_PREFIX + field['field_name'].upper()
    field_name = field['field_name']
    # 可选term在pre_func里处理
    if field_name in schema['index_item_iter_keys']:
        term = _marshal_term(item.get(field_name), schema.get('pre_func', {}).get(field_name))
        document.add_term(prefix + term)
    elif field_name == 'domain':
        for t in item.get(field_name).split(','):
            term = _marshal_term(t, schema.get('pre_func', {}).get(field_name))
            document.add_term(prefix + term)
    # 可选value在pre_func里处理
    elif field_name in schema['index_value_iter_keys']:
        value = _marshal_value(item.get(field_name), schema.get('pre_func', {}).get(field_name))
        document.add_value(field['column'], value)
    elif field_name == 'text':
        terms = item['terms']
        term_gen.set_document(document)
        term_gen.index_text_without_positions(' '.join(terms), 1, prefix)
    elif field_name == 'topics':
        terms = item['topics']
        term_gen.set_document(document)
        term_gen.index_text_without_positions(' '.join(terms), 1, prefix)
