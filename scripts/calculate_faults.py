#!/usr/bin/env python3
import getopt
import itertools
import os
import sys
import django
from django.db import transaction
from multiprocessing import Process

if 'FEAR_V_DIR' not in os.environ:
    print("ERROR: Need to source 'sourceme.sh' first!")
    exit(1)
sys.path.append(os.environ["FEAR_V_DIR"] + "/tools/isa-toolkit/")
os.environ['DJANGO_SETTINGS_MODULE'] = 'app_main.settings'
django.setup()

from webapp.models import *


def bits(n):
    while n:
        b = n & (~n + 1)
        yield b
        n ^= b


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:min(i + n, len(l))]


def exp_bit_faults(bits, limit=1):
    exp = []
    for b in range(limit):
        for c in itertools.combinations(range(bits), b + 1):
            i = 0
            for n in c:
                i += 1 << n
            exp.append(i)
    exp.sort()
    return exp


def split(a, n):
    k, m = divmod(len(a), n)
    return (a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))


def start_faults_generation(arch_name, bits, chunk, nr_chunks):
    experiments = {16: exp_bit_faults(16, limit=bits), 32: exp_bit_faults(32, limit=bits)}

    allinsn = Instruction.objects.filter(subset__arch__name=arch_name)
    # n = math.ceil(float(len(allinsn)) / float(nr_chunks))
    n = int(allinsn.count() / nr_chunks)
    # allinsn_split = list(zip(*[iter(allinsn)] * n))
    allinsn_split = list(split(allinsn, nr_chunks))

    # for i in [allinsn[j:j + n] for j in range(0, len(allinsn), n)][chunk]:
    for i in allinsn_split[chunk]:
        print("Calculating fault effects for instruction '" + i.name + "'.")
        simulate_faults(i, allinsn, experiments[i.bits])


@transaction.atomic
def simulate_faults(insn, allinsn, experiments):
    faults = []
    for ex in experiments:

        f = InstructionFault()
        f.source = insn
        f.error_mask = ex
        f.target = None
        f.distance = bin(f.error_mask).count('1')
        f.effect_gpr = False
        f.effect_fpr = False
        f.effect_csr = False
        f.effect_imm = False
        new_opcode = insn.opcode ^ ex

        # 1) Find target instruction
        for other in allinsn:
            if new_opcode & other.mask == other.opcode:
                f.target = other
                break

        # 2) Which opcode effect?
        if f.target_id is None:
            f.effect_opcode = 'illegal'
        elif insn.id != f.target_id:
            # Can be newop or cfchange
            if "control-transfer" not in insn.kind and "control-transfer" not in f.target.kind:
                f.effect_opcode = 'newop'
            else:
                f.effect_opcode = 'cfchange'

        # 3) Other effects...
        if f.target is not None:
            operands_list = list(f.target.operands.all())
            # bin_error_mask = str('{0:0' + str(insn.bits) + 'b}').format(f.error_mask)
            for b in bits(f.error_mask):
                for o in operands_list:
                    if b & o.mask != 0:
                        if o.optype == "gpr":
                            f.effect_gpr = True
                        elif o.optype == "fpr":
                            f.effect_fpr = True
                        elif o.optype == "csr":
                            f.effect_csr = True
                        else:
                            f.effect_imm = True

        faults.append(f)
    InstructionFault.objects.bulk_create(faults)


def error_usage():
    print("Usage: calculate_faults.py -a <arch_name> [-j <parallel_jobs>] [-b <max_faults_imem>]")
    sys.exit()


def main(argv):
    global counter
    global total
    # Parse the command-line options...
    try:
        opts, args = getopt.getopt(argv, "ha:j:b:", ["help", "arch=", "jobs=", "bits="])
    except getopt.GetoptError:
        error_usage()

    arch_name = None
    nr_jobs = os.cpu_count()
    bits = 3

    for opt, arg in opts:
        if opt in ['-h', '--help']:
            error_usage()
        elif opt in ['-j', '--jobs']:
            try:
                nr_jobs = int(arg)
            except:
                print("ERROR parsing nr_jobs!")
                error_usage()
        elif opt in ['-a', '--arch']:
            arch_name = arg
        elif opt in ['-b', '--bits']:
            bits = int(arg)

    # Option error handling:
    if arch_name is None:
        print("Error: You need to specify the architecture name!")
        error_usage()

    # Create the faults...
    print("Creating faults...")

    processes = []

    for i in range(nr_jobs):
        p = Process(target=start_faults_generation, args=(arch_name, bits, i, nr_jobs))
        p.start()
        processes.append(p)
    for p in processes:
        p.join()


if __name__ == "__main__":
    main(sys.argv[1:])
