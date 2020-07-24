import re
import sqlite3
import logging


logger = logging.getLogger()


class Sqlite:

  def __init__(self, sql_db_filename, TABLE_NAME):
    '''

    '''

    self.connection = sqlite3.connect(sql_db_filename)
    self.cursor = self.connection.cursor()
    self.TABLE_NAME = TABLE_NAME
    self._checkTableExist()

  def _checkTableExist(self):

    sql_query_table = 'SELECT * FROM sqlite_master WHERE type="table" AND name="{}";'.format(self.TABLE_NAME)
    self.cursor.execute(sql_query_table)
    if self.cursor.fetchone():
        return True
    else:
        return self._createTable()

  def _createTable(self):

    sql_create_table = """

      CREATE TABLE "{}" 
      (arxiv_id VARCHAR(255) PRIMARY KEY );

    """.format(self.TABLE_NAME)
    
    self.cursor.execute(sql_create_table)
    self.connection.commit()
    logging.info("Create {} tabel".format(self.TABLE_NAME))

  
  def insert(self, arxiv_id):

    sql_insert_instruct = """

      INSERT INTO "{}" (arxiv_id) 
      VALUES (?);

    """.format(self.TABLE_NAME)

    self.cursor.execute(sql_insert_instruct, (arxiv_id, ))
    self.connection.commit()
    logger.info(f'insert {arxiv_id} to sql')
    # logging.info('{} is insert into sql'.format(otx_id))
  
  
  def select(self, arxiv_id):
    
    sql_query_instruct = """

      SELECT arxiv_id
      From "{}"  
      WHERE arxiv_id = ?

    """.format(self.TABLE_NAME)

    self.cursor = self.connection.cursor()
    self.cursor.execute(sql_query_instruct, (arxiv_id, ))

    res = self.cursor.fetchone()

    if not res:
      return None

    return True

