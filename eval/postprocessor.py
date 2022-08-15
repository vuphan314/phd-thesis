#!/usr/bin/env python3

import functools
import math
import os
import sys

import click

################################################################################

cerr = print = functools.partial(print, flush=True)

PLAN_PHASE = 'plan'
EXEC_PHASE = 'exec'
DUAL_PHASE = 'dual'

DPMC = 'dpmc'
CACHET = 'cachet'
C2D = 'c2d'
MINI = 'mini'
D4 = 'd4'
D4P = 'd4p'
PROJMC = 'projmc'
RESSAT = 'ressat'
ERSSAT = 'erssat'
DCSSAT = 'dcssat'
GAUSS = 'gauss' # GaussMaxHS
MAXHS = 'maxhs'
UWR = 'uwr' # UWrMaxSat
CMS = 'cms' # CryptoMiniSat

################################################################################

jtWidths = []
jtTimes = []

def printOut(key, value): # to .out file
    print(f'{key}:{value}')

def printJtWidthLine(line): # modifies jtWidths
    jtWidth = int(line.split()[-1])
    jtWidths.append(jtWidth)
    printOut(f'width{len(jtWidths)}', jtWidth)

def printJtTimeLine(line): # modifies jtTimes
    jtTime = float(line.split()[-1])
    jtTimes.append(jtTime)
    printOut(f'plantime{len(jtTimes)}', jtTime)

def printJts():
    assert len(jtWidths) >= len(jtTimes), (jtWidths, jtTimes) # TENSOR
    if jtWidths:
        printOut('plans', len(jtWidths))
        printOut('width', jtWidths[-1])
    if jtTimes:
        printOut('plantime', jtTimes[-1])

def printSol(num):
    try:
        num = float(num)
        if math.isfinite(num):
            printOut('sol', num)
    except OverflowError: # int too large to convert to float
        pass

def printLogSol(exponent):
    printOut('logsol', float(exponent))

def printSolAndLogSol(sol):
    sol = float(sol)
    printSol(sol)
    if sol:
        printLogSol(math.log10(sol))
    else:
        pass
        # printLogSol('-inf') # turns logsol column into str instead of float

def printDpmcLine(line, phase): # modifies jtWidths and jtTimes
    words = line.split()

    if line.startswith('c joinTreeWidth '): # LG/HTB/DMC
        printJtWidthLine(line)
    elif line.startswith('Parsed join tree with tensor width '): # TENSOR
        printJtWidthLine(line)

    elif line.startswith('c seconds ') and phase == PLAN_PHASE: # LG/HTB
        printJtTimeLine(line)
    elif line.startswith('c plannerSeconds '): # DMC
        printJtTimeLine(line)
    elif line.startswith('Join Tree Time: '): # TENSOR
        printJtTimeLine(line)

    elif line.startswith('c apparentVarCount '): # HTB/DMC
        printOut('vars', words[-1])
    elif line.startswith('c apparentClauseCount '):
        printOut('clauses', words[-1])
    elif line.startswith('c xorClauseCount '):
        printOut('xors', words[-1])
    elif line.startswith('c clauseSizeMean '):
        printOut('meanlits', words[-1])
    elif line.startswith('c clauseSizeMax '):
        printOut('maxlits', words[-1])

    elif line.startswith('c diagramVarSeconds '): # DMC
        printOut('dvtime', words[-1])
    elif line.startswith('c logBound '):
        printOut('logbound', words[-1])
    elif line.startswith('c prunedDiagrams '):
        printOut('prunecount', words[-1])
    elif line.startswith('c pruningSeconds '):
        printOut('prunetime', words[-1])
    elif line.startswith('c maxDiagramLeaves '):
        printOut('ddleaves', words[-1])
    elif line.startswith('c maxDiagramNodes '):
        printOut('ddnodes', words[-1])
    elif line.startswith('c apparentSolution '):
        printOut('applogsol', words[-1])
    elif line.startswith('c solutionMatch '):
        printOut('match', words[-1])
    elif line.startswith('c maximizerVerificationSeconds '):
        printOut('mvtime', words[-1])

    elif line.startswith('Count: '): # TENSOR
        printSolAndLogSol(words[1])

def printMaximizer(words):
    if len(words) > 1: # long format
        assignment = {}
        for lit in map(int, words):
            if  lit:
                assignment[abs(lit)] = str(int(lit > 0))
        varList = range(1, max(assignment) + 1)
        assert assignment.keys() == set(varList), (assignment, varList)
        bitString = ''.join([assignment[var] for var in varList])
    else: # short format
        bitString = words[0]

    varCount = len(bitString)
    if varCount > 2e5:
        bitString = '-1'

    printOut('model', bitString)
    printOut('modelvars', varCount)

