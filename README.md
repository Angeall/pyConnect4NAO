# Connect4NAO

## Context
 - This module was made in the context of a project made at the University of Mons
  (UMONS) for a Master degree in Computer Sciences.
 - The project was made under the direction of the Professor Tom Mens
  and M. Pierre Hauweele.
 - Every technical detail is written in the file `Connect4NAO-Report.pdf`

## Goal
 The goal of this solution is to made the humanoid robot [NAO](https://www.aldebaran.com/fr/cool-robots/nao) 
   play the Connect 4 game.

[![Connect4NAO](http://i.imgur.com/kXAWzcl.png)](https://www.youtube.com/watch?v=UyRx1V4rx-M "")
 

## Dependencies

 - [`Python 2.7`](https://www.python.org/downloads/)
 - [`Python NAOqi SDK`](http://doc.aldebaran.com/2-1/dev/python/install_guide.html)
 - [`OpenCV 3.0`](http://opencv.org/downloads.html)
 - [`Numpy`](https://pypi.python.org/pypi/numpy/1.10.1)
 - [`Scipy`](https://pypi.python.org/pypi/scipy/0.17.0)
 - [`Hampy`](https://pypi.python.org/pypi/hampy/1.4.1) (requires [`PIL`](http://www.pythonware.com/products/pil/))
 - [`Docopt`](https://pypi.python.org/pypi/docopt/0.6.2)
   <!--- - [`Shapely`] <> (https://pypi.python.org/pypi/Shapely) --->

## How to launch
 - Install the dependencies
 - Launch a terminal emulator in the `src` folder
 - The following line lists and explains each command available in the software:

        python connect4nao.py --help

 - The following line explains the different options available for the command `<command>`

        python connect4nao.py <command> --help
