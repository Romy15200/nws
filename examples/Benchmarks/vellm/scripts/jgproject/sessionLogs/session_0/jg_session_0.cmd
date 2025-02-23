# ----------------------------------------
# Jasper Version Info
# tool      : Jasper 2024.06
# platform  : Linux 3.10.0-1160.62.1.el7.x86_64
# version   : 2024.06p002 64 bits
# build date: 2024.09.02 16:28:38 UTC
# ----------------------------------------
# started   : 2025-02-22 19:14:14 IST
# hostname  : vlsi-ria84.vlsidomain
# pid       : 24510
# arguments : '-label' 'session_0' '-console' '//127.0.0.1:39706' '-nowindow' '-style' 'windows' '-exitonerror' '-data' 'AAABInicVY9LDsIwDERfkdhxlTZCbLviBpygKlABIi1VKb8VnIdTcZMyMXQRR7IzY884SYD8OQwDFsnnV8kT4gh4EjOrV1RhOorHkSCYkbKmpGfDXviN48KZik7ZKZ+oaYW9UMPN2Iq7NIH3ugdmqdqYR61Ox9HYq+m8OKdO4LcUUgXX1nb0HP4OO6GSh/pznVT9BZn51+ZZaLaynZm91tsfvof8KgQ=' '-proj' '/users/rompel/nws/examples/Benchmarks/vellm/scripts/jgproject/sessionLogs/session_0' '-init' '-hidden' '/users/rompel/nws/examples/Benchmarks/vellm/scripts/jgproject/.tmp/.initCmds.tcl' '/users/rompel/nws/examples/Benchmarks/vellm/hard_properties/gray_11-p3.lemma_temp.tcl' '-hidden' '/users/rompel/nws/examples/Benchmarks/vellm/scripts/jgproject/.tmp/.postCmds.tcl'

analyze -sv09 /users/rompel/nws/examples/Benchmarks/vellm/hard_properties/gray_11-p3.lemma_temp.sv
elaborate
reset -none
clock clk
prove -all
exit -force
