#############################################################################
#
# Makefile for CitizenWatt install on Raspberry Pi
#
# License: GPL (General Public License)
# Author:  AlexFaraino
# Date:    2014/10/20 (v1.0)
#
# Description:
# ------------
# You can change the install directory by editing the prefix line
#
prefix=$(DESTDIR)/opt/citizenwatt
files=`ls | grep -v debian`
sup_prefix=$(DESTDIR)/etc/supervisor/conf.d/

# The recommended compiler flags for the Raspberry Pi
CCFLAGS=-Wall -Ofast -mfpu=vfp -mfloat-abi=hard -march=armv6zk -mtune=arm1176jzf-s

all: receive

receive: receive.cpp
	g++ ${CCFLAGS}  -lrf24 $@.cpp -o $@

clean:
	rm -rf receive

install: all
	test -d $(prefix) || mkdir -p $(prefix)
	test -d $(sup_prefix) || mkdir -p $(sup_prefix)
	cp -r $(files) $(prefix)/
	cp system/supervisor_citizenwatt.conf $(sup_prefix)/citizenwatt.conf

.PHONY: install
