# Makefile for generating AEGEE bingo cards (PDF)
# Usage:
#   make
#   make run
#   make N=21 OUT=bingos.pdf
#   make help

PYTHON      ?= python
SCRIPT      ?= bingo_aegee.py

N           ?= 10
CSV         ?= bingo_ideas_example.csv
TEMPLATE_PDF?= aegeeleon-bingo-template.pdf
OUT         ?= combined_bingo_cards.pdf

M_LEFT      ?= 0.05
M_RIGHT     ?= 0.05
M_TOP       ?= 0.240
M_BOTTOM    ?= 0.065

FONT_SIZE   ?= 20
PADDING     ?= 8

# Optional:
# CENTER    ?= keep   # keep|free
# FREE_TEXT ?= FREE
# SEED      ?= 42

.PHONY: all run clean help vars

all: run

run:
	$(PYTHON) $(SCRIPT) -n $(N) \
		--csv $(CSV) \
		--template-pdf $(TEMPLATE_PDF) \
		--out $(OUT) \
		--m-left $(M_LEFT) \
		--m-right $(M_RIGHT) \
		--m-top $(M_TOP) \
		--m-bottom $(M_BOTTOM) \
		--font-size $(FONT_SIZE) \
		--padding $(PADDING)

clean:
	@rm -f "$(OUT)"

vars:
	@echo PYTHON=$(PYTHON)
	@echo SCRIPT=$(SCRIPT)
	@echo N=$(N)
	@echo CSV=$(CSV)
	@echo TEMPLATE_PDF=$(TEMPLATE_PDF)
	@echo OUT=$(OUT)
	@echo M_LEFT=$(M_LEFT)
	@echo M_RIGHT=$(M_RIGHT)
	@echo M_TOP=$(M_TOP)
	@echo M_BOTTOM=$(M_BOTTOM)
	@echo FONT_SIZE=$(FONT_SIZE)
	@echo PADDING=$(PADDING)

help:
	@echo "Targets:"
	@echo "  make / make run      Generate bingo PDF using current variables"
	@echo "  make clean           Remove output PDF"
	@echo "  make vars            Print current variable values"
	@echo ""
	@echo "Override variables like:"
	@echo "  make N=21 OUT=bingos.pdf"
	@echo "  make CSV=ideas.csv TEMPLATE_PDF=template.pdf"
	@echo "  make FONT_SIZE=10 PADDING=6"
