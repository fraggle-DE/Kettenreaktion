#!/usr/local/bin/python3

import requests
import pickle
import argparse
import os
import datetime

OKAPI_CONSUMER_KEY=os.getenv('OKAPI_CONSUMER_KEY')
if OKAPI_CONSUMER_KEY == None or OKAPI_CONSUMER_KEY == '':
    print("FATAL: Please set the environment variable OKAPI_CONSUMER_KEY!")
    exit(1)

#### no user servicable parts below ####

today = datetime.datetime.utcnow().strftime("%Y-%m-%d")

parser = argparse.ArgumentParser(description='Generate input files for Graphviz')
parser.add_argument('--count_only','-c', action='store_true')
parser.add_argument('--do_it_quick','-q', action='store_true')
parser.add_argument('--debug_level','-d', type=int, default=0)
args = parser.parse_args()

debug_level = args.debug_level


OKAPI_BASE_URL='https://www.opencaching.de/okapi/services' # MIT 'www.' am Anfang!

cache_info_by_cache_code = {}

print("INFO: Retrieving list of all KR caches (including unavailable and archived ones, but excluding locked ones).")
NAME_PATTERN='*Kettenreaktion*'

# Leider kann man nicht explizit auch nach 'Locked" Caches suchen:
ALL_STATUSES='Available|Temporarily unavailable|Archived'

url = f"{OKAPI_BASE_URL}/caches/search/all?name={NAME_PATTERN}&status={ALL_STATUSES}&consumer_key={OKAPI_CONSUMER_KEY}"
if debug_level > 0:
  print("INFO: url =", url)
try:
  response = requests.get(url)

  if response.status_code == 200:
    res = response.json()
  else:
    print(f"Error: {response.status_code} - {response.text}")
except requests.exceptions.RequestException as e:
  print(f"Request error: {e}")
  exit()
if debug_level > 0:
  print(f"INFO: result of {url}")
  print(response.text)

all_kettenreaktion_caches = res['results']

if args.do_it_quick:
  print("INFO: Dropping most of the cache codes.")
  all_kettenreaktion_caches = all_kettenreaktion_caches[0:7]
print("INFO: Number of cache codes (OC...) found:", len(all_kettenreaktion_caches))
if args.count_only:
  exit(0)

print("INFO: Retrieving detailed info about each cache...")

# Nun fuer jeden KR-Cache allerlei Infos besorgen.  In jedem
# Schleifendurchlauf wird ein HTTP-Request abgesetzt. Das koennte man
# dahingehend optimieren, dass man statt vieler API-Calls auf
# '.../cache' wenige (oder sogar nur einen) Call auf '.../caches'
# absetzt. Das lohnt sich momentan aber gar nicht, bei nur 50
# KR-Caches.

i=0
for cache_code in all_kettenreaktion_caches:
  # Fortschrittsbalken:
  i+=1
  if debug_level <= 1:
    if i % 10 == 0:
      print(i, end='', flush=True)
    else:
      print('.', end='', flush=True)
  fields='name|type|status|owner|date_created|date_hidden|last_modified|latest_logs|url|founds|attr_acodes|location'
  log_fields='date|type|user' # die Comments brauchen wir nicht, die machen aber die Mehrheit der Datenmenge aus -> wegrationalisiert
  lpc='all' # mit allen Logs - das koennte vielleicht irgendwann mal schief gehen
  url = f"{OKAPI_BASE_URL}/caches/geocache?cache_code={cache_code}&fields={fields}&lpc={lpc}&log_fields={log_fields}&consumer_key={OKAPI_CONSUMER_KEY}"
  if debug_level > 2:
    print("INFO: url =", url)
  try:
    response = requests.get(url)

    if response.status_code == 200:
      res = response.json()
    else:
      print(f"Error: {response.status_code} - {response.text}")
  except requests.exceptions.RequestException as e:
    print(f"Request error: {e}")
    exit()
  if debug_level == 2:
    print(f"INFO: {cache_code} {res['name']}")
  if debug_level > 2:
    print(f"INFO: result of {url}")
    print(response.text)
  cache_info_by_cache_code[cache_code] = res

# Abschluss des Fortschrittbalkens
if debug_level <= 1:
  print()

with open('kettenreaktion_data.pickle', 'wb') as f:
  pickle.dump([cache_info_by_cache_code, today], f, pickle.HIGHEST_PROTOCOL)
print("INFO: This is the end of phase 1.")
exit()
