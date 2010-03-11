DETAILS=component collection subblock block layer
NORMALDETAIL = $(foreach v,$(DETAILS),$(v)-normal.svg)
FIXEDDETAIL = $(foreach v,$(DETAILS),$(v)-fixed.svg)
STATICDETAIL = $(foreach v,$(DETAILS),$(v)-static.svg)

all: $(NORMALDETAIL) $(FIXEDDETAIL) $(STATICDETAIL)

%-normal.svg : model.ini
	perl -S DrawSvg.pl -clean -o $@ -i model.ini -detail $*

%-static.svg : model.ini
	perl -S DrawSvg.pl -clean -o $@ -i model.ini -detail $* -static

%-fixed.svg : model.ini
	perl -S DrawSvg.pl -clean -o $@ -i model.ini -detail $* -detail-type fixed


