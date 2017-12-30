SHELL := /bin/bash

clean:
	rm -r ~/.cache/cauldron

server:
	CAULDRON_DIR=~/.cache/cauldron ./dist/server

install-ubuntu:
	-systemctl --user stop desktop.cauldron.service
	mkdir -p ~/.cache/cauldron
	cp dist/download_blacklist.txt ~/.cache/cauldron
	sudo cp dist/cauldron /usr/local/bin
	sudo cp dist/desktop.cauldron.service /etc/systemd/user/desktop.cauldron.service
	#sudo cp dist/desktop.cauldron.service ~/.config/systemd/user/desktop.cauldron.service
	systemctl --user daemon-reload
	systemctl --user start desktop.cauldron.service
	systemctl --user enable desktop.cauldron.service

build:
	python3 -m venv .cauldron-venv
	source .cauldron-venv/bin/activate; \
	pip install -r requirements.txt; \
	pyinstaller --clean --onefile cauldron.py
	cp download_blacklist.txt dist
	cp install/desktop.cauldron.service dist

optipng:
	find wget/downloads -name '*.png' -print0 | xargs -0 optipng -o7

