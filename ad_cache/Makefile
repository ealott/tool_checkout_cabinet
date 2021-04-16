all: adcache adcache.service
.PHONY: all adcache install uninstall
lib_dir=/usr/local/lib/adcache
conf_dir=/usr/local/etc/adcache
service_dir=/etc/systemd/system
venv=$(lib_dir)/venv

install: $(service_dir) adcache.service
	@echo Installing the service files...
	cp adcache.service $(service_dir)
	chown root:root $(service_dir)/adcache.service
	chmod 644 $(service_dir)/adcache.service

	@echo Installing library files...
	mkdir -p $(lib_dir)
	cp adcache.py $(lib_dir)
	chown root:root $(lib_dir)/*
	chmod 644 $(lib_dir)/*

	@echo Installing configuration files...
	mkdir -p $(conf_dir)
	cp adcache.env $(conf_dir)
	chown root:root $(conf_dir)/*
	chmod 644 $(conf_dir)/*

	@echo Creating python virtual environment and isntalling packages...
	python3 -m venv $(venv)
	$(venv)/bin/pip3 install -r requirements.txt

	@echo Installation complete...
	@echo run 'systemctl start adcache' to start service
	@echo run 'systemctl status adcache' to view status

uninstall:
	-systemctl stop adcache
	-systemctl disable adcache
	-rm -r $(lib_dir)
	-rm -r $(conf_dir)
	-rm -r $(service_dir)/adcache.service