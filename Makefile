ENGINE=dot
#ENGINE=neato
#ENGINE=fdp
#ENGINE=twopi

.SECONDARY: kr_all_logs.dot kr_oldest_logs.dot legend1.dot legend1.svg_inter \
                                               legend2.dot legend2.svg_inter \
                                               legend3.dot legend3.svg_inter \
                                               legend4.dot legend4.svg_inter

all: pdf svg report

pdf: kr_all_logs.pdf kr_oldest_logs.pdf
	open kr_all_logs.pdf
	open kr_oldest_logs.pdf 

svg: kr_all_logs.svg kr_oldest_logs.svg
	open kr_all_logs.svg
	open kr_oldest_logs.svg

svg_inter: kr_all_logs.svg_inter kr_oldest_logs.svg_inter legend.svg_inter

#%.pdf: %.dot
#	$(ENGINE) -Tpdf -o $(basename $<).pdf $<
%.pdf: %.svg
	rsvg-convert -f pdf -o $(basename $<).pdf $<

%.svg: %.svg_inter legend1.svg_inter legend2.svg_inter legend3.svg_inter legend4.svg_inter
	python3 implant_legend.py $< $(basename $<).svg

%.svg_inter: %.dot
	$(ENGINE) -Tsvg -o $(basename $<).svg_inter $<

%.dot: kettenreaktion_data.pickle
	python3 build_graph_phase2_generate_dot.py

report:
	python3 build_graph_phase2_generate_dot.py -r

kettenreaktion_data.pickle:
	python3 build_graph_phase1_retrieve_data.py

default: all

dist:
	(cd .. && tar cvfz /tmp/opencaching_kettenreaktion.tgz --exclude='report*' --exclude='*~' opencaching_kettenreaktion )

clean:
	rm -f *.dot *.svg *.svg_inter *.pdf

deepclean: clean
	rm -f kettenreaktion_data.pickle
