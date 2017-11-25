clean:
	rm -r index wget

server:
	mkdir -p wget
	touch wget/worker.log
	python server.py

install:
	pip install -r requirements.txt
