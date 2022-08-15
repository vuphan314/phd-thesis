#!/usr/bin/env python3

import functools
import math
import operator
import os
import subprocess
import time

from pyeda.boolalg import expr
import click

################################################################################

cerr = print = functools.partial(print, flush=True)

def printWrapperLine(postProcess, key='', value=''): # to postprocessor.py
    line = f'c wrapper {key} {value}' if key or value else ''
    line += '\n'
    if postProcess:
        postProcess.stdin.write(line.encode())
        postProcess.stdin.flush()
    else:
        print(line, end='')

def printTempTimeStats(postProcess, startTime, filePath):
    printWrapperLine(postProcess, 'tmptime', time.time() - startTime)
    printWrapperLine(postProcess, 'tmpmb', os.path.getsize(filePath) / 1e6)
    printWrapperLine(postProcess)

def makeDir(dirPath):
    if dirPath:
        os.makedirs(dirPath, exist_ok=True)

def alignFloat(num, decDigits):
    assert isinstance(num, float), num
    return str(int(num)) if num.is_integer() else f'{num:.{decDigits}f}'

class Assignment(dict): # int |-> bool
    def __init__(self, string):
        if ' ' in string: # long format
            for lit in map(int, string.split()):
                self[abs(lit)] = bool(lit > 0)
        else: # short format
            for i in range(len(string)):
                self[i + 1] = bool(int(string[i]))

    def evalLit(self, lit):
        assert lit, lit
        return (lit > 0) == self[abs(lit)]

class Lit(int):
    PYEDA_VAR = 'v'

    @staticmethod
    def getLits(var):
        return map(Lit, [-var, var])

    def symbolizeLit(self):
        assert self, self
        var = expr.exprvar(self.PYEDA_VAR, abs(self))
        return var if self > 0 else ~var

    def alignSign(self):
        return f'{" " if self > 0 else ""}{self}'

class Clause(list):
    def __init__(self, lits, xorFlag):
        super().__init__(map(Lit, lits))
        self.xorFlag = xorFlag

    def evalClause(self, assignment):
        vals = [assignment.evalLit(lit) for lit in self]
        val = functools.reduce(operator.xor if self.xorFlag else operator.or_, vals)
        return val

    def addClause(self, solver):
        if self.xorFlag:
            lhs = []
            rhs = True
            for lit in self:
                lhs.append(abs(lit))
                if lit < 0:
                    rhs = not rhs
            solver.add_xor_clause(lhs, rhs)
        else:
            solver.add_clause(self)

    def symbolizeClause(self):
        assert self.xorFlag, self.xorFlag
        return expr.Xor(*map(Lit.symbolizeLit, self))

    def getLitsLine(self):
        return f'{" ".join(map(Lit.alignSign, self))} 0\n'

    def alignX(self):
        return 'x' if self.xorFlag else ' '

    def getClauseLine(self):
        return f'{self.alignX()} {self.getLitsLine()}'

