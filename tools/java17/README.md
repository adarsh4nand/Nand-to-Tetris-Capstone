# Launching the simulators with JDK 17

The nand2tetris simulators date from 2006. On very new JDKs (21, 25, 26) they usually start
and run, but the **CPU Emulator stops receiving keyboard input** — which is exactly what the
box program needs. If the screen stays white while a key is held, this is the fix.

1. Install **Temurin 17** (LTS) for Windows 64-bit from <https://adoptium.net>.
2. Copy the two `.bat` files from this folder into your nand2tetris `tools` folder, next to
   `CPUEmulator.bat` and `HardwareSimulator.bat`.
3. Start the emulator by double-clicking **`CPUEmulator-Java17.bat`** instead. It prints the
   Java it is using and then opens the normal emulator window.

The launchers look for `C:\Program Files\Eclipse Adoptium\jdk-17*` and
`C:\Program Files\Java\jdk-17*`, so they work whatever exact 17.x version you install.

Quick check that the keyboard is truly reaching the emulator: load `Box.hack`, find address
`24576` in the RAM pane and hold a letter key — the cell must show the key code (65 for A),
not 0.
