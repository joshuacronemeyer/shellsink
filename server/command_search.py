#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""Full text indexing and search, implemented in pure python.

Defines a SearchableModel subclass of db.Model that supports full text
indexing and search, based on the datastore's existing indexes.

Don't expect too much. First, there's no ranking, which is a killer drawback.
There's also no exact phrase match, substring match, boolean operators,
stemming, or other common full text search features. Finally, support for stop
words (common words that are not indexed) is currently limited to English.

To be indexed, entities must be created and saved as SearchableModel
instances, e.g.:

  class Article(search.SearchableModel):
    text = db.TextProperty()
    ...

  article = Article(text=...)
  article.save()

To search the full text index, use the SearchableModel.all() method to get an
instance of SearchableModel.Query, which subclasses db.Query. Use its search()
method to provide a search query, in addition to any other filters or sort
orders, e.g.:

  query = article.all().search('a search query').filter(...).order(...)
  for result in query:
    ...

The full text index is stored in a property named __searchable_text_index.


In general, if you just want to provide full text search, you *don't* need to
add any extra indexes to your index.yaml. However, if you want to use search()
in a query *in addition to* an ancestor, filter, or sort order, you'll need to
create an index in index.yaml with the __searchable_text_index property. For
example:

  - kind: Article
    properties:
    - name: __searchable_text_index
    - name: date
      direction: desc
    ...

