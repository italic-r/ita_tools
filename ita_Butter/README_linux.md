# Linux Install Tips
##### A quick guide to preparing and utilizing an isolated environment for Maya Python

This guide assumes a default Linux install and a default Maya installation
(I will use 2016.5 x64 for this guide).

###### Some background
* Maya's installation directory should not be disturbed! Keep Maya's directories
  as clean as possible.
* Using a virtual environment will allow you to install and experiment with
  packages while keeping Maya safe from tampering.
* Maya 2014-2017 use Python 2.7.x

Preparing the system
--
The most basic setup you need is a system install of Python 2.7.x. The exact x
number is not very important; the important part is that it is a release of
2.7. Python 2.7 is included by default on nearly all systems, so this is likely
already set up for you. Accompanying this install is a small tool called
`virtualenv`, a vital ingredient for our plans. You can check for virtualenv
by calling it in the terminal with `virtualenv --help`. Install it if you do
not have it.

Creating a virtual environment
--
Create a virtual environment by calling `virtualenv ~/.virtualenvs/mayapy` in
any directory. The terminal will give some feedback about installing setuptools
and pip, then it finishes. The virtual environment has been set up with the
system install of Python 2.7 and is ready to be activated.

Navigate to your virtual environment root: `~/.virtualenvs/mayapy` and source
the activation script using `source bin/activate`.

Congratulations! You now have an isolated environment to test packages for
Maya. Using Numpy as an example, I will show how you can utilize it.

Numpy
--
Numpy is a combination Python/C library for computation-heavy math. Because it is
partly written in C, it is more difficult to distribute and use in non-standard
locations. This walkthrough describes how I use Numpy in Maya.

#### Installing Numpy
Installing Numpy is surprisingly simple with `pip`, Python's package manager.
Simply run `pip install numpy` and it will download and compile the package
based on the Python interpreter you set up in the virtual environment. Enter
into a Python interpreter by calling `python` in your activated environment.
Call `import numpy` to import the Numpy library. If it gives no feedback, it
imported without error. Great!

#### Numpy in Maya
Say you want to use Numpy in Maya for writing a tool. If you copy the numpy
library over to your Maya scripts directory, you would expect Maya to find
the library and import it just as in your virtual environment. However, Maya
will spit out an error saying a library could not be loaded. Without moving
Numpy, we can fix this with one line:
```import os, site; site.addsitedir(os.path.expanduser("~/.virtualenvs/mayapy/lib/python2.7/site-packages"))```
Importing Numpy should result in no output. You now have a fast math library
for use in Maya and your scripts. Any tool that requires Numpy will have
access to Numpy through this path, so there is no need to have multiple copies
of Numpy floating around.

Scipy
--
Follow the same instructions as with [Numpy](README_linux.md#numpy).

Utilizing The Libraries
--
The next logical step is to add this path to your Maya configuration using
`userSetup.py`. Copy the same code line to the top of userSetup.py and it
is now available on Maya startup.

It is important to note an added benefit to using site-packages from the
virtual environment: you can develop in the virtual environment as you would
normally and access all the same libraries within Maya.

#### For individual tools
To use with a single tool, make a 'deps' folder in the tool root.
```
tool_root/
    deps/
        numpy/
        scipy/
        ...
    __init__.py
    ...
```
In \__init\__.py add the line:
```import os, site; site.addsitedir(os.path.join(os.path.dirname(__file__), 'deps'))```

## Recap
* Make sure Python 2.7.x and virtualenv are on your system.
* `virtualenv ~/.virtualenvs/mayapy` to create a new virtual environment.
* `cd ~/.virtualenvs/mayapy && source bin/activate` to activate the
  environment.
* `pip install numpy` to install Numpy.
* Put ``python
  import os, site;
  site.addsitedir(os.path.expanduser("~/.virtualenvs/mayapy/lib/python2.7/site-packages"))``
  at the top of `userSetup.py`
* Start Maya as normal and import Numpy from the script editor or through a Python
  script.
* Develop your Maya scripts within the virtual environment.

Have questions/comments/revision? Leave a
[report](https://github.com/Italic-/ita_tools/issues) or
[pull request](https://github.com/Italic-/ita_tools/pulls) on Github.
