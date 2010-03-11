#!perl
# Copyright (c) 2007-2009 Nokia Corporation and/or its subsidiary(-ies).
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
#

use strict;
use warnings;
use FindBin;
use lib $FindBin::Bin;
use lib $FindBin::Bin."/svg";
use lib $FindBin::Bin."/common";
use lib $FindBin::Bin."/../common"; # needed to run from within DepToolkit

use DrawSvg;

my $drawer = new DrawSvg();
$drawer->Draw();

exit;