class CnfFormula:
    MOVE = 'mkdir -p bad && mv -t bad'

    def __init__(self, cf='', wc=True, pc=False, er=False, weightPairSum=0.0):
        self.cf = cf
        self.wc = wc
        self.pc = pc
        self.er = er
        self.weightPairSum = weightPairSum

        self.declaredVarCount = 0
        self.apparentVars = set()
        self.outerVars = set()
        self.litWeights = {}
        self.clauses = []

    def printCheck(self, message, prefix='#'):
        print(f'  {prefix} {self.cf} # {message}')

    def evalFormula(self, assignment):
        vals = [clause.evalClause(assignment) for clause in self.clauses]
        return functools.reduce(operator.and_, vals)

    def solve(self):
        import pycryptosat
        solver = pycryptosat.Solver()
        for clause in self.clauses:
            clause.addClause(solver)
        return solver.solve()[0]

    def getLitAndAuxVarsFromDisjunct(self, disjunct):
        if isinstance(disjunct, expr.Complement):
            assert len(disjunct.usupport) == 1, disjunct.usupport
            (var, auxVars) = self.getLitAndAuxVarsFromDisjunct(disjunct.top)
            assert var > 0, var
            return (-var, auxVars)
        else:
            assert isinstance(disjunct, expr.Variable), disjunct
            (varIndex,) = disjunct.indices
            if disjunct.name == Lit.PYEDA_VAR:
                assert varIndex > 0, varIndex
                auxVars = set()
            else:
                assert disjunct.name == 'aux', disjunct.name
                assert varIndex >= 0, varIndex
                varIndex += self.declaredVarCount + 1
                auxVars = {varIndex}
            return (varIndex, auxVars)

    def getClauseAndAuxVarsFromConjunct(self, conjunct):
        if isinstance(conjunct, expr.OrOp):
            clause = []
            auxVars = set()
            for disjunct in conjunct.xs:
                (lit, vars) = self.getLitAndAuxVarsFromDisjunct(disjunct)
                clause.append(lit)
                auxVars.update(vars)
            return (clause, auxVars)
        else:
            (lit, auxVars) = self.getLitAndAuxVarsFromDisjunct(conjunct)
            return ([lit], auxVars)

    def getClausesAndAuxVarsFromConjunction(self, conjunction):
        assert isinstance(conjunction, expr.AndOp), conjunction
        assert conjunction.is_cnf(), conjunction
        clauses = []
        auxVars = set()
        for conjunct in conjunction.xs:
            (clause, vars) = self.getClauseAndAuxVarsFromConjunct(conjunct)
            clauses.append(Clause(clause, xorFlag=False))
            auxVars.update(vars)
        return (clauses, auxVars)

    def encodeTseitin(self):
        orClauses = []
        xorClauses = []
        for clause in self.clauses:
            if clause.xorFlag:
                xorClauses.append(clause)
            else:
                orClauses.append(clause)
        e = expr.And(*map(Clause.symbolizeClause, xorClauses))
        e = e.tseitin()
        (clauses, auxVars) = self.getClausesAndAuxVarsFromConjunction(e)
        self.clauses = orClauses + clauses
        self.declaredVarCount += len(auxVars)
        self.checkFormula()

    def getDeclaredVars(self): # returns range
        return range(1, self.declaredVarCount + 1)

    def getMaxClauseSize(self):
        return max(map(len, self.clauses)) if self.clauses else -math.inf

    def getMinWeight(self):
        return min(self.litWeights.values())

    def fillOuterVars(self):
        assert self.outerVars.issubset(self.getDeclaredVars()), self.cf
        if self.pc:
            if not self.outerVars:
                self.printCheck('no outer var', 'rm')
            if self.outerVars == set(self.getDeclaredVars()):
                self.printCheck('all outer vars')
        else:
            # assert not self.outerVars, (self.outerVars, self.cf)
            self.outerVars = set(self.getDeclaredVars())

    def fillLitWeights(self):
        for var in self.getDeclaredVars():
            if var in self.litWeights:
                if -var not in self.litWeights:
                    self.litWeights[-var] = 1 - self.litWeights[var]
            elif -var in self.litWeights:
                self.litWeights[var] = 1 - self.litWeights[-var]
            else:
                self.litWeights[var] = self.litWeights[-var] = 1.0

    def isWeightedVar(self, var):
        return not (
            var in self.litWeights or -var in self.litWeights
        ) or not self.litWeights[var] == self.litWeights[-var] == 1

    def getWeightedVars(self):
        return {var for var in self.getDeclaredVars() if self.isWeightedVar(var)}

    def hasDiffWeightPair(self, var):
        return self.litWeights[var] != self.litWeights[-var]

    def checkWeightPairSum(self, var):
        if self.weightPairSum:
            s = self.litWeights[var] + self.litWeights[-var]
            if s != self.weightPairSum:
                self.printCheck(f'lit weights of var {var} sum to {s} != {self.weightPairSum}')

    def checkLitWeights(self):
        weightedVars = self.getWeightedVars()
        if self.wc:
            diffWeightFlag = False
            for weightedVar in weightedVars:
                self.checkWeightPairSum(weightedVar)
                if self.hasDiffWeightPair(weightedVar):
                    diffWeightFlag = True
            if not diffWeightFlag:
                self.printCheck('no var has diff lit weights', 'rm')
        else:
            if weightedVars:
                self.printCheck(f'weighted vars: {weightedVars}')

    def checkOuterVarsVsLitWeights(self):
        if self.wc and self.pc:
            if self.er:
                assert set(self.getDeclaredVars()) - self.outerVars == self.getWeightedVars(), self.cf
            else:
                weightedVars = self.getWeightedVars()
                if self.outerVars != weightedVars:
                    self.printCheck(f'outerVars == {self.outerVars} != {weightedVars} == weightedVars')

    def checkVar(self, var):
        assert isinstance(var, int), var
        assert 0 < var <= self.declaredVarCount, (var, self.cf)

    def checkLit(self, lit):
        self.checkVar(abs(lit))

    def parseVar(self, word):
        var = int(word)
        self.checkVar(var)
        return var

    def parseLit(self, word):
        lit = int(word)
        self.checkLit(lit)
        lit = Lit(lit)
        return lit

    def readCnfLine(self, words):
        assert words[1] == 'cnf', self.cf
        declaredVarCount = int(words[2])
        assert declaredVarCount, self.cf
        if self.declaredVarCount:
            assert self.declaredVarCount == declaredVarCount, self.cf
        else:
            self.declaredVarCount = declaredVarCount

    def readClauseLine(self, words): # updates apparentVars
        if len(words) < 2:
            self.printCheck(f'clause has too few literals: {words}', self.MOVE)
            return

        if words[-1] != '0':
            self.printCheck(f'clause does not end with 0: {words}', self.MOVE)
            return

        xorFlag = False
        if words[0].startswith('x'):
            xorFlag = True
            if words[0] == 'x':
                words = words[1:]
            else:
                words[0] = words[0][1:]

        lits = []
        for word in words[:-1]:
            lit = self.parseLit(word)
            self.apparentVars.add(abs(lit))
            lits.append(lit)
        self.clauses.append(Clause(lits, xorFlag))

    def checkFormula(self):
        self.fillOuterVars()
        self.fillLitWeights()
        self.checkLitWeights()
        self.checkOuterVarsVsLitWeights()
        if not self.clauses:
            self.printCheck('no clause', self.MOVE)

    def readCnfFile(self):
        for line in open(self.cf):
            line = line.strip()
            words = line.split()
            if line.startswith('p '):
                self.readCnfLine(words)
            elif line.startswith('c p show '):
                for i in range(3, len(words)):
                    word = words[i]
                    if word == '0':
                        assert i == len(words) - 1, self.cf
                    else:
                        self.outerVars.add(self.parseVar(word))
            elif line.startswith('c p weight '):
                lit = self.parseLit(words[3])
                weight = float(words[4])
                self.litWeights[lit] = weight
            elif line and not line.startswith('c'):
                self.readClauseLine(words)
        self.checkFormula()

    def readBayesFile(self):
        for line in open(self.cf):
            line = line.strip()
            words = line.split()
            if line.startswith('p '):
                self.readCnfLine(words)
            elif line.startswith('w'): # possibly 'w\t'
                (w, var, weight) = words
                assert w == 'w', (line, self.cf)
                var = self.parseVar(var)
                weight = float(weight)
                if weight == -1:
                    self.litWeights[var] = self.litWeights[-var] = 1.0
                else:
                    assert 0 < weight < 1, (line, self.cf)
                    self.litWeights[var] = weight
                    self.litWeights[-var] = 1 - weight
            elif line and not line.startswith('c'):
                self.readClauseLine(words)
        for var in self.getDeclaredVars():
            if var not in self.litWeights:
                self.litWeights[var] = self.litWeights[-var] = 0.5
        self.checkFormula()

    def readWapsFile(self):
        for line in open(self.cf):
            line = line.strip()
            words = line.split()
            if line.startswith('p '):
                self.readCnfLine(words)
            elif line.startswith('c ind '):
                for i in range(2, len(words)):
                    word = words[i]
                    if word == '0':
                        assert i == len(words) - 1, (line, self.cf)
                    else:
                        self.outerVars.add(int(word))
            elif line.startswith('w '):
                lit = self.parseLit(words[1])
                weight = float(words[2])
                self.litWeights[lit] = weight
                var = abs(lit)
                if var not in self.outerVars and weight != 1:
                    self.outerVars.add(var)
                    self.printCheck(f'weighted inner var {var} is now outer var')
            elif line and not line.startswith('c'):
                self.readClauseLine(words)
        for outerVar in self.outerVars:
            if not self.isWeightedVar(outerVar):
                self.litWeights[outerVar] = self.litWeights[-outerVar] = 0.5
                self.printCheck(f'unweighted outer var {outerVar} now has lit weights 0.5')
        self.checkFormula()

    def getCnfLine(self):
        return f'p cnf {self.declaredVarCount} {len(self.clauses)}\n' # LG requires 1 space

    def getOuterVarsStr(self, altFlip):
        vars = set(self.getDeclaredVars()) - self.outerVars if altFlip else self.outerVars
        return ' '.join(map(str, sorted(vars)))

    def getWeightedLitLineBlock(self, defaultWeightsFlag, decDigits):
        lines = []
        for var in self.getDeclaredVars():
            for lit in Lit.getLits(var): # helps Cachet
                if defaultWeightsFlag or self.litWeights[lit] != 1:
                    lines.append(
                        f'c p weight {lit.alignSign()} {alignFloat(self.litWeights[lit], decDigits)} 0\n'
                    )
        return ''.join(lines)

    def getClauseLineBlock(self):
        return ''.join(map(Clause.getClauseLine, self.clauses))

    def writeCnfFile(self, newFilePath, blankLines=4, altFlip=False, defaultWeightsFlag=False, decDigits=6):
        makeDir(os.path.dirname(newFilePath))
        with open(newFilePath, 'w') as f:
            f.write(self.getCnfLine())
            f.write('\n' * blankLines)
            if self.pc:
                f.write(f'c p show {self.getOuterVarsStr(altFlip)} 0\n')
            f.write(self.getWeightedLitLineBlock(defaultWeightsFlag, decDigits))
            f.write(self.getClauseLineBlock())

    def writeMiniFile(self, newFilePath):
        makeDir(os.path.dirname(newFilePath))
        with open(newFilePath, 'w') as f:
            f.write(self.getCnfLine())
            f.write(f'''c weights {' '.join([
                f'{self.litWeights[var]} {self.litWeights[-var]}' for var in self.getDeclaredVars()
            ])}\n''')
            f.write(self.getClauseLineBlock())

    def writeD4WeightFile(self, newFilePath):
        makeDir(os.path.dirname(newFilePath))
        with open(newFilePath, 'w') as f:
            for var in self.getDeclaredVars():
                for lit in Lit.getLits(var):
                    f.write(f'{lit.alignSign()} {self.litWeights[lit]}\n')

    def writeD4VarFile(self, newFilePath):
        assert self.outerVars, newFilePath
        makeDir(os.path.dirname(newFilePath))
        with open(newFilePath, 'w') as f:
            f.write(','.join(map(str, sorted(self.outerVars))) + '\n')

