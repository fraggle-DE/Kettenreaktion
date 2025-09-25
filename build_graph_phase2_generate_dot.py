#!/usr/local/bin/python3

from collections import defaultdict
import pickle
import argparse
import datetime

#### no user servicable parts below ####

# Linksammlung:

# https://eviltester.github.io/graphviz-steps/edit-anim.html - hierfuer sind die STEP/END-Marker gedacht. Kann nur dot, keinen anderen Algorithmus
# https://sketchviz.com/new - sieht klasse aus
# https://dot-to-ascii.ggerganov.com/ - dafuer sind wir hier schon mit zu vielen Boxen und Pfeilen unterwegs; das wird unuebersichtlich.
# https://dreampuf.github.io/GraphvizOnline/ - zum schnellen Spielen, kann auch neato usw. und auch verschiedene Ausgabeformate
# https://edotor.net/ - zum schnellen Spielen, kann auch neato usw.

parser = argparse.ArgumentParser(description='Generate input files for Graphviz')
parser.add_argument('--show_founds_in_label','-f', action='store_true')
parser.add_argument('--do_it_quick','-q', action='store_true')
parser.add_argument('--report_questionable_logs','-r', action='store_true')
parser.add_argument('--prepare_movie','-m', action='store_true')
parser.add_argument('--write_graph','-w', action='store_true')
parser.add_argument('--components_color','-c', action='store_true')
parser.add_argument('--debug_level','-d', type=int, default=0)
args = parser.parse_args()

debug_level = args.debug_level

node_defaults = 'fontsize="20" style="filled,rounded"'

cache_types = [
  "Traditional",
  "Multi",
  "Mystery",
  "Other",
  "Webcam",
  "Virtual",
  "Safari",
]

# https://colorpicker.imageonline.co/
    
fillcolor_by_cache_type = {
  "Traditional" : "#469b37",
  "Multi"       : "#f48839",
  "Mystery"     : "#2a8fd2",
  "Other"       : "#30a4a8",
  "Webcam"      : "#A160D0",
  "Virtual"     : "#ec66cd",
  "Safari"      : "#ec66cd",
}

color_by_status = {
  "Available"               : "#000000",
  "Archived"                : "#ff0000",
  "Temporarily unavailable" : "orange"
}

default_shape = "box"
shape_by_cache_type = {
  "Traditional" : default_shape,
  "Multi"       : default_shape,
  "Mystery"     : default_shape,
  "Other"       : default_shape,
  "Webcam"      : default_shape,
  "Virtual"     : default_shape,
  "Safari"      : "ellipse",
  "BigBang"     : "diamond"
}

special_penwidth = 5

big_bang_cache_code='OC423D' # mic@s Urknall

Reverse_Cache_attr = 'A72' # das Safari-Attribut, aus einem Request auf OKAPI_BASE_URL/attrs/attribute_index

cache_info_by_cache_code = {}
cache_codes_by_year = defaultdict(list) # OK
cache_codes_by_uuid = defaultdict(list) # OK
uuid_by_cache_code = defaultdict(str) # OK
year_hidden_by_cache_code = defaultdict(int) # OK
year_archived_by_cache_code = defaultdict(int) # OK
log_year_by_searcher_uuid_and_cache_code = defaultdict(lambda : defaultdict(int)) # OK
oldest_cache_code_by_searcher_uuid = defaultdict(str) # OK
oldest_logdate_by_searcher_uuid = defaultdict(str) # OK
improperly_logged_caches_by_searcher_username = defaultdict(list) # OK
logged_as_note_caches_by_searcher_username = defaultdict(list) # OK

timestamp = datetime.datetime.utcnow().isoformat()
#today = datetime.datetime.utcnow().strftime("%Y-%m-%d")

def year_from_timestamp(t):
  return int(t[0:4])    

with open('kettenreaktion_data.pickle', 'rb') as f:
    # The protocol version used is detected automatically, so we do not
    # have to specify it.
    [cache_info_by_cache_code, today] = pickle.load(f)

all_kettenreaktion_caches = list(cache_info_by_cache_code.keys())
print("INFO: Number of cache codes (OC...):", len(all_kettenreaktion_caches))
if args.do_it_quick:
  all_kettenreaktion_caches = all_kettenreaktion_caches[0:10]

# Nun allerlei Infos besorgen:
# Zeitraum, Liste der Owner

