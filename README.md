# DPMC/ProCount/DPO/DPER
- We provide four exact solvers that support XOR-CNF formulas.
  - DPMC solves *weighted model counting (WMC)*.
  - ProCount solves *weighted projected model counting (WPMC)*.
  - DPO solves *weighted SAT (WSAT)*, i.e., Boolean MPE.
  - DPER solves *exist-random SAT (ERSAT)*.
- Each of these four solvers is a combination of a planner and an executor.
  - A planner produces a **project-join tree** `T` from an XOR-CNF formula F.
  - An executor traverses `T` to computes a solution of F.
  - For WPMC and ERSAT, `T` must be **graded**.
- Two planners are available.
  - [HTB](./htb/) uses constraint-programming heuristics.
  - [LG](./lg/) uses tree decomposers.
- Two executors are available.
  - [DMC](./dmc/) uses *algebraic decision diagrams (ADDs)*.
  - [Tensor](./tensor/) uses tensors and only solves WMC on pure CNF.
- Developers:
  - Vu Phan: HTB and DMC
  - Jeffrey Dudek: LG and Tensor

--------------------------------------------------------------------------------

## Cloning this repository
```bash
https://github.com/vuphan314/phd-thesis
```

--------------------------------------------------------------------------------

## [Examples](./examples/)

--------------------------------------------------------------------------------

## Acknowledgment
- [ADDMC](https://github.com/vardigroup/ADDMC): Dudek, Phan, Vardi
- [BIRD](https://github.com/meelgroup/approxmc): Soos, Meel
- [Cachet](https://cs.rochester.edu/u/kautz/Cachet): Sang, Beame, Kautz
- [CryptoMiniSat](https://github.com/msoos/cryptominisat): Soos
- [CUDD package](https://github.com/ivmai/cudd): Somenzi
- [CUDD visualization](https://davidkebo.com/cudd#cudd6): Kebo
- [cxxopts](https://github.com/jarro2783/cxxopts): Beck
- [DPMC](https://github.com/vardigroup/DPMC): Dudek, Phan, Vardi
- [FlowCutter](https://github.com/kit-algo/flow-cutter-pace17): Strasser
- [htd](https://github.com/mabseher/htd): Abseher, Musliu, Woltran
- [miniC2D](http://reasoning.cs.ucla.edu/minic2d): Oztok, Darwiche
- [Model Counting Competition](https://mccompetition.org): Hecher, Fichte
- [pmc](http://www.cril.univ-artois.fr/KC/pmc.html): Lagniez, Marquis
- [SlurmQueen](https://github.com/Kasekopf/SlurmQueen): Dudek
- [Sylvan](https://trolando.github.io/sylvan): van Dijk
- [Tamaki](https://github.com/TCS-Meiji/PACE2017-TrackA): Tamaki
- [TensorOrder](https://github.com/vardigroup/TensorOrder): Dudek, Duenas-Osorio, Vardi
- [WAPS](https://github.com/meelgroup/WAPS): Gupta, Sharma, Roy, Meel
