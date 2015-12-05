set yrange [0:15]
set xrange [0:3]
set title "Plot of minRadius as a function of the Distance"
set xlabel "Distance (m)" 
set ylabel "minRadius (px)"
f(x) = 4.4143*x**-1.1446
plot f(x) title "4.4143*(x**-1.1446)", "minRadius.txt" title "Calibration value"