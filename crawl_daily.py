import re
import time
import random
import logging
import requests
from datetime import datetime
from bs4 import BeautifulSoup as BS

from utils import randSleep
# No such archive 'qa' exists, see the list of archives.


logger = logging.getLogger()

class ArxivDaliyCrawler:
  def __init__(self, arxiv_category, min_sleep_sec=1, max_sleep_sec=5):
    self.arxiv_category = arxiv_category
    self.min_sleep_sec = min_sleep_sec
    self.max_sleep_sec = max_sleep_sec
  
    self.headers = {
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Accept-Encoding': 'gzip, deflate',
      'Accept-Language': 'en-US,en;q=0.5',
      'Cache-Control': 'max-age=0',
      'Content-Type': 'application/x-www-form-urlencoded'
    }

  def _getWeeklyPage(self, soup):

    try:
      page = re.sub('\d+-', '', soup.find('small').find_all('a')[-1].text)

    except Exception as e:
      logger.error(e)
      return None

    return page

  def _getWeeklyURL(self, url):
    r = requests.get(url, headers=self.headers, timeout=10)
    soup = BS(r.text, 'html.parser')

    paper_urls = [re.sub(r'/abs/', '', paper_id_soup.find('a').get('href')) for paper_id_soup in soup.find_all('span', {'class', 'list-identifier'})]
    return paper_urls


  def crawlDaliyURL(self):

    # crawl_results = dict()
    crawl_results = []

    for category in self.arxiv_category:

      try:
        logger.info(f"Start crawl {category} daliy submitted paper.")
        logger.info(f"{len(set(crawl_results))}")
        url = f"https://arxiv.org/list/{category}/recent/"

        r = requests.get(url, headers=self.headers, timeout=10)
        soup = BS(r.text, 'html.parser')
        weekly_page = self._getWeeklyPage(soup)

        if weekly_page:

          url = f"https://arxiv.org/list/{category}/pastweek?show={weekly_page}"
          # crawl_results[category] = self._getWeeklyURL(url)
          crawl_results.extend(self._getWeeklyURL(url))

        else:
          # crawl_results[category] = self._getWeeklyURL(url)
          crawl_results.extend(self._getWeeklyURL(url))

        randSleep(self.min_sleep_sec, self.max_sleep_sec)

      except Exception as e:
        logger.error(f'crawlDaliyURL error :  {e}')
        return crawl_results

    return crawl_results

  def _getPaperTitle(self, soup):
    try:
      return soup.find('h1', {'class': 'title mathjax'}).text.split('Title:')[1]
    except Exception as e:
      logger.error(f'_getPaperTitle error :  {e}')

  def _getPaperAuthors(self, soup):

    try:

      authors = {
        'author_name': [],
        'author_url': []
      }
      for author in soup.find('div', 'authors').find_all('a'):

        # authors[author.text] = author.get('href')
        authors['author_name'].append(author.text)
        authors['author_url'].append(author.get('href'))

      return authors

    except Exception as e:
      logger.error(f'_getPaperAuthors error :  {e}')
      return None

  def _getPaperAbstract(self, soup):

    try:
      return re.sub(r'Abstract:  ', '', soup.find('blockquote', {'class': 'abstract mathjax'}).text)
    except Exception as e:
      logger.error(f'_getPaperAbstract error :  {e}')
      return None

  def _getPaperSubjects(self, soup):

    try:
      subjects = soup.find('td', 'tablecell subjects').text.replace('\n', '').split('; ')
      return subjects

    except Exception as e:
      logger.error(f'_getPaperSubjects error :  {e}')
      return None

  def _getPaperTags(self, subjects):

    try:
      tags = [re.search(r'(?<=\().*(?=\))', subject).group() for subject in subjects]
      return tags
      
    except Exception as e:
      logger.error(f'_getPaperTags error :  {e}')
      return None

  def _getPaperSubmission(self, soup):

    try:
      submissions_date = []
      submission = soup.find('div', {'class':'submission-history'})
      subs = re.search(r'(?<=\[v\d\]).* (?=\(\d+,{0,}\d{0,} KB\))', submission.text.replace('\n', '')).group()


      for sub_date in re.split(r'\(\d+,{0,}\d+ KB\){1,}', subs):
          sub_date = re.sub('(\[v\d+\])|(UTC)', '', sub_date)
          sub_date = datetime.strptime(sub_date.lstrip().rstrip(), "%a, %d %b %Y %H:%M:%S")
          submissions_date.append(sub_date)
      return submissions_date
      
    except Exception as e:
      logger.error(f'_getPaperSubmission error :  {e}')
      return None

  def _getComments(self, soup):

    try:
      comment_soup = soup.find('td', {'class':'tablecell comments mathjax'})
      if comment_soup:
        return comment_soup.text
      else:
        return None

    except Exception as e:
      logger.error(f'_getComments error :  {e}')
      return False


  def _getJournal(self, soup):

    try:
      journal_soup = soup.find('td', {'class':'tablecell jref'})
      if journal_soup:
        return journal_soup.text
      else:
        return None
        
    except Exception as e:
      logger.error(f'_getJournal error :  {e}')
      return False

  def _getDOI(self, soup):

    try:
      doi_soup = soup.find('td', {'class':'tablecell msc_classes'})
      if doi_soup:
        return doi_soup.text
      else:
        return None
        
    except Exception as e:
      logger.error(f'_getDOI error :  {e}')
      return False



  def crawlPaperInfo(self, paper_id):

    # crawl paper page detail
    paper_info = dict()

    try:
      paper_link = f'https://arxiv.org/abs/{paper_id}'
      r = requests.get(paper_link, headers=self.headers, timeout=10)
      soup = BS(r.text, 'html.parser')

      paper_info['paper_link'] = paper_link
      paper_info['title'] = self._getPaperTitle(soup)
      paper_info['authors'] = self._getPaperAuthors(soup)
      paper_info['abstract'] = self._getPaperAbstract(soup)
      paper_info['subjects'] = self._getPaperSubjects(soup)
      paper_info['tags'] = self._getPaperTags(paper_info['subjects'])
      paper_info['submission'] = self._getPaperSubmission(soup)

      paper_info['comments'] = self._getComments(soup)
      paper_info['journal'] = self._getJournal(soup)
      paper_info['doi'] = self._getDOI(soup)

      randSleep(self.min_sleep_sec, self.max_sleep_sec)

      return paper_info

    except Exception as e:
      logger.error(e)
      return None

    



