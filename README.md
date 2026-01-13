# bingo-creator

Simple PDF 5x5 bingo card generator using a background template and an Excel (`.xlsx`) file with ideas.

The script places random text into a 5×5 bingo grid over a PDF template. Designed for meetings, assemblies, and themed events.


## Project structure

```

.
├── .gitignore
├── aegeeleon-bingo-template.pdf
├── bingo_aegee.py
├── bingo_ideas_example.xlsx
├── Makefile
├── README.md
└── requirements.txt

````

## Installation

```bash
pip install -r requirements.txt
````

## Quick usage

```bash
python bingo_aegee.py \
  -n 10 \
  --xlsx bingo_ideas_example.xlsx \
  --template-pdf aegeeleon-bingo-template.pdf \
  --out combined_bingo_cards.pdf \
  --m-left 0.05 --m-right 0.05 --m-top 0.240 --m-bottom 0.065 \
  --font-size 16 --padding 8
```
or
```bash
python bingo_aegee.py -n 10 --xlsx bingo_ideas_example.xlsx --template-pdf aegeeleon-bingo-template.pdf --out combined_bingo_cards.pdf --m-left 0.05 --m-right 0.05 --m-top 0.240 --m-bottom 0.065 --font-size 16 --padding 8
```

## Using the Makefile

Generate with defaults:

```bash
make run
```

Override options:

```bash
make N=10 OUT=combined_bingo_cards.pdf
make XLSX=bingo_ideas_example.xlsx
```

## Notes

* Bingo items must be in **column A** of the Excel file
* Minimum **24 unique items** required