class SdimacsFormula(CnfFormula):
    def getRandVars(self):
        assert self.wc, self.cf
        assert self.pc, self.cf
        return self.getWeightedVars()

    def getRandLineBlock(self, decDigits):
        lines = []
        for var in sorted(self.getRandVars()):
            weight = self.litWeights[var]
            self.checkWeightPairSum(var)
            lines.append(f'r {alignFloat(weight, decDigits)} {var} 0\n')
        return ''.join(lines)

    def getExistLineBlock(self): # long line would fail DCSSAT
        return ''.join(
            [f'e {var} 0\n' for var in sorted(set(self.getDeclaredVars()) - self.getRandVars())]
        )

    def writeSdimacsFile(self, newFilePath, decDigits=6):
        makeDir(os.path.dirname(newFilePath))
        with open(newFilePath, 'w') as f:
            f.write(self.getCnfLine())
            if self.er:
                f.write(self.getExistLineBlock())
                f.write(self.getRandLineBlock(decDigits))
            else:
                f.write(self.getRandLineBlock(decDigits))
                f.write(self.getExistLineBlock())
            f.write(self.getClauseLineBlock())

class WcnfFormula:
    def __init__(self, cnfFormula):
        self.cnfFormula = cnfFormula
        self.softWeights = {} # lit |-> weight where weight(lit) != weight(-lit)
        self.fillSoftWeights()

    def fillSoftWeights(self):
        for var in self.cnfFormula.getDeclaredVars():
            if self.cnfFormula.hasDiffWeightPair(var): # see postprocessor.printMaxSatOptimum
                for lit in Lit.getLits(var):
                    self.softWeights[lit] = math.log10(
                        self.cnfFormula.litWeights[lit]
                    ) + self.getSoftWeightOffset()

    def getSoftWeightOffset(self):
        minLitWeight = math.inf
        for var in self.cnfFormula.getDeclaredVars():
            if self.cnfFormula.hasDiffWeightPair(var):
                for lit in Lit.getLits(var):
                    minLitWeight = min(minLitWeight, self.cnfFormula.litWeights[lit])
        minClauseWeight = math.log10(minLitWeight)
        return int(abs(minClauseWeight)) + 1 if minClauseWeight <= 0 else 0

    def getSoftWeightMin(self):
        return min(self.softWeights.values())

    def getSoftWeightSum(self):
        return sum(self.softWeights.values())

    def getTopWeight(self):
        return int(self.getSoftWeightSum()) + 1

    def getWcnfLine(self):
        clauseCount = len(self.cnfFormula.clauses) + len(self.softWeights)
        return f'p wcnf {self.cnfFormula.declaredVarCount} {clauseCount} {self.getTopWeight()}\n'

    def getSoftClauseLineBlock(self, decDigits):
        lines = []
        for var in self.cnfFormula.getDeclaredVars():
            if var in self.softWeights:
                for lit in Lit.getLits(var):
                    lines.append(f'  {alignFloat(self.softWeights[lit], decDigits)} {lit.alignSign()} 0\n')
        return ''.join(lines)

    def getHardClauseLineBlock(self):
        return ''.join([
            f'{clause.alignX()} {self.getTopWeight()} {clause.getLitsLine()}'
            for clause in self.cnfFormula.clauses
        ])

    @staticmethod
    def writeStats(fileObject, postProcess, key, value):
        fileObject.write(f'c {key} {value}\n')
        printWrapperLine(postProcess, key, value)

    def writeWcnfFile(self, newFilePath, postProcess, decDigits=6):
        makeDir(os.path.dirname(newFilePath))
        with open(newFilePath, 'w') as f:
            f.write(self.getWcnfLine())
            self.writeStats(f, postProcess, 'weightedVarCount', int(len(self.softWeights) / 2))
            self.writeStats(f, postProcess, 'softWeightSum', alignFloat(self.getSoftWeightSum(), decDigits))
            self.writeStats(f, postProcess, 'softWeightOffset',  self.getSoftWeightOffset())
            self.writeStats(f, postProcess, 'logBase', 10)
            printWrapperLine(postProcess)
            f.write(self.getSoftClauseLineBlock(decDigits))
            f.write(self.getHardClauseLineBlock())

