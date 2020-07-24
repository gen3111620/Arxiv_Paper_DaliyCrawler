import logging
from utils import generateHash
from elasticsearch import helpers
from elasticsearch import Elasticsearch as ES

logger = logging.getLogger()

class ElasticUtils():

  def __init__(self, es_host, es_port, es_index, doc_type):
    try:
      self.es = ES([{"host": es_host, "port": es_port}])
    except Exception as e:
      return False

    self._check_index_exist(es_index)
    self.index = es_index
    self.doc_type = doc_type

  def _check_index_exist(self, index):

    if not self.es.indices.exists(index=index):
      logger.info("Create {} Index".format(index))
      self.es.indices.create(index=index)

    return index


  def insert(self, _id, create_data):
    _id = generateHash(_id)
    try:
      self.es.create(index=self.index, doc_type=self.doc_type, id=_id, body=create_data)
      logger.info('{} is created into es'.format(_id))
      

    except Exception as e:
      logger.warn(e)

  def bulks(self, actions):
    '''
  
    Impelement of es bulks function

    Input:
      self : the specified es
      actions : all actionable data

    results:

      actions all data to the specified es
    
    '''
    helpers.bulk(self.es, actions)