year_min = 9999
year_max = 0
i=0
for cache_code in all_kettenreaktion_caches:
  # Fortschrittsbalken:
  i+=1
  if debug_level <= 1:
    if i % 10 == 0:
      print(i, end='', flush=True)
    else:
      print('.', end='', flush=True)

  # Wir fieseln auch gleich das Jahr der Veroeffentlichung heraus und merken uns
  # - aeltestes und juengstes Jahr
  # - pro Jahr die gelegten Caches
  year_hidden = year_from_timestamp(cache_info_by_cache_code[cache_code]['date_hidden'])
  year_hidden_by_cache_code[cache_code] = year_hidden
  cache_codes_by_year[year_hidden].append(cache_code)

  year_min = min(year_min, year_hidden)
  year_max = max(year_max, year_hidden)

  # Wir fieseln weiterhin heraus, welchen Ownern welche Caches
  # gehoeren (das kann mehr als einer sein! mica@ + TeamMB!), als
  # Nebenprodukt erhalten wir eine Liste der Owner, die ueberhaupt
  # einen KR-Cache gelegt haben.
  
  uuid = cache_info_by_cache_code[cache_code]['owner']['uuid']
  cache_codes_by_uuid[uuid].append(cache_code)
  uuid_by_cache_code[cache_code] = uuid

# Ende der ersten Schleife ueber alle cache_codes

# Abschluss des Fortschrittbalkens
if debug_level <= 1:
  print()

if debug_level > 1:
  print("INFO: Die Owner-UUIDs sortiert:")
  owner_uuids = sorted(cache_codes_by_uuid.keys())
  print("\n".join(owner_uuids))
  

# In einer zweiten Schleife suchen wir nun heraus, welche KR-Owner
# welche KR-Caches gefunden haben, ferner, welcher Fund der aelteste
# fuer den Owner in seiner Funktion als Sucher ist. Schliesslich
# suchen wir fuer schon archivierte Caches das Jahr des Archiv-Logs heraus:

for cache_code in all_kettenreaktion_caches:
  if debug_level > 0:
    print(f"INFO: cache_code = {cache_code}")
  latest_logs = cache_info_by_cache_code[cache_code]['latest_logs']
  status = cache_info_by_cache_code[cache_code]['status']
  for log_entry in latest_logs:
    date = log_entry['date']
    year = year_from_timestamp(date)
    searcher_uuid = log_entry['user']['uuid']
    searcher_username = log_entry['user']['username']
    if log_entry['type'] == 'Found it':
      if searcher_uuid in cache_codes_by_uuid:
        # Hier muessen wir uns nur das Jahr merken (aber: Mehrfachfunde?!?)
        log_year_by_searcher_uuid_and_cache_code[searcher_uuid][cache_code] = year
        if searcher_uuid in oldest_logdate_by_searcher_uuid:
          if date < oldest_logdate_by_searcher_uuid[searcher_uuid]:
            # Hier nehmen wir aber den kompletten Zeitstempel:
            oldest_logdate_by_searcher_uuid[searcher_uuid] = date
            oldest_cache_code_by_searcher_uuid[searcher_uuid] = cache_code
        else:
          oldest_logdate_by_searcher_uuid[searcher_uuid] = date
          oldest_cache_code_by_searcher_uuid[searcher_uuid] = cache_code
      else:
        # Boese Buben:
        improperly_logged_caches_by_searcher_username[searcher_username].append(cache_code)
    elif log_entry['type'] == 'Comment':
      if searcher_uuid not in cache_codes_by_uuid:
         logged_as_note_caches_by_searcher_username[searcher_username].append(cache_code)
#         print(f"INFO: {status} KR cache {cache_code} logged with comment by {searcher_username} not (yet) being a KR cache owner.")
    elif log_entry['type'] == 'Archived' and status == 'Archived':
      year_archived_by_cache_code[cache_code] = year

  # Es gibt einige Caches, die jetzt archiviert sind, die aber
  # keinen 'Archived'-Logeintrag besitzen (warum auch immer). Fuer
  # diese nehmen wir stattdessen das Jahr der letzten Aenderung:
    
  if status == 'Archived' and cache_code not in year_archived_by_cache_code:
#    print(f"INFO: {cache_code} is archived, but I didn't find a matching log entry")
    year_archived_by_cache_code[cache_code] = year_from_timestamp(cache_info_by_cache_code[cache_code]['last_modified'])

