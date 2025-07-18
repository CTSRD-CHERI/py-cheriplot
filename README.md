# py-cheriplot
Python modules for drawing and plotting visualisation for CHERI capabilities


## Modules overview
- **plotter.py** - Main visualization tool to display capabilities and associated symbols from a chosen database.

- **Visualization.py** - Brings all of the modules together and can be used to show additional information if needed.
Gets json information from **json_importer.py**.

- **sqlite_importer.py** - Extracts capability and symbol data and dumps into json files to be read by **json_importer.py**.

- **json_importer** - Imports json information.


## Recommendations
- In **Visualization.py**, have a difference (ub-lb) of around 10 for maximum image quality if using png, if you are using svg, it doesn't matter for quality. This doesn't mean that it won't take long time to work if using a difference of over 1000.
- It takes (estimated) 95 seconds to show 1000 capabilities, it isn't linear so don't expect it to take only 190 seconds for a difference of 2000.
- It is much better to have a smaller difference and run it multiple times to make up to the same total.


## Useful Links
- Introduction to CHERI: https://www.cl.cam.ac.uk/research/security/ctsrd/pdfs/20240419-ieeesp-cheri-memory-safety.pdf

- Python modules tutorial: https://docs.python.org/3/tutorial/modules.html#

