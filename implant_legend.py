#!/Applications/Xcode.app/Contents/Developer/usr/bin/python3

# implantiert die zweite SVG-Datei in die rechte obere Ecke der ersten
# SVG-Datei und schreibt eine dritte SVG-Datei raus.

import svgutils.transform as st
import sys

def get_size(s):
  (w,h) = (int(s.get_size()[0].strip('pt')), int(s.get_size()[1].strip('pt')))
  return (w,h)

graph = st.fromfile(sys.argv[1])
(g_width, g_height) = get_size(graph)

legend1 = st.fromfile('legend1.svg_inter')
(l1_width, l1_height)  = get_size(legend1)
legend1 = legend1.getroot()
legend1.moveto(g_width-l1_width, 0)
graph.append(legend1)

legend2 = st.fromfile('legend2.svg_inter')
(l2_width, l2_height)  = get_size(legend2)
legend2 = legend2.getroot()
legend2.moveto(g_width-(3*l1_width/4)-(l2_width/2), (l1_height-l2_height)/2)
graph.append(legend2)

legend3 = st.fromfile('legend3.svg_inter')
(l3_width, l3_height)  = get_size(legend3)
legend3 = legend3.getroot()
legend3.moveto(g_width-(l1_width/2)-(l3_width/2), (l3_height/2))
graph.append(legend3)

legend4 = st.fromfile('legend4.svg_inter')
(l4_width, l4_height)  = get_size(legend4)
legend4 = legend4.getroot()
legend4.moveto(g_width-(3*l1_width/4)-(l4_width/2)+10, (l1_height-l4_height-13))
graph.append(legend4)


graph.save(sys.argv[2])
