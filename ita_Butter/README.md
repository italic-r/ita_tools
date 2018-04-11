# Butter
##### A Butterworth filter for Maya's animation curves using Numpy and Scipy.

Butter is under active development. Functionality and interface may change
periodically. Please report any bugs and submit pull requests at the links
below.

This filter allows you to quickly smooth and denoise high-density animation
curves, usually from motion capture. If any curves are selected, the filter
will manipulate only selected curves. If no curves are selected, the filter
will manipulate all visible curves in the graph editor.

Quick tip: expand the window sideways for higher precision!

How to use:
Enable the filter by clicking Start interactive filter.
Select your filter type from [Highpass, Bandpass, Lowpass].
Use the sliders to start filtering curves.
Exit the filter by clicking Exit filter.
Undo or redo as necessary.


Loading and Unloading
--
```python
# Load
import ita_Butter
ita_Butter.show()
```


To Install
--
Put ita_Butter directory into your maya scripts directory. The default
locations are:

| System | Location |
| ------ | ------ |
| Windows | C:\Users\\_user_\My Documents\maya\\_version_\prefs\scripts |
| Linux | ~/maya/_version_/prefs/scripts |
| Mac | /Users/_user_/Library/Preferences/Autodesk/maya/version |


Dependencies
--
Butter requires Numpy and Scipy. These are libraries with C extensions, so must
be compiled for Maya's Python interpreter (mayapy) and be made available to it.
The script looks for these libraries under `ita_Butter/deps`, but any other
available site-packages directory would also work. Compiling C extensions is
beyond the scope of this readme, but pre-compiled binaries are available for
download:

Windows: See [Windows README](README_win.md) for instructions.

Mac and Linux: See [Linux README](README_linux.md) for instructions.

For a custom site-packages directory:

* `import site; site.addsitedir('/path/to/site/packages')   # Linux/Mac`

* `import site; site.addsitedir('C:\\path\\to\\site\\packages') # Windows`


# License

(c) Jeffrey "italic" Hoover
italic DOT rendezvous AT gmail DOT com

Licensed under the Apache 2.0 license.
This script can be used for commercial
and non-commercial projects free of charge.
For more information, visit:
https://www.apache.org/licenses/LICENSE-2.0

Attribution not necessary, but greatly appreciated.
Submit [bug reports](https://github.com/Italic-/ita_tools/issues) and
[pull requests](https://github.com/Italic-/ita_tools/pulls).

Enjoy!
