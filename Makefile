#!/usr/bin/make -f

SOURCES := tesco.json

all: $(SOURCES)

clean:
	rm -f *.json *.log

%.json:
	scrapy crawl --output $@ --output-format=proteinjson $* 2>&1 | tee $@.log

deploy: $(SOURCES)
	set -eu; \
		DIR=`mktemp -d`; \
		cp -rv .git/ *.html *.json $${DIR}; \
		cd $${DIR}/; \
		git branch -D gh-pages || true; \
		git checkout --orphan gh-pages; \
		git add --all .; \
		git commit -m "(Automatic build)"; \
		git push -f origin gh-pages

.PHONY: deploy
