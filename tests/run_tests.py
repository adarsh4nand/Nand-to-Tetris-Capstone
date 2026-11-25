#!/usr/bin/env python3
"""
run_tests.py -- the same checks as run_tests.sh, but cross-platform.

Works on Windows, macOS and Linux: it only needs Python 3 and the official
nand2tetris tools (the folder that contains HardwareSimulator.sh / .bat).

Usage:
    python tests/run_tests.py --tools C:\\nand2tetris\\tools
    python tests/run_tests.py --tools ../nand2tetris/tools
    python tests/run_tests.py --tools ../nand2tetris/tools --slow
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
HDL = os.path.join(ROOT, "hdl")
OFFICIAL = os.path.join(HERE, "official")

CHIP_TESTS = [
    "Not", "And", "Or", "Xor", "Mux", "DMux", "Not16", "And16", "Or16", "Mux16",
    "Or8Way", "Mux4Way16", "Mux8Way16", "DMux4Way", "DMux8Way",
    "HalfAdder", "FullAdder", "Add16", "Inc16", "ALU",
    "Bit", "Register", "RAM8", "RAM64", "RAM512", "RAM4K", "RAM16K", "PC",
]

passed = []
failed = []


def java_classpath(tools):
    """The library jars, plus '.' so the simulator finds its built-in chips."""
    jars = [os.path.join(tools, "bin", "classes")]
    lib = os.path.join(tools, "bin", "lib")
    for name in ("Hack.jar", "HackGUI.jar", "Simulators.jar", "SimulatorsGUI.jar", "Compilers.jar"):
        jars.append(os.path.join(lib, name))
    parts = ["."] + jars
    if os.environ.get("CLASSPATH"):
        parts.append(os.environ["CLASSPATH"])
    return os.pathsep.join(parts)


def java(tools, main_class, args, classpath, cwd=None):
    java_exe = os.environ.get("JAVA") or shutil.which("java")
    if not java_exe:
        print("  java was not found. Install a JDK (Java 11 or newer) and try again.")
        sys.exit(1)
    command = [java_exe, "-Xmx4g", "-classpath", classpath, main_class] + args
    return subprocess.run(command, cwd=cwd or tools, capture_output=True,
                          text=True, errors="replace")


def run_hdl_test(tools, workdir, name, classpath):
    script = os.path.join(workdir, name + ".tst")
    if not os.path.exists(script):
        print("  SKIP  %-16s (no %s.tst)" % (name, name))
        return
    result = java(tools, "HardwareSimulatorMain", [script], classpath)
    text = (result.stdout or "") + (result.stderr or "")
    if "Comparison ended successfully" in text:
        passed.append(name)
        print("  PASS  %s" % name)
    else:
        failed.append(name)
        tail = " ".join(text.strip().splitlines()[-2:])[:160]
        print("  FAIL  %s" % name)
        if tail:
            print("        %s" % tail)


def prepare(workdir, with_builtin_pc_and_ram):
    os.makedirs(workdir, exist_ok=True)
    for name in os.listdir(HDL):
        if name.endswith(".hdl"):
            if with_builtin_pc_and_ram and name in ("PC.hdl", "RAM16K.hdl"):
                continue
            shutil.copy(os.path.join(HDL, name), workdir)
    for name in os.listdir(OFFICIAL):
        if name.endswith((".tst", ".cmp", ".hack")):
            shutil.copy(os.path.join(OFFICIAL, name), workdir)


def check_assembler(tools, workdir, classpath):
    asm_dir = os.path.join(workdir, "_asm")
    os.makedirs(asm_dir, exist_ok=True)
    for program in ("Add", "Max", "Rect", "Pong"):
        source = os.path.join(OFFICIAL, program + ".asm")
        shutil.copy(source, asm_dir)
        mine = os.path.join(asm_dir, program + ".mine.hack")
        subprocess.run([sys.executable, os.path.join(ROOT, "assembler.py"), source, "-o", mine],
                       capture_output=True, text=True)
        java(tools, "HackAssemblerMain", [program + ".asm"], classpath, cwd=asm_dir)
        official = os.path.join(asm_dir, program + ".hack")
        if os.path.exists(mine) and os.path.exists(official):
            with open(mine) as a, open(official) as b:
                same = a.read() == b.read()
            if same:
                with open(mine) as handle:
                    count = sum(1 for line in handle if line.strip())
                passed.append("assembler " + program)
                print("  PASS  assembler %-6s (%d instructions, identical)" % (program, count))
                continue
        failed.append("assembler " + program)
        print("  FAIL  assembler %s" % program)


def check_box():
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    from hack_emu import Hack, load  # noqa: E402

    with open(os.path.join(ROOT, "Box.asm")) as handle:
        source = handle.read().splitlines()

    start_row = width = None
    for line in source:
        stripped = line.strip()
        if stripped.startswith("@") and "START ROW = K" in line:
            start_row = int(stripped[1:].split()[0])
        if stripped.startswith("@") and "WIDTH IN WORDS" in line:
            width = int(stripped[1:].split()[0])
    if start_row is None or width is None:
        failed.append("box")
        print("  FAIL  box program (could not read the numbers from Box.asm)")
        return

    print("  Box.asm says: K=%d, width=%d word(s), height=20" % (start_row, width))

    def screen_after(cycles, key):
        emulator = Hack(load(os.path.join(ROOT, "Box.hack")))
        emulator.ram[24576] = key
        for _ in range(cycles):
            emulator.step()
        return emulator.black_box(), emulator.black_pixels()

    expected = (start_row, start_row + 19, 0, width * 16 - 1)
    pressed, pixels = screen_after(300000, 65)
    released, released_pixels = screen_after(300000, 0)
    pressed_again, _ = screen_after(300000, 65)

    print("  key held   -> box=%s black_pixels=%d" % (pressed, pixels))
    print("  key up     -> box=%s black_pixels=%d" % (released, released_pixels))
    print("  key held   -> box=%s" % (pressed_again,))

    if pressed == expected and pressed_again == expected and released is None:
        passed.append("box")
        print("  PASS  box: rows %d-%d, %d pixels wide, appears and disappears"
              % (start_row, start_row + 19, width * 16))
    else:
        failed.append("box")
        print("  FAIL  box (expected box=%s, got %s)" % (expected, pressed))


def main():
    parser = argparse.ArgumentParser(description="Re-check the whole capstone.")
    parser.add_argument("--tools", required=True,
                        help="the nand2tetris tools folder (it contains HardwareSimulator.sh)")
    parser.add_argument("--slow", action="store_true",
                        help="also run the full official Memory.tst (about 20 minutes)")
    args = parser.parse_args()

    tools = os.path.abspath(os.path.expanduser(args.tools))
    marker = os.path.join(tools, "HardwareSimulator.sh")
    if not os.path.exists(marker) and not os.path.exists(os.path.join(tools, "HardwareSimulator.bat")):
        print("Cannot find the nand2tetris tools in %s" % tools)
        print("Point --tools at the folder that contains HardwareSimulator.sh / .bat")
        return 1

    classpath = java_classpath(tools)
    workdir = tempfile.mkdtemp(prefix="capstone-")
    try:
        print("\n=== 1. chips of projects 1-3 (our HDL) ===")
        full = os.path.join(workdir, "full")
        prepare(full, with_builtin_pc_and_ram=False)
        for chip in CHIP_TESTS:
            run_hdl_test(tools, full, chip, classpath)

        print("\n=== 2. the CPU (our CPU.hdl) ===")
        run_hdl_test(tools, full, "CPU", classpath)

        print("\n=== 3. Memory and the Computer ===")
        run_hdl_test(tools, full, "Memory-quick", classpath)
        if args.slow:
            print("  (running the full official Memory.tst -- this one is slow)")
            run_hdl_test(tools, full, "Memory", classpath)
        builtin = os.path.join(workdir, "builtin")
        prepare(builtin, with_builtin_pc_and_ram=True)
        for name in ("ComputerAdd", "ComputerMax", "ComputerRect"):
            run_hdl_test(tools, builtin, name, classpath)

        print("\n=== 4. our assembler against the official assembler ===")
        check_assembler(tools, workdir, classpath)

        print("\n=== 5. the box program (emulator check) ===")
        check_box()
    finally:
        shutil.rmtree(workdir, ignore_errors=True)

    print("\n-------------------------------------------------------------")
    print("  %d passed, %d failed" % (len(passed), len(failed)))
    if failed:
        print("  failed: %s" % ", ".join(failed))
    print("-------------------------------------------------------------")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
