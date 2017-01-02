::

	 ___  ___             _ _
	| _ \/ __|_ __ ____ _(_) |
	|   /\__ \ V  V / _` | | |
	|_|_\|___/\_/\_/\__,_|_|_|

RSwail is an implementation of the perpetually-being-redeveloped-language Swail.

This implementation is being written in RPython because it should automate most
boring details of actually generating code, allowing us to just implement
things and not worry about it being too slow.

For more detailed documentation, see the contents of the ``docs`` directory.

Swail
=====

Swail is a programming language designed to do what you want, expect and say,
in that order. The name is officially an acronym for "I forgot the words in
this acronym", but you can also expand it to:

* Super Wumbo Awesome Interesting Language
* Some Witty Acronym for an Interpreted Language
* Swail Wins Against Inferior Languages
* System Without Any Intelligence Left

or if you are currently wearing a suit, just call it:

* The Swail Language

Despite maybe standing for the initial letters of words, you should write and
pronounce Swail like it's a word (or more precisely, a proper noun), i.e.
"Swail" and /sweɪl/, not "SWAIL" and /ɛs ˈdʌbl̩.juː eɪ aɪ ɛl/.

Swail is supposed to be straightforward to write and read. It draws inspiration
from Python and Haskell, which you might appreciate if you enjoy that kind of
languages.  A lot of the language features are explained by analogy to either
of those languages. However, it does have its own conventions, so you can't
always translate concepts one-to-one between languages.

Building and Installing
=======================

TL;DR::

	cd /path/to/source/RSwail # you should see README.rst in this directory
	hg clone https://bitbucket.org/pypy/pypy
	sudo apt-get install pypy python2-pytest # or yum or dnf or pacman or ...
	make
	./swail tests.swa

To compile RSwail, you need to unpack a recent edition of `PyPy
<http://pypy.org>`_ into a directory ``pypy`` in the RSwail directory. You
should also add the pypy executable to your search path. If not, you can still
build RSwail, it just takes painfully long.  Then, install the py.test library
for Python 2. Before compilation, we run a test suite to make sure RSwail will
work on your computer.

Once you have installed the dependencies, go to the RSwail directory and run
``make``. After a very long time in which your terminal will be filled with
nice colored fractals, you get the ``swail`` executable. At this point, you can
either move this executable to your favourite binaries directory (e.g.
``/usr/local/bin``) or perform a sanity check against the file ``tests.swa``
which is also in the RSwail directory.

Development
===========

The basic testing command is ``make test``. This will run the Python test
suite, compile a non-JIT interpreter, run the Swail test suite, compile a JIT
interpreter and run the test suite again. Note that the compilation alone will
take tens of minutes, so you probably want to make sure the Python test suite
is very accurate.

If you want to get an idea of how RSwail works, you can start with the file
``target.py`` which contains the entry points for all the interpreter editions.
If you want to get an idea of how Swail works, you can start with the file
``test.swa`` which is used to verify RSwail implements the Swail language
correctly.  Implementations for language features can be found in the
``rswail`` directory, Python test cases can be found in the ``test`` directory
and Swail examples and test cases in the ``example`` directory.

Documentation can be found in this README file and in the directory ``docs``.
To build documentation, you need to install the Sphynx documentation
generator::

	pip install sphynx sphynx-autobuild

Building documentation is done with the command ``make docs``.

License
=======

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program.  If not, see <http://www.gnu.org/licenses/>.
