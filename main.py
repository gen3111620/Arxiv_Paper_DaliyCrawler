import ast
import sys
import time
import sqlite3
import logging
import schedule
import configparser

from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

from sqldb import Sqlite
from es_use import ElasticUtils
from crawl_daily import ArxivDaliyCrawler
from elasticsearch import Elasticsearch as ES



logger = logging.getLogger()
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(module)s - %(message)s'))
logger.addHandler(console_handler)

file_handler = TimedRotatingFileHandler('./logs/log.log', when="midnight", interval=1, encoding='utf-8', backupCount=30)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(module)s - %(message)s'))
logger.addHandler(file_handler)




def main(ES_HOST, ES_PORT, ES_INDEX, ES_DOC_TYPE, CRAWL_CATEGORY, CRAWL_MIN_SLEEP, CRAWL_MAX_SLEEP):

  try:
    logger.info('start crawl job.')
    logger.info(f'crawl category : {CRAWL_CATEGORY}')

    es = ElasticUtils(ES_HOST, ES_PORT, ES_INDEX, ES_DOC_TYPE)
    sql = Sqlite('arxiv_id_records.db', TABLE_NAME='arxiv_record')

    
    crawler = ArxivDaliyCrawler(CRAWL_CATEGORY, CRAWL_MIN_SLEEP, CRAWL_MAX_SLEEP)
    
    arxiv_ids = set(crawler.crawlDaliyURL())
    print(arxiv_ids)
    print(len(arxiv_ids))

    for arxiv_id in arxiv_ids:
      if sql.select(arxiv_id) is None:
        paper_info = crawler.crawlPaperInfo(arxiv_id)
        es.insert(_id=paper_info['paper_link'], create_data=paper_info)
        sql.insert(arxiv_id)


    logger.info('crawl job is done.')

  except Exception as e:
    logger.error(e)
  
if __name__ == '__main__':


  config = configparser.ConfigParser()
  config.read("config.ini")

  ES_HOST = config.get("es", "es_host")
  ES_PORT = config.get("es", "es_port")
  ES_INDEX = config.get("es", "es_index")
  ES_DOC_TYPE = config.get("es", "doc_type")

  CRAWL_CATEGORY = ast.literal_eval(config.get("crawl_setting", "crawl_category"))
  CRAWL_MIN_SLEEP = config.getint("crawl_setting", "min_sleep")
  CRAWL_MAX_SLEEP = config.getint("crawl_setting", "max_sleep")
  SCHEDULE_TIME = config.getint("schedule", "schedule_time")

  # waiting for es build.
  while True:
    es = ElasticUtils(ES_HOST, ES_PORT, ES_INDEX, ES_DOC_TYPE)
    if es:
      break

  main(ES_HOST, ES_PORT, ES_INDEX, ES_DOC_TYPE,
       CRAWL_CATEGORY, CRAWL_MIN_SLEEP, CRAWL_MAX_SLEEP)

  schedule.every(SCHEDULE_TIME).seconds.do(
      main, ES_HOST, ES_PORT, ES_INDEX, ES_DOC_TYPE,
       CRAWL_CATEGORY, CRAWL_MIN_SLEEP, CRAWL_MAX_SLEEP)

  while True:
    schedule.run_pending()
    time.sleep(1)


  


