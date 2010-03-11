all:
	perl -S drawsvg.pl -i filestest.ini
	perl -S drawsvg.pl -i dirtest.ini
	perl -S drawsvg.pl -s12 . -system_version 9.5 -sysdef System_Definition_Template.xml -o model95A.svg -shapes "" -tempdir  model95 -sysinfo ""
	perl -S drawsvg.pl -s12  Symbian_OS_v9.4_Schedule12.xml -s12  Symbian_OS_v9.5_Schedule12.xml -s12  Symbian_OS_v9.6_Schedule12.xml -s12  Symbian_OS_vFuture_Schedule12.xml  -sysdef System_Definition_Template.xml -o modelallA.svg -shapes "" -tempdir  modelall -sysinfo ""
	
