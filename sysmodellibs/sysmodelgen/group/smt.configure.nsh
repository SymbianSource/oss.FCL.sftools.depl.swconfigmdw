push $R1

FileOpen $R1 "$INSTDIR\SysModGen.cmd" w
FileWrite $R1 "@echo off$\r$\n"
FileWrite $R1 "perl -S $INSTDIR\SystemModelGenerator\SysModGen.pl %* $\r$\n"
FileClose $R1


pop $R1
