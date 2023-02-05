# Mass Spectrometry Isotope Detection

## Bromide & Chloride Isotope Detection (CSV Input/Output)

### Overview

This implementation detects potential bromide & chloride isotopes by analysing the differences between data point mass
to charge ratios, accounting for margin of error. Detection can be filtered by a configurable minimum intensity value.

Data is input/output through CSV files. **It is expected that the provided input data is sorted by ascending m/z
ratios.** `config.py` provides configurable options for the detection process.

### Performance

Where possible, data will be split into chunks to be multi-processed (depending on if suitable boundaries can be found,
distances between m/z points). Practically, worst case performance (O(n^2)) will be when the minimum intensity value is
set to
0 (m/z distances likely to be less sparse). Binary searching is also relied upon for efficient iteration.

## Dependencies

- `python@3.10`
- `pyarrow@11.0.0`