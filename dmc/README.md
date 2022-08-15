# DMC (diagram model counter)
Given a join tree `T` for an XOR-CNF formula, DMC solves:
- weighted model counting (WMC)
- weighted projected model counting (WPMC); `T` must be graded
- weighted SAT (WSAT), also called Boolean MPE
- exist-random SAT (ERSAT); `T` must be graded

--------------------------------------------------------------------------------

## Installation (Linux)

### Prerequisites
#### External libraries
- automake 1.16
- cmake 3.16
- g++ 11.2
- gmp 6.2
- python3 3.8
#### [Included libraries](../addmc/libraries/)
- [cryptominisat 5.8](https://github.com/msoos/cryptominisat)
- [cudd 3.0](https://github.com/vuphan314/cudd)
- [cxxopts 2.2](https://github.com/jarro2783/cxxopts)
- [sylvan 1.5](https://github.com/vuphan314/sylvan)

### Command to build statically linked executable
```bash
make dmc
```

--------------------------------------------------------------------------------

## Examples

### Showing options
#### Command
```bash
./dmc
```
#### Output
```
Diagram Model Counter (reads join tree from stdin)
Usage:
  dmc [OPTION...]

      --cf arg  CNF file path; string (required)
      --wc arg  weighted counting: 0, 1; int (default: 1)
      --pc arg  projected counting (graded join tree): 0, 1; int (default: 0)
      --er arg  exist-random SAT (max-sum instead of sum-max): 0, 1; int (default: 0)
      --dp arg  diagram package: c/CUDD, s/SYLVAN; string (default: c)
      --lc arg  logarithmic counting [needs dp_arg = c]: 0, 1; int (default: 0)
      --lb arg  log10(bound) for pruning [needs pc_arg = 0, er_arg = 1, lc_arg = 1]; float (default: -inf)
      --tm arg  threshold model for pruning [needs pc_arg = 0, er_arg = 1, lc_arg = 1, lb_arg = -inf]; string
                (default: "")
      --sp arg  SAT pruning with CryptoMiniSat [needs pc_arg = 0, er_arg = 1, lc_arg = 1, lb_arg = -inf, tm_arg =
                ""]: 0, 1; int (default: 0)
      --mf arg  maximizer format [needs er_arg = 1, dp_arg = c]: 0/NEITHER, 1/SHORT, 2/LONG, 3/DUAL; int (default: 0)
      --mv arg  maximizer verification [needs mf_arg > 0]: 0, 1; int (default: 0)
      --sm arg  substitution-based maximization [needs wc_arg = 0, mf_arg > 0]: 0, 1; int (default: 0)
      --pw arg  planner wait duration minimum (in seconds); float (default: 0.0)
      --tc arg  thread count [or 0 for hardware_concurrency value]; int (default: 1)
      --ts arg  thread slice count [needs dp_arg = c]; int (default: 1)
      --rs arg  random seed; int (default: 0)
      --dv arg  diagram var order: 0/RANDOM, 1/DECLARATION, 2/MOST_CLAUSES, 3/MIN_FILL, 4/MCS, 5/LEX_P, 6/LEX_M
                (negatives for inverse orders); int (default: 4)
      --sv arg  slice var order [needs ts_arg > 1]: 0/RANDOM, 1/DECLARATION, 2/MOST_CLAUSES, 3/MIN_FILL, 4/MCS,
                5/LEX_P, 6/LEX_M, 7/BIGGEST_NODE, 8/HIGHEST_NODE (negatives for inverse orders); int (default: 7)
      --ms arg  memory sensitivity (in MB) for reporting usage [needs dp_arg = c]; float (default: 1e3)
      --mm arg  maximum memory (in MB) for unique table and cache table combined [or 0 for unlimited memory with
                CUDD]; float (default: 4e3)
      --tr arg  table ratio [needs dp_arg = s]: log2(unique_size/cache_size); int (default: 1)
      --ir arg  init ratio for tables [needs dp_arg = s]: log2(max_size/init_size); int (default: 10)
      --mp arg  multiple precision [needs dp_arg = s]: 0, 1; int (default: 0)
      --jp arg  join priority: a/ARBITRARY_PAIR, b/BIGGEST_PAIR, s/SMALLEST_PAIR; string (default: s)
      --vc arg  verbose CNF processing: 0, 1, 2, 3; int (default: 0)
      --vj arg  verbose join-tree processing: 0, 1, 2 (default: 0)
      --vp arg  verbose profiling: 0, 1, 2; int (default: 0)
      --vs arg  verbose solving: 0, 1, 2; int (default: 0)
  -h            help
```

### Solving WMC given CNF formula from file and join tree from planner
#### Command
```bash
cnfFile="../examples/flip_1_p_t2.cnf" && ../lg/lg.sif "/solvers/flow-cutter-pace17/flow_cutter_pace17 -p 100" <$cnfFile | ./dmc --cf=$cnfFile
```
#### Output
```
c joinTreeWidth                 4
c plannerSeconds                0.0206429
c getting join tree from stdin: done
c killed planner process with pid 479506

c computing output...
c sliceWidth                    4
c threadMaxMemMegabytes         4000
c maxDiagramLeaves              4
c maxDiagramNodes               15
c ------------------------------------------------------------------
s SATISFIABLE
c s type wmc
c s log10-estimate -1.44063
c s exact double prec-sci 0.0362549
c ------------------------------------------------------------------
c seconds                       0.183
```

### Solving WPMC given CNF formula from file and graded join tree from file
#### Command
```bash
./dmc --cf=../examples/phi.cnf --pc=1 <../examples/phi.jt
```
#### Output
```
c joinTreeWidth                 2
c plannerSeconds                0
c getting join tree from stdin: done

c computing output...
c sliceWidth                    2
c threadMaxMemMegabytes         4000
c maxDiagramLeaves              2
c maxDiagramNodes               5
c ------------------------------------------------------------------
s SATISFIABLE
c s type pwmc
c s log10-estimate -0.39794
c s exact double prec-sci 0.4
c ------------------------------------------------------------------
c seconds                       0.029
```

### Solving WSAT given XOR-CNF formula from file and join tree from planner
#### Command
```bash
cnfFile="../examples/chain_k10_n20.xcnf" && ../lg/lg.sif "/solvers/flow-cutter-pace17/flow_cutter_pace17 -p 100" <$cnfFile | ./dmc --cf=$cnfFile --er=1 --lc=1 --mf=1
```
#### Output
```
c joinTreeWidth                 10
c plannerSeconds                0.0205073
c getting join tree from stdin: done
c killed planner process with pid 479747

c computing output...
c sliceWidth                    10
c threadMaxMemMegabytes         4000
c maxDiagramLeaves              8
c maxDiagramNodes               76
c ------------------------------------------------------------------
s SATISFIABLE
c s type maximum
c s log10-estimate 38
c s exact double prec-sci 1e+38
c ------------------------------------------------------------------
v 00000111001010001110
c seconds                       0.189
```

### Solving ERSAT given CNF formula from file and graded join tree from planner
#### Command
```bash
cnfFile="../examples/s27_3_2-er.cnf" && ../lg/lg.sif "/solvers/flow-cutter-pace17/flow_cutter_pace17 -p 100" <$cnfFile | ./dmc --cf=$cnfFile --pc=1 --er=1 --mf=1
```
#### Output
```
c joinTreeWidth                 4
c plannerSeconds                0.0207061
c getting join tree from stdin: done
c killed planner process with pid 479923

c computing output...
c sliceWidth                    4
c threadMaxMemMegabytes         4000
c maxDiagramLeaves              6
c maxDiagramNodes               15
c ------------------------------------------------------------------
s SATISFIABLE
c s type maximum
c s log10-estimate -0.74136
c s exact double prec-sci 0.181401
c ------------------------------------------------------------------
v 11111111110010001111
c seconds                       0.18
```
