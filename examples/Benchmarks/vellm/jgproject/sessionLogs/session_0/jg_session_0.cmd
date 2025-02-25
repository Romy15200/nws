# ----------------------------------------
# Jasper Version Info
# tool      : Jasper 2024.06
# platform  : Linux 3.10.0-1160.62.1.el7.x86_64
# version   : 2024.06p002 64 bits
# build date: 2024.09.02 16:28:38 UTC
# ----------------------------------------
# started   : 2025-02-25 20:58:26 IST
# hostname  : vlsi-ria68.vlsidomain
# pid       : 31285
# arguments : '-label' 'session_0' '-console' '//127.0.0.1:42723' '-nowindow' '-style' 'windows' '-exitonerror' '-data' 'AAABLHicVY9LDoJAEEQfJu68ihBN3LHyBp6A+CFqHJAgoDs9lAfyJljdyoJe9Kd6qqonAtJn3/d4RJ9fJY0Yh82TMbJ5jSpMB/LwxAgz5uzY0rDnpPlNQsuNnFo5Ub5SUGkOmkrujuY8xDE8qDdkrVq6RqFNzcXRznlBWKKN4QcysUy1co+G81/BPDtXybw/qi5Y6b6KJbE7Fa6eiZW7e+x3B//NF1WeLB0=' '-proj' '/users/rompel/nws/examples/Benchmarks/vellm/jgproject/sessionLogs/session_0' '-init' '-hidden' '/users/rompel/nws/examples/Benchmarks/vellm/jgproject/.tmp/.initCmds.tcl' '/users/rompel/nws/examples/Benchmarks/vellm/hard_properties/seven_seg_15-p2.lemma_temp.tcl' '-hidden' '/users/rompel/nws/examples/Benchmarks/vellm/jgproject/.tmp/.postCmds.tcl'

analyze -sv09 /users/rompel/nws/examples/Benchmarks/vellm/hard_properties/seven_seg_15-p2.lemma_temp.sv
elaborate
reset -none
clock clk
prove -all
