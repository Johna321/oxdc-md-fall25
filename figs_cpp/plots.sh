#!/bin/bash

gnuplot -e "set term pngcairo size 900,450; set out 'eq1_rmsd_ca.png'; \
set xlabel 'frame'; set ylabel 'Å'; plot 'eq1_rmsd_ca.dat' u 1:2 w l ti 'RMSD CA'"

gnuplot -e "set term pngcairo size 1000,400; set out 'eq1_rmsf_ca.png'; \
set xlabel 'residue'; set ylabel 'Å'; plot 'eq1_rmsf_ca.dat' u 1:2 w l ti 'RMSF CA'"