def printMaxSatOptimum(optimum, weightedVarCount, softWeightSum, softWeightOffset, logBase):
    exponent = softWeightSum - optimum - weightedVarCount * softWeightOffset
    if exponent.is_integer():
        exponent = int(exponent)

    printLogSol(exponent)
    printSol(logBase**exponent)

def printCtrlLine(line, phase):
    try:
        (k, v) = line.split('=')
        if k == 'WCTIME':
            time = float(v)
            if phase == EXEC_PHASE:
                printOut('exectime', time)
                if jtTimes:
                    time += jtTimes[-1]
            printOut('time', time)
            if jtTimes:
                printOut('plantimerate', jtTimes[-1] / time)
        elif k == 'MAXMM': # in KB; determines TIMEOUT (must not use MAXVM or MAXRSS)
            printOut('mem', float(v) / 1e6)
        elif k == 'TIMEOUT':
            printOut('timeout', int(v == 'true'))
        elif k == 'MEMOUT':
            printOut('memout', int(v == 'true'))
        elif k == 'EXITSTATUS':
            printOut('exit', v)
    except ValueError as e:
        print(line)
        raise e

@click.command(
    context_settings={
        'help_option_names': ['-h', '--help'],
        'show_default': True,
    },
    help='Standard input will be read.',
)
@click.option('--show',
    default=0,
    help='outer vars',
)
def main(show):
    prog = None
    phase = None
    weightedVarCount = None
    softWeightSum = None
    softWeightOffset = None
    logBase = None

    ctrlStarted = False
    for line in sys.stdin:
        line = line.rstrip()
        words = line.split()

        if '# WCTIME: wall clock time in seconds' in line: # ctrl
            assert not ctrlStarted
            ctrlStarted = True
            printJts()
        elif ctrlStarted and not line.startswith('# '):
            printCtrlLine(line, phase)

        elif line.startswith('c wrapper '):
            (key, value) = words[2:]
            if key == 'cf':
                printOut('root', os.path.splitext(os.path.basename(value))[0])
                if show:
                    for line in open(value):
                        if line.startswith('c p show '):
                            assert line.endswith(' 0\n'), line
                            printOut('show', len(line.split()) - 4)
                        elif line.startswith('c p weight '):
                            break
            elif key == 'prog':
                prog = value
            elif key == 'phase':
                phase = value
            elif key == 'weightedVarCount':
                weightedVarCount = int(value)
            elif key == 'softWeightSum':
                softWeightSum = float(value)
            elif key == 'softWeightOffset':
                softWeightOffset = int(value)
            elif key == 'logBase':
                logBase = int(value)
            else:
                printOut(key, value)

        elif line.startswith('c s log10-estimate '): # multiple programs
            printLogSol(words[-1])
        elif line.startswith('c s exact ') and words[3] != 'arb':
            printSol(words[-1])

        elif line.startswith('s mc '):
            printSolAndLogSol(words[-1])

        elif line.startswith('Satisfying probability\t') and prog == CACHET:
            printSolAndLogSol(words[-1])

        elif line.startswith('  Count \t') and prog == MINI:
            printSolAndLogSol(words[1])

        elif line.startswith('s '):
            if prog == CMS:
                printSol(int(words[1] == 'SATISFIABLE'))
            elif prog in {D4, D4P, PROJMC} and words[1] != 'SATISFIABLE': # d4mc21 == 0
                printSolAndLogSol(words[-1])

        elif line.startswith('  > Satisfying probability: ') and prog in {RESSAT, ERSSAT}:
            printSolAndLogSol(words[-1])

        elif line.startswith('Pr[SAT] ') and prog == DCSSAT:
            printSolAndLogSol(words[-1])

        elif line.startswith('o ') and prog in {GAUSS, MAXHS, UWR}:
            printMaxSatOptimum(float(words[1]), weightedVarCount, softWeightSum, softWeightOffset, logBase)

        elif line.startswith('v '): # multiple programs
            pass
            # printMaximizer(words[1:]) # slow for SQL

        elif prog == DPMC:
            printDpmcLine(line, phase)

        if line != 'c Non-int weights detected Resetting cplex absolute gap to zero': # MAXHS
            print(line, file=sys.stderr)

    if not ctrlStarted: # in case ctrl fails
        printJts()

if __name__ == '__main__':
    main()
