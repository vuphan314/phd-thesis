#!/usr/bin/env python3

import functools
import os
import subprocess

import click

################################################################################

cerr = print = functools.partial(print, flush=True)

PLAN_PHASE = 'plan'
EXEC_PHASE = 'exec'
DUAL_PHASE = 'dual'

LG = 'lg'
HTB = 'htb'

DMC = 'dmc'
TENSOR = 'tensor'

FLOW = 'flow'
MEIJI = 'meiji'
HTD = 'htd'

################################################################################

def getTdCmd(td, tw):
    if td == HTD: # decomposition.maximumBagSize() <= 100
        return '/solvers/htd-master/bin/htd_main --strategy challenge --preprocessing full --opt width --iterations 0'
    if td == FLOW:
        cmd = '/solvers/flow-cutter-pace17/flow_cutter_pace17'
    if td == MEIJI:
        cmd = 'java -classpath /solvers/TCS-Meiji tw.heuristic.MainDecomposer'
    return f'{cmd} -p {tw}'

def getBinFilePath(fileName):
    return os.path.join(os.path.dirname(__file__), 'bin', fileName)

def getHostFilePath(filePath):
    return f'/host/{os.path.realpath(filePath)}'

@click.command(
    context_settings={
        'help_option_names': ['-h', '--help'],
        'show_default': True,
        'ignore_unknown_options': True,
        'allow_extra_args': True,
    },
    help=f'Unknown options will be passed to file `{DMC}`',
)
@click.option('--cf',
    required=True,
    help='CNF file',
)
@click.option('--phase',
    type=click.Choice([PLAN_PHASE, EXEC_PHASE, DUAL_PHASE]),
    default=DUAL_PHASE,
    help='planning, execution, or both',
)
@click.option('--pt',
    type=click.Choice([LG, HTB]),
    default=LG,
    help=f'[{PLAN_PHASE}|{DUAL_PHASE}] planning tool',
)
@click.option('--et',
    type=click.Choice([DMC, TENSOR]),
    default=DMC,
    help=f'[{EXEC_PHASE}|{DUAL_PHASE}] execution tool',
)
@click.option('--jf',
    help=f'[{EXEC_PHASE}] JT file',
)
@click.option('--td',
    type=click.Choice([FLOW, MEIJI, HTD]),
    default=FLOW,
    help=f'[{LG}] tree decomposer',
)
@click.option('--tw',
    default=100,
    help=f'[{FLOW}|{MEIJI}] treewidth',
)
@click.option('--cv',
    default=5,
    help=f'[{HTB}] cluster var order',
)
@click.option('--ch',
    default='bmt',
    help=f'[{HTB}] clustering heuristic',
)
@click.option('--pc',
    default=0,
    help=f'[{HTB}|{DMC}] projected counting',
)
@click.option('--vc',
    default=1, # prints CNF stats
    help=f'[{HTB}|{DMC}] verbose CNF processing',
)
@click.option('--vs',
    default=0,
    help=f'[{HTB}|{DMC}] verbose solving',
)
@click.option('--vj',
    default=1, # prints join tree
    help=f'[{DMC}] verbose JT processing',
)
@click.option('--er',
    default=0,
    help=f'[{DMC}] exist-random',
)
@click.option('--lc',
    default=1,
    help=f'[{DMC}] logarithmic counting',
)
@click.option('--softmemcap',
    default=0.0,
    help=f'[{DMC}] in GB',
)
@click.pass_context
def main(ctx, cf, phase, pt, et, jf, td, tw, cv, ch, pc, vc, vs, vj, er, lc, softmemcap):
    lgCmd = [getBinFilePath('lg.sif'), getTdCmd(td, tw)]

    htbCmd = [
        getBinFilePath('htb'),
        f'--cf={cf}',
        f'--pc={pc}',
        f'--cv={cv}',
        f'--ch={ch}',
        f'--vc={vc}',
        f'--vs={vs}',
    ]

    dmcCmd = [
        getBinFilePath('dmc'),
        f'--cf={cf}',
        f'--pc={pc}',
        f'--er={er}',
        f'--mf={er}',
        f'--lc={lc}',
        f'--mm={softmemcap * 1e3}',
        f'--vc={vc}',
        f'--vj={vj}',
        f'--vs={vs}',
    ] + ctx.args

    tensorCmd = [
        'singularity',
        'run',
        '--bind=/:/host',
        getBinFilePath('tensor.sif'),
        f'--formula={getHostFilePath(cf)}',
    ]

    if phase == PLAN_PHASE:
        if pt == LG:
            subprocess.run(lgCmd, stdin=open(cf))
        else:
            subprocess.run(htbCmd)
    elif phase == EXEC_PHASE:
        assert jf, jf
        if et == DMC:
            subprocess.run(dmcCmd, stdin=open(jf))
        else:
            subprocess.run(tensorCmd + [f'--join_tree={getHostFilePath(jf)}'])
    else:
        plannerArgs = {'stdout': subprocess.PIPE}
        if pt == LG:
            plannerArgs['stdin'] = open(cf)
            plannerCmd = lgCmd
        else:
            plannerCmd = htbCmd
        plannerProcess = subprocess.Popen(plannerCmd, **plannerArgs)
        subprocess.run(
            dmcCmd if et == DMC else tensorCmd,
            stdin=plannerProcess.stdout,
        )

if __name__ == '__main__':
    main()
