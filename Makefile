clean:
	rm -r index wget url_map.db

server:
	mkdir -p wget
	touch wget/worker.log
	python server.py $(ARGS)

install:
	pip install -r requirements.txt
