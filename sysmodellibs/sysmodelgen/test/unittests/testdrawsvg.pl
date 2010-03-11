# Copyright (c) 2008-2009 Nokia Corporation and/or its subsidiary(-ies).
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
use Test;

BEGIN { plan tests => 7}

use FindBin;
use lib $FindBin::Bin."/../../src/svg";
use lib $FindBin::Bin."/../../src/common";
use DrawSvg;
use File::Spec;

# File not specified, should return undef
ok(DrawSvg->FullPath(), undef);

# If file is a URL then should be returned as is
ok(DrawSvg::FullPath(undef, 'http://something.com'), 'http://something.com');

# If file is Windows path then should be returned as is
ok(DrawSvg::FullPath(undef, 'c:\\something.txt'), 'c:\\something.txt');

# If the root is a file then the directory name should be used
ok(DrawSvg::FullPath("$0", 'afile.txt'), File::Spec->catdir($FindBin::Bin, 'afile.txt'));

# If root is already a directory then the root should remain unchanged
ok(DrawSvg::FullPath($FindBin::Bin, 'afile.txt'), File::Spec->catdir($FindBin::Bin, 'afile.txt'));

# If the file is relative from the root then add drive letter to file
my ($driveLetter) = split /[\\\/]/, $FindBin::Bin;
ok(DrawSvg::FullPath($FindBin::Bin, '\afile.txt'), File::Spec->catdir($driveLetter, 'afile.txt'));

# If the file is relative from the root but root doesn't contain a drive letter
ok(DrawSvg::FullPath(undef, '\afile.txt'), '\afile.txt');

# If root does not exist then a fatal error should be logged
#	Unable to test this due to exit in logger