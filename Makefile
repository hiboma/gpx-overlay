fit2tsv:
	/bin/ls -1 activities/*.fit | xargs -P4 -IXXX bundle exec ruby bin/fit2tsv.rb XXX

all:
	python ./bin/overlay.py --activities 'activities/*.tsv'

2016:
	python ./bin/overlay.py --activities 'activities/2016-*.tsv' --output 2016.html

2017:
	python ./bin/overlay.py --activities 'activities/2017-*.tsv' --output 2017.html

2018:
	python ./bin/overlay.py --activities 'activities/2018-*.tsv' --output 2018.html
