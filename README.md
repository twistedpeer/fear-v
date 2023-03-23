# FEAR-V: Fault Effect Analysis for RISC-V

This is the main repository for FEAR-V.

## Prerequisites

### Required tools

In order to use FEAR-V, you need to have the following tools available:

* PostgreSQL Database Server
* Python 3.9 or later
* Python virtualenv
* Build environment with Make and GCC
* Cmake
* OpenJDK v8 (for riscv-torture)
* SiFive riscv-gnu-toolchain (for compilation of FE300 testprograms)

### Database setup

FEAR-V requires a PostgreSQL database server that is accessible by user "django" with password "django" that has the right to create/update a database also called "django".

For details how to setup the database server, please refer to the official documentation. A setup guide for Ubuntu can be found here: https://ubuntu.com/server/docs/databases-postgresql

The following page describes how to create a database user: https://www.postgresql.org/docs/8.0/sql-createuser.html

## Installation

First, you need to setup a python virtualenv:
```
# Create python3 venv
python3 -m venv .venv
source .venv/bin/activate
# Install packages
pip install --upgrade pip
pip install -r requirements.txt
source sourceme.sh
```

Then proceed with the initialization of the subrepositories:
```
# Init git submodules
git submodule update --init
```

Check out the Django analysis framework:
```
# DJANGO
cd tools/isa-toolkit
git checkout main
cd ../..
```

Check out and build the fear5 branch of QEMU:
```
# QEMU
cd tools/qemu
git checkout fear5
./configure --target-list=riscv32-softmmu --enable-fear5 --disable-docs --disable-werror
make -j5
cd ../..
```

Check out and build the FE300 code generation environment. This repository wraps Csmith, riscv-tests, riscv-arch-tests and risc-torture:
```
# FE300-SWGEN
cd tools/fe300-swgen
git checkout main
./install.sh
cd ../..
```

## Usage
In order to use FEAR-V, you need to load some environment variables. You can do so by executing the following command:
```
source sourceme.sh
```

After loading the environment variables, the f5 script is ready to execute FEAR-V YAML files. In the directory demos/testsw-297 there are three demos including FEAR-V YAML files. The following section describes how to execute these demos.

### Demonstration: testsw-297
This repository comes with three demos that share 297 pre-compiled binary test programs. They demo resides in the following directory:
```
cd demo/testsw-297
```

The first demo simulates single-bit permanent instruction, GPR and CSR faults. It can be run with:
```
f5 01_permanent_1Bit.yaml
```

The second demo simulates single-bit transient GPR faults. It is started with:
```
f5 02_transient_1Bit.yaml
```

The third demo simulates 4-bit transient GPR faults. It can be run with:
```
f5 03_transient_4Bit.yaml 
```