# Ende der zweiten Schleife ueber alle cache_codes
    
if debug_level > 1:
  print("INFO: Die Searcher-UUIDs sortiert:")
  searcher_uuids = sorted(log_year_by_searcher_uuid_and_cache_code.keys())
  print("\n".join(searcher_uuids))

  
# Wir haben die Datenbasis beisammen, nun koennen wir 2 Plots, also 2
# dot-Dateien anfertigen:

# Fuer die Verwendung in
# https://eviltester.github.io/graphviz-steps/edit-anim.html ist es
# entscheidend, die Zeilen in der dot-datei in der richtigen
# Reihenfolge hinzuschreiben, naemlich gebuendelt pro STEP, in unserem
# Fall also pro Jahr. Also schreiben wir nicht einfach in die Datei,
# sondern in einen nach Jahreszahlen organisierten Buffer. - Wenn aber
# gar kein Movie angefertigt werden soll, ignorieren wir die
# Jahresangabe.

def add_node_to_write_buffer(year, cache_code, label, tooltip, url, color, fillcolor, shape):
  if not args.prepare_movie:
    year = 0
  penwidth = 1
  if color != color_by_status['Available']:
    penwidth = special_penwidth
  write_buffer[year].append(f'  "{cache_code}" [ color="{color}" penwidth="{penwidth}" fillcolor="{fillcolor}" URL="{url}" shape="{shape}" label="{label}" tooltip="{tooltip}" ] ;\n')

def write_legend1(f, digraph_or_subgraph):
      # Wenn wir keine Animation vorbereiten, dann gibt's noch eine
      # Legende dazu.  Das ist aber nicht wirklich schoen zu machen in
      # Graphviz, weil man nicht vernuenftig steuern kann, wohin die
      # Legende kommt. Zum Glueck legt Graphviz den subgraph von
      # selbst an den oberen Rand.

###      # Um die Legenden-Box an den rechten
###      # Rand zu bekommen, fuege ich eine unsichtbare dummy-Box ein,
###      # deren Breite aber nicht automatisch ermittelt/gesetzt werden
###      # kann, vielmehr mu"s die (optimale) Breite durch Ausprobieren
###      # ermittelt werden.
###            
###      if oldest_logs_only:
###        width = 17.2
###      else:
###        width = 23.5
###      f.write('''
###  # Abstandhalter zur Legende:
###  dummy [ width="%f" style="invis" ] ;
###''' % width)
      f.write('''
  # Legende:
  %s "cluster_legend_outer" {
      ranksep=0.3 ;
''' % (digraph_or_subgraph) )
      if digraph_or_subgraph == 'subgraph':
        f.write('''
    graph [ style="invis" margin="30.0" ] ;
''')
      f.write('''
    subgraph "cluster_legend_inner" {
      graph [ style="rounded" margin="10.0"  ] ;
      edge [ style="invis" ] ;
      node [ %s width="1.6" ] ;
''' % (node_defaults) )

      f.write('''
      "Legend"      [ label="Legend"      fillcolor="white" shape="none" fontsize="24" style="invis"] ;
      "Start"       [ label="Start"       fillcolor="white" shape="%s" URL="https://www.opencaching.de/viewcache.php?wp=OC423D" ] ;
      "Archived"    [ label="Archived"    fillcolor="white" color="%s" penwidth="%d" shape="box" ] ;
      "Unavailable" [ label="Unavailable" fillcolor="white" color="%s" penwidth="%d" shape="box" ] ;
''' % (shape_by_cache_type["BigBang"],
       color_by_status["Archived"],
       special_penwidth,
       color_by_status["Temporarily unavailable"],
       special_penwidth
      ))

      for cache_type in cache_types:
        URL = 'https://www.opencaching.de/articles.php?page=cacheinfo'
        if cache_type == "Safari":
          URL = 'https://www.opencaching.de/articles.php?page=cacheinfo#attr61'
        f.write('      "%s" [ label="%s" fillcolor="%s" shape="%s" URL="%s" ] ;\n' % (cache_type, cache_type, fillcolor_by_cache_type[cache_type], shape_by_cache_type[cache_type], URL))

      f.write('''
      "Legend" -> "Start" ;
      "Start" -> "Archived" ;
      "Archived" -> "Unavailable" ;
      "Unavailable" -> "Traditional" ;

      "top" [ style="invis" ] ;
      "bottom" [ style="invis" ] ;
      "top" -> "bottom" [ style="invis" ] ;
      {rank="same" ; "Unavailable" ; "top" }
      {rank="same" ; "Other" ; "bottom" }
''')

      # Ohne diesen Pfeil kommt dot gelegentlich auf die Idee, die
      # Legenden-Boxen links von den unsichtbaren Abstandhalter-Boxen
      # zu malen, was die Legende voellig kaputt macht.
      
      f.write('''
      "top" -> "Unavailable" ;
''')

      for i in range(len(cache_types)-1):
        f.write('      "%s" -> "%s" ;\n' % (cache_types[i], cache_types[i+1]))
      f.write('''    }
  }
  # Ende der Legende
''')


