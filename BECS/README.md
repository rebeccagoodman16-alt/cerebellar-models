# BECS

This folder is the working output folder for the cerebellar model run.

Use the Miniconda command shims, because the system PATH currently finds broken Python 3.14 shims first:

```bash
/opt/miniconda3/bin/python BECS/generate_config.py
/opt/miniconda3/bin/bsb compile BECS/circuit_reconstruction_only.yaml -v4 --clear
```

`circuit_reconstruction_only.yaml` can compile the structure without NEST. `circuit.yaml` includes the configured `nest_basal_activity` simulation and needs NEST installed before BSB can load it.
