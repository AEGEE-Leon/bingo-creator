# Makefile for generating AEGEE bingo cards (PDF)
# Usage:
#   make
#   make run
#   make N=21 OUT=bingos.pdf
#   make XLSX=my_items.xlsx
#   make SHEET=Hoja1
#   make help

PYTHON       ?= python
SCRIPT       ?= bingo_aegee.py

N            ?= 1
XLSX         ?= bingo_ideas_example.xlsx
SHEET        ?=
TEMPLATE_PDF ?= aegeeleon-bingo-template.pdf
OUT          ?= combined_bingo_cards.pdf

M_LEFT       ?= 0.045
M_RIGHT      ?= 0.045
M_TOP        ?= 0.240
M_BOTTOM     ?= 0.065

FONT_SIZE    ?= 20
PADDING      ?= 8

# Optional:
# CENTER     ?= keep   # keep|free
# FREE_TEXT  ?= FREE
# SEED       ?= 42

.PHONY: all run clean help vars install

all: run

run:
	$(PYTHON) $(SCRIPT) -n $(N) \
		--xlsx $(XLSX) \
		$(if $(SHEET),--sheet "$(SHEET)",) \
		--template-pdf $(TEMPLATE_PDF) \
		--out $(OUT) \
		--m-left $(M_LEFT) \
		--m-right $(M_RIGHT) \
		--m-top $(M_TOP) \
		--m-bottom $(M_BOTTOM) \
		--font-size $(FONT_SIZE) \
		--padding $(PADDING) \
		$(if $(CENTER),--center $(CENTER),) \
		$(if $(FREE_TEXT),--free-text "$(FREE_TEXT)",) \
		$(if $(SEED),--seed $(SEED),)

clean:
	@rm -f "$(OUT)"

install:
	pip install -r requirements.txt

vars:
	@echo PYTHON=$(PYTHON)
	@echo SCRIPT=$(SCRIPT)
	@echo N=$(N)
	@echo XLSX=$(XLSX)
	@echo SHEET=$(SHEET)
	@echo TEMPLATE_PDF=$(TEMPLATE_PDF)
	@echo OUT=$(OUT)
	@echo M_LEFT=$(M_LEFT)
	@echo M_RIGHT=$(M_RIGHT)
	@echo M_TOP=$(M_TOP)
	@echo M_BOTTOM=$(M_BOTTOM)
	@echo FONT_SIZE=$(FONT_SIZE)
	@echo PADDING=$(PADDING)
	@echo CENTER=$(CENTER)
	@echo FREE_TEXT=$(FREE_TEXT)
	@echo SEED=$(SEED)

help:
	@echo "Targets:"
	@echo "  make / make run      Generate bingo PDF using current variables"
	@echo "  make clean           Remove output PDF"
	@echo "  make install         Install dependencies from requirements.txt"
	@echo "  make vars            Print current variable values"
	@echo ""
	@echo "Override variables like:"
	@echo "  make N=21 OUT=bingos.pdf"
	@echo "  make XLSX=ideas.xlsx TEMPLATE_PDF=template.pdf"
	@echo "  make SHEET=Hoja1"
	@echo "  make FONT_SIZE=10 PADDING=6"
	@echo "  make CENTER=free FREE_TEXT=GRATIS"
	@echo "  make SEED=42"
