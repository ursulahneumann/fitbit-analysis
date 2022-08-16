# Project Title
Short description of project.

## Table of Contents
0) Usage (Temporary)<br>
1) Project Motivation <br>
2) File Description <br>
3) Libraries Required <br>
4) Summary of Results <br>
5) Licensing and Acknowledgements <br>

## Usage (Temporary)
TODO this catchall usage section to be moved.

```python
# From main project folder
from core import api, util
from core.constants import CONFIG_FILE

fitbit = api.FitbitAPI(util.load_tokens(CONFIG_FILE))
# JSON data as dict
data = fitbit.hr.by_date()
print(data)
```

## Project Motivation
Rationale for doing this project.

## File Descriptions

**README.md** - This file, describing the contents of this repo.

**filename.R** - R script containing something.

## Libraries Required

**Rpackage1** - Rpackage for some purpose.

## Summary of Results
Summarize results here.

## Licenses and Acknowledgements
Any licenses, references to where data was taken from, etc.