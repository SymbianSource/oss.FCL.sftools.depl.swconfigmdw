#!/bin/bash
#
# Copyright (c) 2009 Nokia Corporation and/or its subsidiary(-ies).
# All rights reserved.
# This component and the accompanying materials are made available
# under the terms of "Eclipse Public License v1.0"
# which accompanies this distribution, and is available
# at the URL "http://www.eclipse.org/legal/epl-v10.html".
#
# Initial Contributors:
# Nokia Corporation - initial contribution.
#
# Contributors:
#
# Description: 
#  ConE tool wrapper for Unix

# Check that Python is available
# ------------------------------
python --version &> /dev/null
if [ $? -ne 0 ]
then
    echo "Python is required to run ConE!"
    exit 1
fi


# Determine the path where ConE is installed
# ------------------------------------------

# Try to derefence a symlink
SCRIPT_FILE=`readlink $0`
if [ "$SCRIPT_FILE" = "" ]
then
    # Not a symlink, the first command line parameter can be used
    SCRIPT_FILE=$0
fi
CONE_BASEDIR=`dirname "$SCRIPT_FILE"`/cone


# Find out the Python version
# ---------------------------
PYTHON_VERSION=`python -c "import sys; print sys.version[:3]"`
#echo "Python version: $PYTHON_VERSION"


# Set the correct lib and scripts directories
# to use based on the Python version
# -------------------------------------------
case $PYTHON_VERSION in
"2.5")
    CONE_BASEDIR="$CONE_BASEDIR/2.5"
    ;;
"2.6")
    CONE_BASEDIR="$CONE_BASEDIR/2.6"
    ;;
*)
    echo "You are using an unsupported Python version ($PYTHON_VERSION)"
    echo "ConE requires Python 2.5 or 2.6"
    exit 1
    ;;
esac

#echo "CONE_BASEDIR: $CONE_BASEDIR"


# Check that this ConE installation supports the Python version
# -------------------------------------------------------------
if [ ! -e "$CONE_BASEDIR" ]
then
    echo "Python version $PYTHON_VERSION is not supported by this ConE installation"
    exit 1
fi


# Override PYTHONPATH so that the libraries in
# the standalone installation are used
# --------------------------------------------
export PYTHONPATH="$CONE_BASEDIR/lib:$PYTHONPATH"

# Run cone_tool.py
# ----------------
python $CONE_BASEDIR/scripts/cone_tool.py $@
