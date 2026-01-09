# Makefile for OxDC MD Analysis Presentation

# Main target
MAIN = oxdc_md_analysis_with_figures
OUTPUT = oxdc_md_presentation.pdf

# LaTeX compiler
LATEX = pdflatex
LATEXFLAGS = -interaction=nonstopmode

# Default target
all: $(OUTPUT)

$(OUTPUT): $(MAIN).tex
	$(LATEX) $(LATEXFLAGS) $(MAIN).tex
	$(LATEX) $(LATEXFLAGS) $(MAIN).tex
	mv $(MAIN).pdf $(OUTPUT)

# Build without figures (placeholder version)
draft:
	$(LATEX) $(LATEXFLAGS) oxdc_md_analysis.tex
	$(LATEX) $(LATEXFLAGS) oxdc_md_analysis.tex

# Clean auxiliary files
clean:
	rm -f *.aux *.log *.nav *.out *.snm *.toc *.vrb

# Clean all including PDF
distclean: clean
	rm -f *.pdf

# View the PDF (Linux)
view: $(OUTPUT)
	xdg-open $(OUTPUT) 2>/dev/null || open $(OUTPUT)

.PHONY: all draft clean distclean view