def write_legend2(f):
      f.write('''
digraph arrow {
  graph [ ranksep="2"]
      "top" [ style="invis" ]
      "bottom" [ style="invis" ]
      "top" -> "bottom" [ label="  has\n  been\n  found\n   by" fontsize="24" style="solid" ] ;
}
''')  

def write_legend3(f):
      f.write('''
digraph title {
      "Legend"      [ label="Legend"      fillcolor="white" shape="none" fontsize="24" ] ;
}
''')  

def write_legend4(f):
      f.write('''
digraph date {
      "date"      [ label="status:\n%s"      fillcolor="white" shape="none" fontsize="15" ] ;
}
''' % today)
#''' % "2024-04-20")

for oldest_logs_only in [False, True]:

  if oldest_logs_only:
    filename_dot = 'kr_oldest_logs.dot'
    filename_py = 'kr_oldest_logs.txt'
  else:
    filename_dot = 'kr_all_logs.dot'
    filename_py = 'kr_all_logs.txt'

  write_buffer = defaultdict(list)
  py_edges_buffer = []
  neo4j_edges_buffer = []

  # Die Zeitleiste, nur die nackten Jahreszahlen und Striche (keine Pfeile)
  # dazwischen:

  for year in range(year_min, year_max+1):
    write_buffer[year].append(f'  "{year}" [ fontsize="24" shape="plaintext" style="" ] ;\n')
  for year in range(year_min, year_max):
    year2 = year+1
    write_buffer[year2].append(f'  "{year}" -> "{year2}" [ dir="none" ] ;\n')

  # Fuer jeden Cache einen Node, i.d.R. eine Box: (Diese Schleife k"oente man
  # sogar anders bauen, denn wir haben schon ermittelt, zu welchem Jahr welche
  # Caches gehoeren. Egal.)
  
  id = 0 # Fuer graphframes brauchen wir eine numerische id
  for cache_code in all_kettenreaktion_caches:
    cache_info_by_cache_code[cache_code]['id'] = id
    id += 1
    name = cache_info_by_cache_code[cache_code]['name']
    owner = cache_info_by_cache_code[cache_code]['owner']['username']
    url = cache_info_by_cache_code[cache_code]['url']
    date_hidden = cache_info_by_cache_code[cache_code]['date_hidden']
    cache_type = cache_info_by_cache_code[cache_code]['type']
    status = cache_info_by_cache_code[cache_code]['status']
    founds = cache_info_by_cache_code[cache_code]['founds']
