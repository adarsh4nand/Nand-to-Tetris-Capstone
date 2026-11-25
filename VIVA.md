# Running everything on your laptop (viva setup)

Everything below is done once, before the viva. Fifteen minutes if the tools are not
installed yet, three minutes if they are.

You need three things: a **JDK** (the nand2tetris tools are Java programs), **Python 3** (for
the assembler), and the **nand2tetris tools** themselves.

---

## 1. Install the JDK

- **Windows / macOS:** install an OpenJDK build from <https://adoptium.net> (Java 17 or 21,
  "x64" or "aarch64" to match the machine). Run the installer with the default options.
- **Linux:** `sudo apt install openjdk-17-jdk` (Debian/Ubuntu) or the equivalent.

Check it:

```bash
java -version
```

It must print a version. If the command is not found, the installer did not add Java to the
PATH — reopen the terminal first, and on Windows re-run the installer with the "add to PATH"
option ticked.

## 2. Install Python 3

- **Windows / macOS:** <https://python.org/downloads> — tick **"Add python.exe to PATH"** on
  the first Windows screen.
- **Linux:** already installed.

Check it:

```bash
python --version       # Windows
python3 --version      # macOS / Linux
```

## 3. Download the nand2tetris tools

Go to <https://www.nand2tetris.org/software>, download the tools zip and extract it
somewhere simple, for example:

- Windows: `C:\nand2tetris`
- macOS / Linux: `~/nand2tetris`

The folder you need is the one that contains `HardwareSimulator.sh` and
`HardwareSimulator.bat` — normally `nand2tetris/tools`.

## 4. Get this repository

```bash
git clone https://github.com/adarsh4nand/Nand-to-Tetris-Capstone
cd Nand-to-Tetris-Capstone
```

No Git? Download the ZIP from the green **Code** button and extract it — the commands below
are the same, just run from the extracted folder.

## 5. Run every check

```bash
python tests/run_tests.py --tools C:\nand2tetris\tools     # Windows
python3 tests/run_tests.py --tools ~/nand2tetris/tools     # macOS / Linux
```

It ends with `38 passed, 0 failed`. This is the number to quote if the examiner asks whether
the work actually passes the official tests.

There is also `tests/run_tests.sh`, the same checks as a shell script — use it from Git Bash
if you prefer, but the Python one works everywhere.

---

## 6. The five-minute demo, in order

Open a terminal in the repository folder before you start.

### a) Show the tree (20 seconds)

```bash
ls            # or: dir
```

Say what each piece is: `hdl/` the computer, `assembler.py` the assembler, `Box.asm` /
`Box.hack` the program, `tests/` the official test files.

### b) Run the checks (2 minutes)

```bash
python tests/run_tests.py --tools C:\nand2tetris\tools
```

While it runs, point at the sections: chip tests, CPU, Memory and Computer, assembler
comparison, box check. Show the final `38 passed, 0 failed`.

### c) The computer in the Hardware Simulator (40 seconds)

1. Open **Hardware Simulator** (double-click `HardwareSimulator.bat`, or `sh
   HardwareSimulator.sh`).
2. **File → Load Test Script** → `tests/screenshot/01-cpu/CPU.tst`.
3. Click **Run**. The status line turns green: *End of script - Comparison ended
   successfully*.

If asked: this test walks the CPU through A-instructions, C-instructions, ALU operations and
every jump condition, and compares the outputs with `CPU.cmp` line by line.

### d) The box (1 minute)

1. Open **CPU Emulator** (`CPUEmulator.bat`).
2. Click the **folder icon above the ROM list** → choose `tests/screenshot/04-box/Box.hack`.
   The ROM shows `@93, D=A, @16, M=D, @2, …`.
3. Drag the **Animate** slider all the way to **Fast**.
4. Press **F5** (Run), then **hold any letter key** — the box appears at row 93, 32 pixels
   wide, at the left edge.
5. **Release the key** — the box disappears. Press again — it comes back.

### e) The change they will ask for (1 minute)

Moving the box down is one number.

1. Open `Box.asm` in any editor.
2. Find the line marked `START ROW = K` — it reads `@93`.
3. Change it to `@120`, save.
4. Reassemble and reload:

```bash
python assembler.py Box.asm
```

5. In the CPU Emulator: **folder icon → `Box.hack`** again, **F5**, hold a key. The box is
   now 27 rows lower.

The width line just below it (`@2` — words per row) does the same for the width: 1 → 16 px,
2 → 32 px, 3 → 48 px, 4 → 64 px.

---

## 7. The questions, in one line each

**How does the CPU work?** It decodes the instruction bits directly: bit 15 tells an
A-instruction from a C-instruction, bits 4–5 are the destination, 6–12 the ALU control,
13–15 the jump. The ALU works on D and either A or M (`instruction[12]`), and the program
counter jumps when the selected condition holds, otherwise it increments.

**Why is the A register loaded differently in the two instruction types?** An A-instruction
puts its 15-bit constant into A; a C-instruction may put the ALU result there. A 16-bit
multiplexer driven by `instruction[15]` chooses between the instruction word and the ALU
output.

**How does Memory decide where a write goes?** `address[14]` selects RAM (0) or the
input/output region (1); inside that region `address[13]` selects the screen (0) or the
keyboard (1). The load signal is gated with the same bits, so a write can only reach the
selected chip.

**How does the assembler work?** Two passes. The first removes comments and records every
label with the address of the following instruction. The second translates each line: the
symbol table is checked, unknown symbols become new variables from RAM[16] upward, and each
instruction is emitted as 16 bits.

**How are variable addresses allocated?** Predefined symbols first, then labels, then a
counter that starts at 16 and increments the first time each new name is seen. `symbols.txt`
shows the result.

**What is your extra feature?** For K = 93, K mod 3 = 0, so the assembler writes `symbols.txt`
with every label and variable and its address. The other two features (line-numbered errors,
duplicate-label warning) are in the same file, switched on.

**How does screen memory work?** It starts at 16384, 32 words per row, 16 pixels per word,
so row *r* is at `16384 + 32r`. Writing −1 paints a word's 16 pixels black, 0 clears them.

**Why does the box start at row 93?** Because K = 93; the boot section of `Box.asm` stores K,
the width and the height in variables, and the paint routine adds 32 (one row) K times to
reach row K.

---

## 8. If something goes wrong at the demo

| Symptom | Fix |
|---|---|
| `java: command not found` | the JDK is not on the PATH — reopen the terminal, or reinstall with the PATH option |
| `Cannot find the nand2tetris tools` | `--tools` must point at the folder holding `HardwareSimulator.sh` |
| Hardware Simulator: *Chip Nand is not found* | the test script was opened from a folder without the chips — use the folders in `tests/screenshot/` |
| ComputerRect fails when you use your own `PC.hdl`/`RAM16K.hdl` | expected: that test prints their internal state; the folder `02-computerrect/` already leaves them out |
| The emulator runs very slowly | drag the **Animate** slider to **Fast**; the box still takes a few seconds to appear because the program has to reach row 93 first |
| `Memory.tst` seems to hang | it is genuinely slow (about 20 minutes on a laptop). Skip it; `Memory-quick.tst` covers the same decoding in seconds |
