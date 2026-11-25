@echo off
rem ---------------------------------------------------------------------------
rem  Starts the nand2tetris CPU Emulator with JDK 17 instead of whatever Java
rem  is first on the PATH. Copy this file into the nand2tetris "tools" folder
rem  (next to CPUEmulator.bat) and double-click it.
rem
rem  Why: the simulators are from 2006 and on very new JDKs (21, 25, 26) they
rem  run but stop receiving keyboard input, which the box program needs.
rem ---------------------------------------------------------------------------
setlocal enabledelayedexpansion

set "JAVA17="
for /d %%D in ("C:\Program Files\Eclipse Adoptium\jdk-17*") do (
    if exist "%%~fD\bin\java.exe" set "JAVA17=%%~fD\bin\java.exe"
)
if not defined JAVA17 (
    for /d %%D in ("C:\Program Files\Java\jdk-17*") do (
        if exist "%%~fD\bin\java.exe" set "JAVA17=%%~fD\bin\java.exe"
    )
)
if not defined JAVA17 (
    echo.
    echo Could not find a JDK 17.
    echo Install Temurin 17 from https://adoptium.net and run this again.
    echo.
    pause
    exit /b 1
)

echo Using: "%JAVA17%"
cd /d "%~dp0"
"%JAVA17%" -classpath "bin\classes;bin\lib\Hack.jar;bin\lib\HackGUI.jar;bin\lib\Simulators.jar;bin\lib\SimulatorsGUI.jar;bin\lib\Compilers.jar" CPUEmulatorMain
