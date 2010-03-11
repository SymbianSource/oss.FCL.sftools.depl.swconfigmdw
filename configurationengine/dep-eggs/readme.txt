This directory contains all library dependencies needed by ConE as egg files.

Note that if a plug-in requires a library not used in ConE core, the egg
should not be added here, but in source/plugins/<plugin-package>/dep-eggs/.
This way the egg will not be installed unless the plug-in package requiring
it is installed.