################################################################################

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

def getAbsPath(*args): # relative to this file
    p = os.path.join(os.path.dirname(__file__), *args)
    p = os.path.realpath(p) # also resolves symbolic links
    return p

def getBinFilePath(fileName):
    return getAbsPath('bin', fileName)

def getFileNameRoot(filePath):
    return os.path.splitext(os.path.basename(filePath))[0]

def getTempFilePath(cf, temp, ext):
    assert not ext.startswith('.'), ext
    fileName = f'{getFileNameRoot(cf)}.{ext}'
    makeDir(temp)
    return os.path.join(temp, fileName)

def getShellCmd(cmd):
    assert isinstance(cmd, list), cmd
    return ' '.join(cmd)

def getCtrlCmd(timecap, memcap):
    cmd = [getBinFilePath('runsolver'), '-w /dev/null', '-v /dev/stdout']
    if timecap:
        cmd.append(f'-W {int(timecap)}')
    if memcap:
        cmd.append(f'-R {int(memcap * 1e3)}') # in MB (must not use -M or -V)
    return cmd

def getWrittenWcnfFilePath(cf, prog, temp, postProcess):
    startTime = time.time()
    cnfFormula = CnfFormula(cf)
    cnfFormula.readCnfFile()
    if cf.endswith('.xcnf') and prog != GAUSS:
        cnfFormula.encodeTseitin()
    wcnfFilePath = getTempFilePath(cf, temp, 'wcnf')
    WcnfFormula(cnfFormula).writeWcnfFile(wcnfFilePath, postProcess)
    printTempTimeStats(postProcess, startTime, wcnfFilePath)
    return wcnfFilePath

