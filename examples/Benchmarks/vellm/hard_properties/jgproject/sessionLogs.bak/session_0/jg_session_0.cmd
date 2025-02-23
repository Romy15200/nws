# ----------------------------------------
# Jasper Version Info
# tool      : Jasper 2024.06
# platform  : Linux 3.10.0-1160.62.1.el7.x86_64
# version   : 2024.06p002 64 bits
# build date: 2024.09.02 16:28:38 UTC
# ----------------------------------------
# started   : 2025-02-22 18:48:51 IST
# hostname  : vlsi-ria84.vlsidomain
# pid       : 14565
# arguments : '-label' 'session_0' '-console' '//127.0.0.1:43677' '-nowindow' '-style' 'windows' '-exitonerror' '-data' 'AAAAqnicVYwxCoAwFENfBTevUkFdewlPICqiQ4UiXZz0qN6k/lYcmgz5CT9RgLlCCCSo51OMIkf0RZ70d6ZQ/uX/JRYqNBMjnplNfMvKIf5koBFqHB01loVdOEru0+0kjS2btl5zVRIz' '-proj' '/users/rompel/nws/examples/Benchmarks/vellm/hard_properties/jgproject/sessionLogs/session_0' '-init' '-hidden' '/users/rompel/nws/examples/Benchmarks/vellm/hard_properties/jgproject/.tmp/.initCmds.tcl' 'gray_11-p3.lemma_temp.tcl' '-hidden' '/users/rompel/nws/examples/Benchmarks/vellm/hard_properties/jgproject/.tmp/.postCmds.tcl'

analyze -sv09 /users/rompel/nws/examples/Benchmarks/vellm/hard_properties/gray_11-p3.lemma_temp.sv
elaborate
reset -none
clock clk
prove -all
exit -force
