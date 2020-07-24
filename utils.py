import time
import random
import hashlib

def randSleep(min_sec=2, max_sec=5):
  return time.sleep(random.uniform(min_sec, max_sec))

def generateHash(arxiv_id):
  """ Create your own server_uuid
  @param input_string (str): information to be encoded as server_uuid
  @returns server_uuid (str): your unique server_uuid
  """
  s = hashlib.sha256()
  data = arxiv_id.encode("utf-8")
  s.update(data)
  sha_str = s.hexdigest()
  return sha_str
