# 5-Minute Individual Viva Guide (K = 93)

**Student:** Adarsh Anand · **Roll No.:** 2501730393 · **Personal Number (K):** 93  
**Course:** Nand to Tetris – I (ETCCNT301) · K.R. Mangalam University

---

## 1. Quick Numbers to Memorize

- **K = 93** (last two digits of `2501730393`)
- **Assembler extra feature (`K mod 3`):** `93 mod 3 = 0` → saves all predefined symbols, labels, and variables with their addresses into `symbols.txt`
- **Box starting row:** `r = K = 93` (rows `93` to `112`)
- **Box height:** `20` rows
- **Box width:** `16 × ((93 mod 4) + 1) = 16 × (1 + 1) = 32` pixels = **2 words** per row, starting from the left edge (column `0`)
- **Starting screen address:** `SCREEN + 32 × 93 = 16384 + 2976 = 19360`
- **Total pixels / words:** `32 × 20 = 640` pixels (`40` screen words)

---

## 2. Live 5-Minute Demo Sequence

1. **Show `capstone/` folder:**
   - Contains `CPU.hdl`, `Memory.hdl`, `Computer.hdl` (plus all 28 course chips), `assembler.py`, `Box.asm`, `Box.hack`, `symbols.txt`, `test_programs/*.hack`, and `screenshots/`.
2. **Demonstrate `assembler.py`:**
   ```bash
   python3 capstone/assembler.py capstone/Box.asm
   ```
   Show that it creates `Box.hack` (85 instructions) and `symbols.txt` automatically (`K mod 3 = 0`).
3. **Demonstrate `Box.hack` in CPU Emulator:**
   - Open `CPUEmulator` → load `capstone/Box.hack`.
   - Set **Animate** slider to **Fast**, press **Run (F5)**.
   - Hold any key → black 32×20 box appears at row 93 on the left edge.
   - Release the key → box disappears immediately.
4. **Live Modification (Step 6.7 — e.g. moving the box down):**
   - Open `capstone/Box.asm`.
   - Find line `@93 // START ROW = K` inside `(BOOT)` and change `@93` to `@120` (or whatever row the faculty asks for, e.g., `@130`).
   - Reassemble:
     ```bash
     python3 capstone/assembler.py capstone/Box.asm
     ```
   - Reload `capstone/Box.hack` in CPU Emulator, press **F5**, hold a key → box now appears at the new row!
   - *(If asked to change width, change `@2 // WIDTH IN WORDS` to `@3` for 48 px or `@4` for 64 px; to change height, change `@20 // HEIGHT IN ROWS`.)*

---

## 3. Concise Answers to the 7 Viva Questions

1. **How do `CPU.hdl`, `Memory.hdl`, and `Computer.hdl` work?**
   - **`CPU.hdl`:** Decodes the 16-bit instruction: `instruction[15]` distinguishes A-instructions (`0`) from C-instructions (`1`). A `Mux16` chooses between the instruction constant and `aluOut` for `ARegister`. `DRegister` loads `aluOut` on `instruction[15] & instruction[4]`. The `ALU` operates on `D` and either `A` or `inM` (`instruction[12]`). `writeM` is `instruction[15] & instruction[3]`. Jump logic checks `jlt` (`ng`), `jeq` (`zr`), and `jgt` (`!(zr | ng)`) when `instruction[15]=1`; if triggered, `PC` loads `A`, otherwise increments.
   - **`Memory.hdl`:** Uses `address[14]` and `address[13]` to route reads and writes: `0x` → `RAM16K` (`0..16383`), `10` → `Screen` (`16384..24575`), `11` → `Keyboard` (`24576`, read-only).
   - **`Computer.hdl`:** Connects `ROM32K` (`address=pc` → `instruction`), `CPU`, and `Memory` in a closed loop with `reset`.
   - *Built-in note:* Standard built-in primitives (`Nand, DFF, ARegister, DRegister, ROM32K, Screen, Keyboard`) are used, and built-in `RAM16K` / `PC` are used only when running `ComputerAdd/Max/Rect.tst` because those scripts probe `RAM16K[0]` / `PC[]` internal state (our custom `RAM16K.hdl` and `PC.hdl` pass `RAM16K.tst` and `PC.tst` independently).

2. **How does `assembler.py` work?**
   - **Pass 0:** Strips `//` and `/* ... */` comments and blank lines while preserving original line numbers.
   - **Pass 1:** Scans instructions, records every `(LABEL)` in the symbol table with the ROM address of the next real instruction (labels do not occupy ROM space).
   - **Pass 2:** Translates each instruction into 16 bits (`0` + 15-bit address for A-instructions; `111 + a + c1..c6 + d1..d3 + j1..j3` for C-instructions).

3. **How are labels and variables allocated?**
   - Predefined symbols (`SP=0..THAT=4`, `R0..R15`, `SCREEN=16384`, `KBD=24576`) are loaded first.
   - Pass 1 adds labels with ROM addresses (`0, 12, 20, ...`).
   - Pass 2 assigns any unseen `@variable` sequentially to RAM addresses starting at **16** (`startRow=16`, `width=17`, `height=18`, `fill=19`, `addr=20`, ...).

4. **What is your additional feature for K = 93?**
   - Since `93 mod 3 = 0`, `assembler.py` automatically exports all predefined symbols, Pass-1 labels, and Pass-2 variables with their assigned addresses into `symbols.txt`.

5. **How does Hack screen memory work?**
   - Memory-mapped from `16384` (`SCREEN`) to `24575` (`8192` words = `256` rows × `32` words/row). Each 16-bit word controls 16 horizontal pixels. Row `r` starts at `16384 + 32 × r`. Writing `-1` (`1111111111111111`) draws 16 black pixels; writing `0` clears them white.

6. **How does `Box.asm` draw and erase the box?**
   - `MAIN` continuously polls `@KBD` (`24576`). If `KBD != 0`, `fill = -1`; if `KBD == 0`, `fill = 0`. `PAINT` adds `32` to `SCREEN` `startRow` (`93`) times to reach `19360`, then nested loops (`ROW` and `WORD`) write `fill` into `2` words per row across `20` rows (`40` words = `640` pixels) and loop back to `MAIN`.

7. **What mistake did you encounter and fix?**
   - Initially forgetting to copy `addr` into a separate per-row pointer `ptr` and reload `wordsLeft = width` at the start of every row caused only row 93 (a 1-row line) to render. Reloading `ptr = addr` and `wordsLeft = width` at `(ROW)` while advancing `addr = addr + 32` only at `(ROW_DONE)` fixed it.
