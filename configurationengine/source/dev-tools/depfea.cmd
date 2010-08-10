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
::  Name        : depfea.cmd
::  Part of     : depfea
::  Description : depfea tool wrapper for Windows
::  Version     : %version: 1 %
::
:: ============================================================================



@echo off
setlocal

set CONE_CMDARG=%*
set BASEDIR=%~dp0
set CONE_BASEDIR=%BASEDIR%configurationengine\win\
set PYTHONCASEOK=1

if not exist "%CONE_BASEDIR%" (
echo Cannot run ConE, the ConE base directory does not exist:
echo %CONE_BASEDIR%
exit /b 1
)

@rem Check that Python is available
call python -c None >nul 2>&1
if %errorlevel% neq 0 (
echo Python is required to run ConE!
exit /b 1
)

@REM Find out Python version
FOR /F "tokens=*" %%i in ('PYTHON -c "import sys; sys.stdout.write(sys.version[:3])"') do SET VER1=%%i

@REM Set the used base directory based on the version
if %VER1%==2.5 (
set CONE_BASEDIR=%CONE_BASEDIR%2.5\
goto EndVersionCheck
)
if %VER1%==2.6 (
set CONE_BASEDIR=%CONE_BASEDIR%2.6\
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

@rem Set the egg cache dir to be unique to avoid egg extraction clashes
@rem when running multiple parallel ConE instances
FOR /F "tokens=*" %%i in ('PYTHON -c "import tempfile; d = tempfile.mkdtemp(); print d"') do SET EGG_CACHE_DIR=%%i
@rem echo Egg cache dir: %EGG_CACHE_DIR%
set PYTHON_EGG_CACHE=%EGG_CACHE_DIR%

@rem Set environment variables and run deprfea.py
set CONE_LIBDIR=%CONE_BASEDIR%\lib
set CONE_SCRIPTDIR=%CONE_BASEDIR%\scripts
set PATH=%CONE_SCRIPTDIR%;%PATH%
set PYTHONPATH=%CONE_LIBDIR%;%PYTHONPATH%
REM The cone_tool will parse the arguments from the environment variable
call python "%BASEDIR%deprfea.py" %*
set CONE_ERROR_CODE=%ERRORLEVEL%

@rem Delete the egg cache dir
call rd /S /Q "%EGG_CACHE_DIR%"

if 0%CONE_EXITSHELL% equ 0 exit /b %CONE_ERROR_CODE%
exit %CONE_ERROR_CODE%
endlocal

:: END OF depfea.cmd
