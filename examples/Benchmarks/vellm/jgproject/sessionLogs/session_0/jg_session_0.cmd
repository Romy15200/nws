# ----------------------------------------
# Jasper Version Info
# tool      : Jasper 2024.06
# platform  : Linux 3.10.0-1160.62.1.el7.x86_64
# version   : 2024.06p002 64 bits
# build date: 2024.09.02 16:28:38 UTC
# ----------------------------------------
# started   : 2025-02-25 13:21:16 IST
# hostname  : vlsi-ria68.vlsidomain
# pid       : 3000
# arguments : '-label' 'session_0' '-console' '//127.0.0.1:38800' '-nowindow' '-style' 'windows' '-exitonerror' '-data' 'AAABIHicVY5LDsIwDERfkdhxlVIhtl1xA06ACpSPSEtVym8Fx+FY3CSMQ7uII9mZZ4+TBMhf3ntCJN9/JU+Iw/QoJst3VGE8mIcRM0xIWVPQseEg/SHjyoWSVjlTPlPRSDupmnugJQ95jDvdjSxU67CjUqflFOgt+JxYpo7xLSu5bGsT3ug49hvsB07dnciwda+JgqfoTCeVZ860n7T4AUE+KZc=' '-proj' '/users/rompel/nws/examples/Benchmarks/vellm/jgproject/sessionLogs/session_0' '-init' '-hidden' '/users/rompel/nws/examples/Benchmarks/vellm/jgproject/.tmp/.initCmds.tcl' '/users/rompel/nws/examples/Benchmarks/vellm/hard_properties/tcl_files/gray_11-p3.tcl' '-hidden' '/users/rompel/nws/examples/Benchmarks/vellm/jgproject/.tmp/.postCmds.tcl'
analyze -sv09 /users/rompel/nws/examples/Benchmarks/vellm/hard_properties/gray_11-p3.sv
elaborate
reset -none
clock clk
prove -all