#    location = cache_info_by_cache_code[cache_code]['location']
#    lat, lon = location.split('|')
#    lat = float(lat)*10.0
#    lon = float(lon)*10.0
#    print(lat, lon)
#    location = "%f,%f" % (lat, lon)
    if founds == 1:
      founds_str = "1 found"
    else:
      founds_str = ("%s" % founds) + " founds"

    tooltip = "\\n".join([cache_code, name, date_hidden[0:10], cache_type, status, founds_str])

    # Die Hintergrundfarbe des Node ermitteln:
    fillcolor = 'white' # sollte in jedem Falle ueberschrieben werden

    # Diese Fallunterscheidung muss ggf. erweitert werden, z.B. wenn
    # der erste Event-KR-Cache daherkommt. Die Farben sind die
    # RGB-Werte aus den Original-Icons.

    if cache_type == 'Quiz':
      cache_type = 'Mystery'
    fillcolor = fillcolor_by_cache_type[cache_type]
    if fillcolor == 'white':
       print('WARNING: unknown cache type, no proper color known.')
       fillcolor = 'black'

    # Einige wenige Cache bekommen keine Box, sondern einen anderen shape
    shape = 'box'

    # Safari-Caches bekommen eine Ellipse:
    attr_acodes = cache_info_by_cache_code[cache_code]['attr_acodes']
    if Reverse_Cache_attr in attr_acodes:
      shape = shape_by_cache_type["Safari"]

    # mic@s allererster (und nur der allererste)
    # Kettenreaktionscache bekommt ein Doppel-Oktogon:
    if cache_code == big_bang_cache_code:
      shape = shape_by_cache_type["BigBang"]

    label = owner
    if args.show_founds_in_label:
      label += f"\\n{founds_str}"
    year_hidden = year_hidden_by_cache_code[cache_code]
    if status == 'Archived' and args.prepare_movie:
      year_archived = year_archived_by_cache_code[cache_code]
      add_node_to_write_buffer(year_hidden,   cache_code, label, tooltip, url, color_by_status["Available"], fillcolor, shape)
      add_node_to_write_buffer(year_archived, cache_code, label, tooltip, url, color_by_status["Archived"],  fillcolor, shape)
    else:
      if args.components_color:
        fillcolor = "white"
        if cache_code in component_color_number_by_cache_code:
          f = component_color_number_by_cache_code[cache_code]
          if f == 0:
            fillcolor = "red"
          if f == 1:
            fillcolor = "green"
          if f == 2:
            fillcolor = "blue"

        color = "black"
      else:
        color = color_by_status[status]
      add_node_to_write_buffer(year_hidden,   cache_code, label, tooltip, url, color, fillcolor, shape)
          
  # Nun die Caches in die Zeitleiste einsortieren:
  for year in range(year_min, year_max+1):
     if year in cache_codes_by_year:
       cache_codes = cache_codes_by_year[year]
       quoted_cache_codes = ' '.join([f'"{x}"' for x in cache_codes])
       write_buffer[year].append(f'  {{ rank="same" ; "{year}" {quoted_cache_codes} ; }}\n')

  # Jetzt koennen wir fuer jeden KR-Cache den Owner ermitteln und
  # nachsehen, welche anderen KR-Caches dieser Owner gefunden hat
  # - fuer jeden Fund gibt es einen Pfeil (mit genau einer
  # Ausnahme):
      
  number_of_found_logs = 0
  owner_uuids_done = []
  for cache_code in all_kettenreaktion_caches:
    if debug_level > 1:
      print(f"INFO: cache_code = {cache_code}")
    owner_uuid = uuid_by_cache_code[cache_code]
    # Jeder Owner kommt aber nur einmal dran:
    if (owner_uuid not in owner_uuids_done) or oldest_logs_only:
      owner_uuids_done.append(owner_uuid)
      if oldest_logs_only:
        if owner_uuid in oldest_cache_code_by_searcher_uuid:
          found_cache_codes = [ oldest_cache_code_by_searcher_uuid[owner_uuid] ]
        else:
          found_cache_codes = []
      else:
        if owner_uuid in log_year_by_searcher_uuid_and_cache_code:
          found_cache_codes = list(log_year_by_searcher_uuid_and_cache_code[owner_uuid].keys())
        else:
          found_cache_codes = []
      
      for found_cache_code in found_cache_codes:
        if debug_level > 1:
          print(f"INFO: found_cache_code = {found_cache_code}")
  
        # Die Ausnahme: Wenn nur die aeltesten Logs gezeigt werden,
        # so wird der aelteste Fund von mic@ (als Owner von
        # big_bang_cache_code=OC423D) unterdrueckt, denn der ergaebe
        # einen in die Vergangenheit statt in die Zukunft weisenden
        # Pfeil.
  
        if not ( oldest_logs_only and cache_code == big_bang_cache_code ):
          year = max(year_hidden_by_cache_code[found_cache_code], year_hidden_by_cache_code[cache_code])
          if not oldest_logs_only:
  
            # In diesem Modus sollen Fund-Pfeile erst im Jahr des Fundes
            # auftreten, also muss das Fund-Jahr auch in die
            # Maximumsberechnung eingehen:
  
            searcher_uuid = uuid_by_cache_code[cache_code]
            year = max(year, log_year_by_searcher_uuid_and_cache_code[searcher_uuid][found_cache_code])
          write_buffer[year].append(f'  "{found_cache_code}" -> "{cache_code}" ;\n')
          cache_code_id = cache_info_by_cache_code[cache_code]['id']
          found_cache_code_id = cache_info_by_cache_code[found_cache_code]['id']
          py_edges_buffer.append(f'      ({found_cache_code_id}, {cache_code_id}, "any", 1.0),')
          neo4j_edges_buffer.append(f'CREATE( {found_cache_code} )-[:wasfoundby]->( {cache_code} )')
          number_of_found_logs += 1
  print("STATS: number of found-logs = number of arrows = ", number_of_found_logs)

  SPLINES='splines=compound'
  SPLINES=''
  if debug_level > 1:
    print(f"INFO: Writing now {filename_dot} and {filename_py}")
  with open(filename_dot, 'w') as f:
    with open(filename_py, 'w') as p:
      # Header:
      f.write("digraph Kettenreaktionen {\n")
      f.write(f"  # generated {timestamp}\n")
      if args.prepare_movie:
        f.write(f"  # https://eviltester.github.io/graphviz-steps/edit-anim.html\n")
      f.write(f"  {SPLINES}\n")
      f.write(f"  node [ {node_defaults} ] ;\n")

      # Body:
      for year in write_buffer.keys():
        f.write("\n")
        if args.prepare_movie:
          f.write(f"  # STEP {year}\n")
        f.write(''.join(write_buffer[year]))
        f.write("\n")
      
      # Footer:
      if args.prepare_movie:
        f.write("  # END\n")
  #    else:
  #      write_legend1(f, 'subgraph')
      f.write('}\n')
      f.close()

      p.write('  v = spark.createDataFrame([\n')
      for cache_code in all_kettenreaktion_caches:
        id = cache_info_by_cache_code[cache_code]['id']
        owner = cache_info_by_cache_code[cache_code]['owner']['username']
        p.write(f'        ({id}, "{cache_code}", "{owner}"),\n')
