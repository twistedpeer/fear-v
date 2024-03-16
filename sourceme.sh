#!/bin/bash

export FEAR_V_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# DJANGO
export FEAR_V_FILES_DIR="${FEAR_V_DIR}/tools/isa-toolkit/.files"
export PYTHONPATH="$PYTHONPATH:${FEAR_V_DIR}/tools/isa-toolkit"

# QEMU
export PATH="${FEAR_V_DIR}/tools/qemu/build/riscv32-softmmu:$PATH"

# CSMITH
export PATH="${FEAR_V_DIR}/tools/fe300-swgen/work/csmith/bin:$PATH"

# FEAR-V-Scripts
export PATH="${FEAR_V_DIR}/scripts:$PATH"

# Enter Python Virtualenv
source "${FEAR_V_DIR}/.venv/bin/activate"
