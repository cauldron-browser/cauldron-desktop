clean:
	rm -r index wget url_map.db .google-cookie

server:
	mkdir -p wget
	touch wget/worker.log
	python server.py

install:
	pip install -r requirements.txt