Note that using SearchableModel will noticeable increase the latency of save()
operations, since it writes an index row for each indexable word. This also
means that the latency of save() will increase roughly with the size of the
properties in a given entity. Caveat hacker!
"""




import re
import string
import sys

from google.appengine.api import datastore
from google.appengine.api import datastore_errors
from google.appengine.api import datastore_types
from google.appengine.ext import db
from google.appengine.datastore import datastore_pb

class SearchableEntity(datastore.Entity):
  """A subclass of datastore.Entity that supports full text indexing.

  Automatically indexes all string and Text properties, using the datastore's
  built-in per-property indices. To search, use the SearchableQuery class and
  its Search() method.
  """
  _FULL_TEXT_INDEX_PROPERTY = '__searchable_text_index'

  _FULL_TEXT_MIN_LENGTH = 1

  _FULL_TEXT_STOP_WORDS = frozenset([])

  _word_delimiter_regex = re.compile('[' + re.escape(string.punctuation) + ']')

  def __init__(self, kind_or_entity, word_delimiter_regex=None, *args,
               **kwargs):
    """Constructor. May be called as a copy constructor.

    If kind_or_entity is a datastore.Entity, copies it into this Entity.
    datastore.Get() and Query() returns instances of datastore.Entity, so this
    is useful for converting them back to SearchableEntity so that they'll be
    indexed when they're stored back in the datastore.

    Otherwise, passes through the positional and keyword args to the
    datastore.Entity constructor.

    Args:
      kind_or_entity: string or datastore.Entity
      word_delimiter_regex: a regex matching characters that delimit words
    """
    self._word_delimiter_regex = word_delimiter_regex
    if isinstance(kind_or_entity, datastore.Entity):
      self._Entity__key = kind_or_entity._Entity__key
      self.update(kind_or_entity)
    else:
      super(SearchableEntity, self).__init__(kind_or_entity, *args, **kwargs)

  def _ToPb(self):
    """Rebuilds the full text index, then delegates to the superclass.

    Returns:
      entity_pb.Entity
    """
    if SearchableEntity._FULL_TEXT_INDEX_PROPERTY in self:
      del self[SearchableEntity._FULL_TEXT_INDEX_PROPERTY]

    index = set()
    for (name, values) in self.items():
      if not isinstance(values, list):
        values = [values]
      if (isinstance(values[0], basestring) and
          not isinstance(values[0], datastore_types.Blob)):
        for value in values:
          index.update(SearchableEntity._FullTextIndex(
              value, self._word_delimiter_regex))

    index_list = list(index)
    if index_list:
      self[SearchableEntity._FULL_TEXT_INDEX_PROPERTY] = index_list

    return super(SearchableEntity, self)._ToPb()

  @classmethod
  def _FullTextIndex(cls, text, word_delimiter_regex=None):
    """Returns a set of keywords appropriate for full text indexing.

    See SearchableQuery.Search() for details.

    Args:
      text: string

    Returns:
      set of strings
    """

    if word_delimiter_regex is None:
      word_delimiter_regex = cls._word_delimiter_regex

    if text:
      datastore_types.ValidateString(text, 'text', max_len=sys.maxint)
      text = word_delimiter_regex.sub(' ', text)
      words = text.lower().split()

      words = set(unicode(w) for w in words)

      words -= cls._FULL_TEXT_STOP_WORDS
      for word in list(words):
        if len(word) < cls._FULL_TEXT_MIN_LENGTH:
          words.remove(word)

    else:
      words = set()

    return words


class SearchableQuery(datastore.Query):
  """A subclass of datastore.Query that supports full text search.

  Only searches over entities that were created and stored using the
  SearchableEntity or SearchableModel classes.
  """

  def Search(self, search_query, word_delimiter_regex=None):
    """Add a search query. This may be combined with filters.

    Note that keywords in the search query will be silently dropped if they
    are stop words or too short, ie if they wouldn't be indexed.

    Args:
     search_query: string

    Returns:
      # this query
      SearchableQuery
    """
    datastore_types.ValidateString(search_query, 'search query')
    self._search_query = search_query
    self._word_delimiter_regex = word_delimiter_regex
    return self

  def _ToPb(self, limit=None, offset=None):
    """Adds filters for the search query, then delegates to the superclass.

    Raises BadFilterError if a filter on the index property already exists.

    Args:
      # an upper bound on the number of results returned by the query.
      limit: int
      # number of results that match the query to skip.  limit is applied
      # after the offset is fulfilled.
      offset: int

    Returns:
      datastore_pb.Query
    """
    if SearchableEntity._FULL_TEXT_INDEX_PROPERTY in self:
      raise datastore_errors.BadFilterError(
        '%s is a reserved name.' % SearchableEntity._FULL_TEXT_INDEX_PROPERTY)

    pb = super(SearchableQuery, self)._ToPb(limit=limit, offset=offset)

    if hasattr(self, '_search_query'):
      keywords = SearchableEntity._FullTextIndex(
          self._search_query, self._word_delimiter_regex)
      for keyword in keywords:
        filter = pb.add_filter()
        filter.set_op(datastore_pb.Query_Filter.EQUAL)
        prop = filter.add_property()
        prop.set_name(SearchableEntity._FULL_TEXT_INDEX_PROPERTY)
        prop.set_multiple(len(keywords) > 1)
        prop.mutable_value().set_stringvalue(unicode(keyword).encode('utf-8'))

    return pb


class SearchableMultiQuery(datastore.MultiQuery):
  """A multiquery that supports Search() by searching subqueries."""

  def Search(self, *args, **kwargs):
    """Add a search query, by trying to add it to all subqueries.

    Args:
      args: Passed to Search on each subquery.
      kwargs: Passed to Search on each subquery.

    Returns:
      self for consistency with SearchableQuery.
    """
    for q in self:
      q.Search(*args, **kwargs)
    return self


class SearchableModel(db.Model):
  """A subclass of db.Model that supports full text search and indexing.

  Automatically indexes all string-based properties. To search, use the all()
  method to get a SearchableModel.Query, then use its search() method.
  """

  class Query(db.Query):
    """A subclass of db.Query that supports full text search."""
    _search_query = None

    def search(self, search_query):
      """Adds a full text search to this query.

      Args:
        search_query, a string containing the full text search query.

      Returns:
        self
      """
      self._search_query = search_query
      return self

    def _get_query(self):
      """Wraps db.Query._get_query() and injects SearchableQuery."""
      query = db.Query._get_query(self,
                                  _query_class=SearchableQuery,
                                  _multi_query_class=SearchableMultiQuery)
      if self._search_query:
        query.Search(self._search_query)
      return query

  def _populate_internal_entity(self):
    """Wraps db.Model._populate_internal_entity() and injects
    SearchableEntity."""
    return db.Model._populate_internal_entity(self,
                                              _entity_class=SearchableEntity)

  @classmethod
  def from_entity(cls, entity):
    """Wraps db.Model.from_entity() and injects SearchableEntity."""
    if not isinstance(entity, SearchableEntity):
      entity = SearchableEntity(entity)
    return super(SearchableModel, cls).from_entity(entity)

  @classmethod
  def all(cls):
    """Returns a SearchableModel.Query for this kind."""
    return SearchableModel.Query(cls)

