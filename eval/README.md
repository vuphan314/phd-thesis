# Evaluation (Linux)

## Benchmarks

### Downloading archive to this dir (`eval`)
```bash
wget https://github.com/vuphan314/phd-thesis/releases/download/v0/benchmarks.zip
```

### Extracting downloaded archive into new dir `eval/benchmarks`
```bash
unzip benchmarks.zip
```

### Files
- Dir `benchmarks/cnf`: Boolean formulas
  - Subdir `chain`: crafted formulas, with zero quantifier alternation, in XOR-CNF
  - Subdir `app0`: application formulas, with zero quantifier alternation, in CNF
    - Subdir [`bayes`](https://henrykautz.com/Cachet/Model_Counting_Benchmarks/index.htm): inference
    - Subdir [`planning`](http://www.cril.univ-artois.fr/KC/benchmarks.html): planning
  - Subdir `app1er`: application formulas, with one quantifier alternation (exist-random), in CNF
    - Subdir [`waps`](https://github.com/meelgroup/WAPS#benchmarks): sampling
    - Subdir [`bird`](https://github.com/meelgroup/ApproxMC#how-to-cite): counting
  - Subdir `app1er`: application formulas, with one quantifier alternation (random-existl), in CNF
- Dir `benchmarks/jt`: join trees produced by our planners (HTB and LG)

--------------------------------------------------------------------------------

## Solver binaries

### Downloading archive to this dir (`eval`)
```bash
wget https://github.com/vuphan314/phd-thesis/releases/download/v0/bin.zip
```

### Extracting downloaded archive into dir `eval/bin`
```bash
unzip bin.zip
```

### Files
- `bin/abc`: [reSSAT/erSSAT](https://github.com/vuphan314/ssat)
- `bin/c2d`: C2D (from Adnan Darwiche)
- `bin/cachet`: [Cachet](https://github.com/vuphan314/cachet)
- `bin/centos.img`: CentOS image to run miniC2D
- `bin/cryptominisat5_amd64_linux_static`: [CryptoMiniSat](https://github.com/msoos/cryptominisat)
- `bin/d4`: D4 (from Lagniez Jean-Marie)
- `bin/dcssat`: DC-SSAT (from Nian-Ze Lee)
- `bin/dmc`: [our main executor](../dmc)
- `bin/gaussmaxhs`: [GaussMaxHS](https://github.com/vuphan314/gaussmaxhs)
- `bin/hgr2htree`: library for miniC2D
- `bin/htb`: [our secondary planner](../htb)
- `bin/lg.sif`: [our main planner](../lg)
- `bin/maxhs`: [MaxHS](https://github.com/vuphan314/maxhs)
- `bin/miniC2D`: [miniC2D](https://github.com/vuphan314/minic2d)
- `bin/runsolver`: [tool to control and measure resource consumption](https://github.com/utpalbora/runsolver)
- `bin/tensor.sif`: [our secondary executor](../tensor)
- `bin/uwrmaxsat`: [UWrMaxSat](https://github.com/marekpiotrow/UWrMaxSat)

--------------------------------------------------------------------------------

## WMC examples

### DPMC
```bash
./wrapper.py --cf=../examples/flip_1_p_t2.cnf --vc=0 --vj=0
```
```
c joinTreeWidth                 4
c plannerSeconds                0.0199251
c getting join tree from stdin: done
c killed planner process with pid 474466

c computing output...
c sliceWidth                    4
c threadMaxMemMegabytes         0
c maxDiagramLeaves              4
c maxDiagramNodes               15
c ------------------------------------------------------------------
s SATISFIABLE
c s type wmc
c s log10-estimate -1.44063
c s exact double prec-sci 0.0362549
c ------------------------------------------------------------------
c seconds                       0.157
```

### C2D
```bash
./wrapper.py --cf=../examples/flip_1_p_t2.cnf --prog=c2d
```
```
c s exact double prec-sci 3.62548828125e-2
c s log10-estimate -1.440633494314543
c
c Total Time: 0.0s
```

### D4
```bash
./wrapper.py --cf=../examples/flip_1_p_t2.cnf --prog=d4
```
```
c Final time: 0.000181
c
s SATISFIABLE
c s
c s log10-estimate -1.4406334943145431851433219504100391786793796759689
c s exact quadruple int 0.0362548828125
```

### Cachet
```bash
./wrapper.py --cf=../examples/flip_1_p_t2.cnf --prog=cachet
```
```
Total Run Time				0.0184

Satisfying probability			0.0362549
```

### miniC2D
```bash
./wrapper.py --cf=../examples/flip_1_p_t2.cnf --prog=mini
```
```
c wrapper tmptime 0.0004382133483886719
c wrapper tmpmb 0.000347


Constructing CNF... DONE
CNF stats:
  Vars=9 / Clauses=20
  CNF Time	0.000s
Constructing vtree (from primal graph)... DONE
Vtree stats:
  Vtree widths: con<=3, c_con=12 v_con=3
  Vtree Time	0.000s
Counting... DONE
  Learned clauses      	0
Cache stats:
  hit rate   	0.0%
  lookups    	4
  ent count  	4
  ent memory 	0.2 KB
  ht  memory 	152.6 MB
  clists     	1.0 ave, 1 max
  keys       	2.0b ave, 2.0b max, 2.0b min
Count stats:
  Count Time	0.000s
  Count 	0.036
Total Time: 0.040s
```

--------------------------------------------------------------------------------

## WSAT examples

### DPO
```bash
./wrapper.py --cf=../examples/chain_k10_n20.xcnf --vc=0 --vj=0 --er=1
```
```
c joinTreeWidth                 10
c plannerSeconds                0.0195386
c getting join tree from stdin: done
c killed planner process with pid 474861

c computing output...
c sliceWidth                    10
c threadMaxMemMegabytes         0
c maxDiagramLeaves              8
c maxDiagramNodes               76
c ------------------------------------------------------------------
s SATISFIABLE
c s type maximum
c s log10-estimate 38
c s exact double prec-sci 1e+38
c ------------------------------------------------------------------
v 00000111001010001110
c seconds                       0.175
```

### GaussMaxHS
```bash
./wrapper.py --cf=../examples/chain_k10_n20.xcnf --prog=gauss --post=1
```
```
c wrapper weightedVarCount 20
c wrapper softWeightSum 60
c wrapper softWeightOffset 0
c wrapper logBase 10

tmptime:0.001458883285522461
c wrapper tmptime 0.001458883285522461
tmpmb:0.000945
c wrapper tmpmb 0.000945

c MaxHS 3.0.0
c Instance: tempdir/chain_k10_n20.wcnf
c Dimacs Vars: 20
c Dimacs Clauses: 51
c HARD: #Clauses = 11, Total Lits = 110, Ave Len = 10
c SOFT: #Clauses = 40, Total Lits = 40, Ave Len = 1
c Total Soft Clause Weight (+ basecost): 60 (+ 0), Dimacs Top = 61
c SOFT%: 78.4314%
c #distinct weights: 2, mean = 1.5, std. dev = 0.50637, min = 1, max = 2
c Total Clauses: 51
c Parse time: 0
c Wcnf Space Required: 0MB
c ================================
c Using IBM CPLEX version 20.1.0.0 under IBM's Academic Initiative licencing program
c Solved by Disjoint phase.
logsol:38.0
sol:1e+38
o 22
```

### MaxHS
```bash
./wrapper.py --cf=../examples/chain_k10_n20.xcnf --prog=maxhs --post=1
```
```
c wrapper weightedVarCount 20
c wrapper softWeightSum 60
c wrapper softWeightOffset 0
c wrapper logBase 10

tmptime:0.0393671989440918
c wrapper tmptime 0.0393671989440918
tmpmb:0.032179
c wrapper tmpmb 0.032179

c MaxHS 4.0.0
c Instance: tempdir/chain_k10_n20.wcnf
c Instance: tempdir/chain_k10_n20.wcnf
c Dimacs Vars: 572
c Dimacs Clauses: 1821
c Dimacs Top: 61
c HARD: #Clauses = 1793, Total Lits = 4262, Ave Len = 2.3770 #units = 12
c SOFT: #Clauses = 40, Total Lits = 40, Ave Len = 1.0000
c Total Soft Clause Weight (+ basecost): 60 (+ 0)
c SOFT%: 2.1822%
c #distinct weights: 2, mean = 1.5000, std. dev = 0.5064, min = 1, max = 2
c Total Clauses: 1833
c Parse time: 0.000265
c Wcnf Space Required: 0.0000MB
c ================================
c Using IBM CPLEX version 20.1.0.0 under IBM's Academic Initiative licencing program
c Solved by disjoint phase.
logsol:38.0
sol:1e+38
o 22
```

### UWrMaxSat
```bash
./wrapper.py --cf=../examples/chain_k10_n20.xcnf --prog=uwr --post=1
```
```
c wrapper weightedVarCount 20
c wrapper softWeightSum 60
c wrapper softWeightOffset 0
c wrapper logBase 10

tmptime:0.0399625301361084
c wrapper tmptime 0.0399625301361084
tmpmb:0.032179
c wrapper tmpmb 0.032179

c Using COMiniSatPS SAT solver by Chanseok Oh (2016)
logsol:37.0
sol:1e+37
o 23
logsol:38.0
sol:1e+38
o 22
```

--------------------------------------------------------------------------------

## WPMC examples

### ProCount
```bash
./wrapper.py --cf=../examples/s27_3_2-re.cnf --vc=0 --vj=0 --pc=1
```
```
c joinTreeWidth                 9
c plannerSeconds                0.0201491
c getting join tree from stdin: done
c killed planner process with pid 477204

c computing output...
c sliceWidth                    9
c threadMaxMemMegabytes         0
c maxDiagramLeaves              2
c maxDiagramNodes               35
c ------------------------------------------------------------------
s SATISFIABLE
c s type pwmc
c s log10-estimate -0.259428
c s exact double prec-sci 0.550265
c ------------------------------------------------------------------
c seconds                       0.204
```

### D4p
```bash
./wrapper.py --cf=../examples/s27_3_2-re.cnf --prog=d4p
```
```
c Final time: 0.000365
c
s SATISFIABLE
c s
c s log10-estimate -0.25942836852589153125979968118256585700059767851413
c s exact quadruple int 0.5502646723411869051101368345191515532610414133245
```

### projMC
```bash
./wrapper.py --cf=../examples/s27_3_2-re.cnf --prog=projmc
```
```
c [PROJMC] Final time: 0.014924
c
s 0.550265
```

### reSSAT
```bash
./wrapper.py --cf=../examples/s27_3_2-re.cnf --prog=ressat
```
```
c wrapper tmptime 0.0006024837493896484
c wrapper tmpmb 0.000763

[INFO] Input sdimacs file: tempdir/s27_3_2-re.sdimacs
[INFO] Starting analysis ...
[INFO] Stopping analysis ...
[INFO] # of UNSAT cubes: 10
[INFO] # of   SAT cubes: 17

==== Solving results ====

  > Satisfying probability: 5.502647e-01
  > Time =     0.01 sec
```

--------------------------------------------------------------------------------

## ERSAT examples

### DPER
```bash
./wrapper.py --cf=../examples/s27_3_2-er.cnf --vc=0 --vj=0 --pc=1 --er=1
```
```
c joinTreeWidth                 4
c plannerSeconds                0.0203482
c getting join tree from stdin: done
c killed planner process with pid 477471

c computing output...
c sliceWidth                    4
c threadMaxMemMegabytes         0
c maxDiagramLeaves              6
c maxDiagramNodes               15
c ------------------------------------------------------------------
s SATISFIABLE
c s type maximum
c s log10-estimate -0.74136
c s exact double prec-sci 0.181401
c ------------------------------------------------------------------
v 11111111110010001111
c seconds                       0.154
```

### erSSAT
```bash
./wrapper.py --cf=../examples/s27_3_2-er.cnf --prog=erssat
```
```
c wrapper tmptime 0.0006146430969238281
c wrapper tmpmb 0.000763

[INFO] Input sdimacs file: tempdir/s27_3_2-er.sdimacs
[INFO] Starting analysis ...
[INFO] Stopping analysis ...

==== Solving results ====

  > Satisfying probability: 1.814011e-01
  > Time =     0.00 sec
```

### DC-SSAT
```bash
./wrapper.py --cf=../examples/s27_3_2-er.cnf --prog=dcssat
```
```
c wrapper tmptime 0.0006134510040283203
c wrapper tmpmb 0.000763



solve time:              = 0.000349998
rebuild/print time:      = 2.7895e-05
   total time:           = 0.000377893

Pr[SAT]                  =   0.181401
```

--------------------------------------------------------------------------------

## Data

### Downloading archive to this dir (`eval`)
```bash
wget https://github.com/vuphan314/phd-thesis/releases/download/v0/data.zip
```

### Extracting downloaded archive into dir `eval/data`
```bash
unzip data.zip
```

### Files
- Dir `data/r`: WMC
  - Subdir `dual/dpmc/dmc`: main executor
    - Subdir `lg/flow`: main planner with default treewidth cap of 100
- Dir `data/re`: WPMC
- Dir `data/er`: ERSAY
- Dir `data/e`: WSAT
  - Subdir `chain`: crafted formulas, with zero quantifier alternation, in XOR-CNF
  - Subdir `app0`: application formulas, with zero quantifier alternation, in CNF

--------------------------------------------------------------------------------

## [Jupyter notebook](phd.ipynb)
- The `Figures` section has ilustrations used in the thesis.
- Run all cells again to re-generate these figures from dir `data`.
