# Copyright (c) 2008-2009 Nokia Corporation and/or its subsidiary(-ies).
# All rights reserved.
# This component and the accompanying materials are made available
# under the terms of the License "Eclipse Public License v1.0"
# which accompanies this distribution, and is available
# at the URL "http://www.eclipse.org/legal/epl-v10.html".
#
# Initial Contributors:
# Nokia Corporation - initial contribution.
#
# Contributors:
#
# Description:
#

DetailPrint "Configuring SDB..."

push $R0
push $R1

ClearErrors
${REReplace} $R0 "\\" $INSTDIR "\\\\" 1
IfErrors REGEXP_ERRS_SDB_INSTDIR REGEXP_NO_ERRS_SDB_INSTDIR

REGEXP_NO_ERRS_SDB_INSTDIR:
ClearErrors
FileOpen $R1 "$INSTDIR\sdb-creator\config\sdb.properties" w
IfErrors FILEOPEN_ERRS_SDB_INSTDIR FILEOPEN_NO_ERRS_SDB_INSTDIR


FILEOPEN_NO_ERRS_SDB_INSTDIR:
FileWrite $R1 "# Log File Settings$\r$\n"
FileWrite $R1 "sdb.log.file.enabled = true$\r$\n"
FileWrite $R1 "sdb.log.file.format  = %-5p [%-20.20C{1}] %-8r %4L - %m%n$\r$\n"
FileWrite $R1 "sdb.log.file.path    = logs\\sdb.log$\r$\n"
FileWrite $R1 "sdb.log.file.level   = DEBUG$\r$\n$\r$\n"
FileWrite $R1 "# Console Log Settings$\r$\n"
FileWrite $R1 "sdb.log.console.format = %m%n$\r$\n"
FileWrite $R1 "sdb.log.console.level  = INFO$\r$\n$\r$\n"
FileWrite $R1 "#Default Database Settings$\r$\n"
FileWrite $R1 "sdb.dbname = sdb.db$\r$\n$\r$\n"
FileWrite $R1 "#JDBC dll location$\r$\n"
FileWrite $R1 "org.sqlite.lib.path = $R0\\sdb-creator\\lib\\$\r$\n"
FileWrite $R1 "com.symbian.dbms.lib.path = $R0\\sdb-creator\\lib\\$\r$\n"
FileWrite $R1 "sdb.contacts.configuration = $R0\\sdb-creator\\config\\contacts.xml$\r$\n"
FileWrite $R1 "sdb.contacts.configuration.locale = $R0\\sdb-creator\\config\\contacts_locale_en_gb.xml$\r$\n"
FileWrite $R1 "sdb.ced.location = $R0\\ced\\win$\r$\n"
FileClose $R1
DetailPrint "Successfully wrote config file for SDB."
GOTO SDB_END


FILEOPEN_ERRS_SDB_INSTDIR:
DetailPrint "ERROR: Failed to open SDB configuration file for writing."

GOTO SDB_END

REGEXP_ERRS_SDB_INSTDIR:
DetailPrint "ERROR: Failed to write INSTDIR variable with double backslash."

SDB_END:

pop $R1
pop $R0
