set yrange [0:19]
set xrange [0:3]
set title "Plot of maxRadius as a function of the Distance"
set xlabel "Distance (m)" 
set ylabel "maxRadius (px)"
f(x) = 8.5468*x**-0.7126
plot f(x) title "8.5468*(x**-0.7126)", "maxRadius.txt" title "Calibration value"