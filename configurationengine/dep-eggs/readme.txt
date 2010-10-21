This directory contains all library dependencies needed by ConE as egg files.

In addition to these libraries, ConE also depends on Jinja2 and lxml. Use the 
following commands to install these libraries into your Python environment:

easy_install Jinja2
easy_install lxml

Note: If you need to use a HTTP proxy to access the Internet, you need to set
HTTP_PROXY enviroment variable before running the above commands.

Note that if a plug-in requires a library not used in ConE core, the egg
should not be added here, but in source/plugins/<plugin-package>/dep-eggs/.
This way the egg will not be installed unless the plug-in package requiring
it is installed.