def getCmsCmd(cf):
    return [
        getBinFilePath('cryptominisat5_amd64_linux_static'),
        cf,
        '--verb=0',
        '--printsol=0',
    ]

def getProgCmd(ctxArgs, cf, prog, phase, temp, postProcess):
    if prog == DPMC:
        return [
            'python3',
            getAbsPath('dpmc.py'),
            f'--cf={cf}',
            f'--phase={phase}',
        ] + ctxArgs
    elif prog == CACHET: # possibly wrong solution with default weight 1
        return [
            getBinFilePath('cachet'),
            cf,
        ]
    elif prog == C2D:
        return [
            getBinFilePath('c2d'),
            '-in', cf,
            '-silent',
        ]
    elif prog == MINI:
        startTime = time.time()
        cnfFormula = CnfFormula(cf)
        cnfFormula.readCnfFile()
        miniFilePath = getTempFilePath(cf, temp, 'mini')
        cnfFormula.writeMiniFile(miniFilePath)
        printTempTimeStats(postProcess, startTime, miniFilePath)
        return [
            'singularity',
            'exec',
            getBinFilePath('centos.img'),
            getBinFilePath('miniC2D'),
            f'--cnf={miniFilePath}',
            '-W',
        ]
    elif prog in {D4, D4P, PROJMC}:
        return [
            getBinFilePath('d4'),
            f'--input={cf}',
            '--float=1',
            '--output-format=competition',
            f'--keyword-output-format-solution=s type {"wmc" if prog == D4 else "pmc"}',
            f'--method={"projMC" if prog == PROJMC else "counting"}',
        ]
    elif prog in {RESSAT, ERSSAT, DCSSAT}:
        startTime = time.time()
        sdimacsFormula = SdimacsFormula(cf, pc=True, er=prog != RESSAT)
        sdimacsFormula.readCnfFile()
        sdimacsFilePath = getTempFilePath(cf, temp, 'sdimacs') # ext required by RESSAT/ERSSAT
        sdimacsFormula.writeSdimacsFile(sdimacsFilePath)
        printTempTimeStats(postProcess, startTime, sdimacsFilePath)
        if prog == DCSSAT:
            return [getBinFilePath('dcssat'), sdimacsFilePath]
        else: # RESSAT/ERSSAT
            return [
                getBinFilePath('abc'),
                '-q ssat',
                sdimacsFilePath,
            ]
    elif prog == GAUSS:
        return [
            getBinFilePath('gaussmaxhs'),
            getWrittenWcnfFilePath(cf, prog, temp, postProcess),
            '-verb=0',
        ]
    elif prog == MAXHS:
        return [
            getBinFilePath('maxhs'),
            getWrittenWcnfFilePath(cf, prog, temp, postProcess),
            '-printSoln',
            '-no-printOptions',
            '-verb=0',
        ]
    elif prog == UWR:
        return [
            getBinFilePath('uwrmaxsat'),
            getWrittenWcnfFilePath(cf, prog, temp, postProcess),
            '-bm',
            '-v0',
        ]
    else:
        assert prog == CMS, prog
        return getCmsCmd(cf)

