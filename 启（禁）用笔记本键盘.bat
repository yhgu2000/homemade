@echo off

if "%1" == "disable" (
    echo sc config i8042prt start=disabled
    sc config i8042prt start=disabled
) else (
    echo sc config i8042prt start=demand
    sc config i8042prt start=demand
)

pause
exit
