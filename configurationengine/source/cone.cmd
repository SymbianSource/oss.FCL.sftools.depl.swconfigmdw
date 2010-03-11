@rem
@rem Copyright (c) 2009 Nokia Corporation and/or its subsidiary(-ies).
@rem All rights reserved.
@rem This component and the accompanying materials are made available
@rem under the terms of "Eclipse Public License v1.0"
@rem which accompanies this distribution, and is available
@rem at the URL "http://www.eclipse.org/legal/epl-v10.html".
@rem
@rem Initial Contributors:
@rem Nokia Corporation - initial contribution.
@rem
@rem Contributors:
@rem
@rem Description:
@rem

:: ============================================================================
::  Name        : cone.cmd
::  Part of     : ConE
::  Description : ConE tool wrapper for Windows
::  Version     : %version: 1 %
::
:: ============================================================================



@echo off
setlocal

set CONE_CMDARG=%*
set CONE_BASEDIR=%~dp0
set PYTHONCASEOK=1

@rem Check that Python is available
call python -h >nul 2>&1
if %errorlevel% neq 0 (
echo Python is required to run ConE!
exit /b 1
)

@REM Find out Python version
set VERFILE=%TEMP%\cone_version_check.tmp
python -c "import sys; print sys.version[:3]" > %VERFILE%
set varNUM=0
for /f "tokens=*" %%T in (%VERFILE%) do call :varSET %%T
if exist %VERFILE% del %VERFILE% 


@REM Set the used base directory based on the version
if %VER1%==2.5 (
set CONE_BASEDIR=%CONE_BASEDIR%cone\2.5\
goto EndVersionCheck
)
if %VER1%==2.6 (
set CONE_BASEDIR=%CONE_BASEDIR%cone\2.6\
goto EndVersionCheck
)
echo You are using an unsupported Python version (%VER1%)
echo ConE requires Python 2.5 or 2.6
exit /b 1
)
:EndVersionCheck

@rem Check that this ConE installation supports the Python version
if not exist "%CONE_BASEDIR%" (
echo Python version %VER1% is not supported by this ConE installation
exit /b 1
)


@rem Set environment variables and run cone_tool.py
set CONE_LIBDIR=%CONE_BASEDIR%\lib
set CONE_SCRIPTDIR=%CONE_BASEDIR%\scripts
set PATH=%CONE_SCRIPTDIR%;%PATH%
set PYTHONPATH=%CONE_LIBDIR%;%PYTHONPATH%
call python "%CONE_SCRIPTDIR%\cone_tool.py" %CONE_CMDARG%
exit /b %ERRORLEVEL%

endlocal

:VarSET
set /a varNUM=%varNUM%+1
set VER%varNUM%=%1

:: END OF cone.cmd
