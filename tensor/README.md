# Tensor

A Python 3 tool for valuating project-join trees with tensors.

## Running with Singularity

### Building the container

The container can be built with the following commands (`make` requires root to build the Singularity container):
```bash
sudo make
```

### Usage

Once built, example usage is:
```bash
cnfFile="../examples/flip_1_p_t2.cnf" && ../lg/lg.sif "/solvers/flow-cutter-pace17/flow_cutter_pace17 -p 100" <$cnfFile | ./tensor.sif --formula=$cnfFile --timeout=100
```

Output:
```
Parsed join tree with tensor width 5
Join Tree Time: 0.011701
Count: 0.0062255859375
Parse Formula Time: 0.00017690658569335938
Parse Join Tree Time: 0.00038242340087890625
Execution Time: 0.004231691360473633
Total Time: 0.004794120788574219
````
