#!/bin/bash

# Create python3 venv
python3 -m venv .venv
source .venv/bin/activate
# Install packages
pip install --upgrade pip
pip install -r requirements.txt

# Enter venv (may be obsolete...)
source sourceme.sh

# Init git submodules
git submodule update --init

# DJANGO
cd tools/isa-toolkit
git checkout main
cd ../..

# QEMU
cd tools/qemu
git checkout fear5
./configure --target-list=riscv32-softmmu --enable-fear5 --disable-docs --disable-werror
make -j5
cd ../..

# FE300-SWGEN
cd tools/fe300-swgen
git checkout main
./install.sh
cd ../..