#        p.write(f'CREATE( {cache_code}:cache {{name: "{owner}"}} )\n')
      p.write('      ], ["id", "cache_code", "owner"])\n')
      p.write('  e = spark.createDataFrame([\n')
      for edge in py_edges_buffer:
        p.write(f'  {edge}\n')
#      for edge in neo4j_edges_buffer:
#        p.write(f'{edge}\n')
      p.write('      ], ["src", "dst", "relationship", "weight" ])\n')
      p.close()

filename = 'legend1.dot'
with open(filename, 'w') as f:
  write_legend1(f, 'digraph')
  f.close()

filename = 'legend2.dot'
with open(filename, 'w') as f:
  write_legend2(f)
  f.close()

filename = 'legend3.dot'
with open(filename, 'w') as f:
  write_legend3(f)
  f.close()

  filename = 'legend4.dot'
with open(filename, 'w') as f:
  write_legend4(f)
  f.close()


if args.report_questionable_logs:
  filename = "report_%s.txt" % timestamp
  n_warning = 0
  n_info = 0
  with open(filename, 'w') as f:
    f.write("INFO: generated %s\n" % timestamp)
    improper_finders = sorted(improperly_logged_caches_by_searcher_username.keys())
    for username in improper_finders:
      found_cache_codes = sorted(list(set(improperly_logged_caches_by_searcher_username[username])))
      found_cache_codes_str = ', '.join(found_cache_codes)
      n_warning += 1
      f.write("WARNING: %-16s logged %-7s as found without being a KR cache owner.\n" % (username, found_cache_codes_str))
    
    note_finders = sorted(logged_as_note_caches_by_searcher_username.keys())
    for username in note_finders:
      note_cache_codes = set(logged_as_note_caches_by_searcher_username[username])
      # aus diesen Caches muessen wir aber die herausfiltern, die der Finder schon als gefunden geloggt hat:
      if username in improper_finders:
        found_cache_codes = set(improperly_logged_caches_by_searcher_username[username])
        note_cache_codes = note_cache_codes.difference(found_cache_codes)
      if note_cache_codes:
        note_cache_codes_str = ', '.join(sorted(list(note_cache_codes)))
        n_info += 1
        f.write("INFO: %-16s logged %-7s with a note without being a KR cache owner.\n" % (username, note_cache_codes_str))
    f.write("STATS: %2d users created warnings.\n" % n_warning)
    f.write("STATS: %2d users created infos.\n" % n_info)
    f.close()

if args.prepare_movie:
  print("INFO: You may now visit https://eviltester.github.io/graphviz-steps/edit-anim.html and visualize the *.dot files there.")
print("INFO: This is the end.")
exit()
