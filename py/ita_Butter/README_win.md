# Windows Install Tips
##### A quick guide to installing Windows wheels.

This guide assumes no Python installation is available on a Windows machine,
and your firewall allows downloading .whl files. This guide also assumes your
Maya version is 2014-2017 (these use Python 2.7.x); adjust versions as
necessary for earlier Maya versions. This guide will use 2016.5.

###### Some background
* Maya's installation directory should not be disturbed! Keep Maya's directories
as clean as possible.
* Maya 2014-2017 use Python 2.7.x
* %MAYA_APP_DIR% is an environment variable that specifies where Maya's
preferences are stored. On Windows, this defaults to
*C:\\Users\\\_\_username\_\_\\My Documents\\maya*.
I will assume this configuration.
* %MAYA_SCRIPTS_PATH% is a variable Maya uses to find scripts to source at startup.
A typical default is *%MAYA_APP_DIR%\\2016.5\\prefs\\scripts*.
I assume you know what paths are in your scripts path.

### The Basics
The easiest, most direct way to get a binary library for Windows is to
download a pre-built binary. This avoids the need for a C(++) compiler
and avoids unnecessary virtual environments. 

To demonstrate, we will use Numpy and Scipy, two libraries useful for
heavy number crunching and data filtering. Both of these libraries require
C(++) compilation and Scipy depends on Numpy, so they are perfect for this method.

How To
--
* Download
[numpy-1.9.2-cp27-none-win_amd64.whl](https://pypi.anaconda.org/carlkl/simple/numpy/)
and
[scipy-0.16.0-cp27-none-win_amd64.whl](https://pypi.anaconda.org/carlkl/simple/scipy/)
(or \*win32.whl if on 32-bit Windows).
 
* Rename the downloaded files from \*.whl to \*.zip and open them in your
favorite zipping program (such as Windows Explorer, Peazip, 7-zip, etc.).
 
* Extract the library directories (*numpy* or *scipy* in this example)
into a new directory for storing Python binaries.

**NOTE:** this directory **cannot** be in a Maya scripts path
(such as %MAYA_APP_DIR%\\maya2014-x64\\prefs\\scripts or any path
specified in the environment variable %MAYA_SCRIPTS_PATH%).
I recommend something like *%MAYA_APP_DIR%\\deps*.

* Add this new path to your Python environment within Maya.

* * For general use in Maya, in _userSetup.py_ put the line at the top:
```python
import os, site; site.addsitedir(os.path.join(os.path.expandvars("$MAYA_APP_DIR"), "deps"))
```

* * For use within a package, make a new "deps" directory in your
package root, put numpy and scipy in there, and in your package's
_\_\_init\_\_.py_ put:
```python
import os, site; site.addsitedir(os.path.join(os.path.dirname(__name__)), "deps")
```

* Import Numpy or Scipy from Maya's script editor or another module with:
```python
import numpy, scipy
```
