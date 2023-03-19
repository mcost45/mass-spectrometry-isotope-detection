# Mass Spectrometry Isotope Detection

## Bromide & Chloride Isotope Detection (CSV Input/Output)

### Overview

This implementation detects potential bromide & chloride isotopes by analysing the differences between data point mass
to charge ratios and intensities, accounting for margin of error. Detection can be filtered by a configurable minimum
intensity value.

Data is input/output through CSV files. **It is expected that the provided input data is sorted by ascending 'm/z'
ratios.** `config.py` provides configurable options for the detection process.

### Theory

Both bromine and chlorine have two stable isotopes, each isotope with a relative abundance. When comparing the data
points, we are looking for 'm/z' deltas and intensity ratios matching the characteristics of these isotopes. A 'match'
between two data points indicates a potential pair of stable isotopes type one and type two, which then may be
investigated further.

### Performance

Where possible, data will be split into chunks to be multi-processed (depending on if suitable boundaries can be found).
It runs in O(n^2) time. Practically, worst case performance will be when the minimum intensity value is very low,
where 'm/z' distances likely to be less sparse and it is more difficult to chunk the data. Binary searching is also
relied upon for efficient iteration.

## Dependencies

- `python@3.10`
- `pyarrow@11.0.0`