@click.command(
    context_settings={
        'max_content_width': 105,
        'help_option_names': ['-h', '--help'],
        'show_default': True,
        'ignore_unknown_options': True,
        'allow_extra_args': True,
    },
    help=f'Unknown options will be passed to file `{DPMC}.py`',
)
@click.option('--cf',
    help='CNF file',
    required=True,
)
@click.option('--prog',
    type=click.Choice([
        DPMC, CACHET, C2D, MINI, D4, D4P, PROJMC, RESSAT, ERSSAT, DCSSAT, GAUSS, MAXHS, UWR, CMS
    ]),
    default=DPMC,
    help='program',
)
@click.option('--phase',
    type=click.Choice([PLAN_PHASE, EXEC_PHASE, DUAL_PHASE]),
    default=DUAL_PHASE,
    help=f'[{DPMC}] planning, execution, or both',
)
@click.option('--temp',
    default='tempdir',
    help='temp dir to write aux files',
)
@click.option('--ctrl',
    default=0,
    help='control software (runsolver)',
)
@click.option('--timecap',
    default=0.0,
    help='[ctrl] in seconds',
)
@click.option('--memcap',
    default=0.0,
    help='[ctrl] in GB',
)
@click.option('--post',
    default=0,
    help='postprocessing',
)
@click.pass_context
def main(ctx, cf, prog, phase, temp, ctrl, timecap, memcap, post):
    if timecap or memcap or post:
        ctrl = 1
    cmd = getCtrlCmd(timecap, memcap) if ctrl else []

    postProcess = None
    if post:
        postProcess = subprocess.Popen(
            ['python3', getAbsPath('postprocessor.py')], stdin=subprocess.PIPE
        )
        printWrapperLine(postProcess, 'cf', cf)
        printWrapperLine(postProcess, 'prog', prog)
        printWrapperLine(postProcess, 'phase', phase)
        printWrapperLine(postProcess)

    cmd += getProgCmd(ctx.args, cf, prog, phase, temp, postProcess)

    if post:
        subprocess.run(
            getShellCmd(cmd),
            shell=True, # required by ctrl
            stderr=postProcess.stdin,
            stdout=postProcess.stdin,
        )
        postProcess.communicate()
    else:
        subprocess.run(
            getShellCmd(cmd),
            shell=True, # required by ctrl
            stderr=subprocess.STDOUT,
        )

if __name__ == '__main__':
    main()
