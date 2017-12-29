clean:
	rm -r index wget url_map.db

server:
	mkdir -p wget
	touch wget/worker.log
	python server.py $(ARGS)

install:
	pip install -r requirements.txt

optipng:
	find wget/downloads -name '*.png' -print0 | xargs -0 optipng -o7
