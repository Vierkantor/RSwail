.. _swail-tutorial:

Tutorial
********

Welcome to Swail! This document is intended as a friendly introduction
counterpart to the more precise :ref:`swail-reference`. If you want to learn
how to use Swail, you can check this out, but if you already know quite a bit,
the reference is probably more interesting.

If you set your text editor to replace tabs with spaces, you probably want to
change it back to enjoy programming in Swail.

Hello, World!
=============

The traditional way to show off a language is to demonstrate a program that
outputs "Hello, World!". In Swail, you can write it like this::

	def main():
		print("Hello, World!")

Copy these two lines to a text file, save it with a name like "hello.swa" and
use your favorite compiler/interpreter to run it (e.g. "swail hello.swa"). You
should see something like the following::

	$ swail hello.swa
	Hello, World!
	$

Try playing around with this program! What happens if you copy and paste the
line with ``print`` on it, and change the text between quotes? What happens
when you replace the double quotes with single ones?

Now that you've built a very simple program, let's try something more difficult.

Number guesser
==============

Let's build a very simple game: the computer thinks of a number and you try to
guess it. If you get it right, the game stops, else the computer says whether
your guess was too high or too low and lets you try again. Starting off with a
blank program, we'll use the ``print`` function as in the previous expample.
This function writes whatever you give it between the parentheses on the
screen. In this case, we give it a ``string`` that writes a little
introductory message::

	def main():
		print("I'm thinking of a number...")

If you run the program now, you'll see the program wrting that introduction
message and stopping. That's not very interesting, so we'll try to read a
guess. The ``input`` function reads a line of user input. Because it doesn't
need any other information, we don't need to write anything between the
parentheses. The program will look as follows::

	def main():
		print("I'm thinking of a number...")
		guess = input()
		print(guess)

When you run it, the program will now print out another line starting with the
symbol ``>``. When you type a number and press return, the program writes the
number back to you::

	$ swail guesser.swa
	I'm thinking of a number...
	> 37
	37
	$

You can play around with this program for a bit. Can you predict what will
happen when you write the line ``guess = input()`` twice?

Let's make the computer actually think of a number. We want the number to be
different each time you run the program, so we need some way to get
unpredictable numbers. Luckily, other people have already made code for doing
this. The ``require`` declaration tells Swail to load a certain module, in this
case ``random``, and the function ``random.uniform`` chooses a number in the
given range. Putting it all together::

	require random
	
	def main():
		print("I'm thinking of a number...")
		correct-answer = random.uniform(1..100)
		guess = input()
		print(guess)
		print("The correct answer is:")
		print(correct-answer)

When you have made this change, you can run the program again and see the
results::

	$ swail guesser.swa
	I'm thinking of a number...
	> 37
	37
	The correct answer is:
	42
	$

The next step is to check whether the guess is correct, too high or too low. To
write this out in Swail code, we will use the ``<=>`` operator, which
determines whether the first value is smaller than, equal to, or larger than
the second value. There's only one problem, which is that we can't directly use
the operator on ``guess`` and ``correct-answer``. If we try it::

	comparison = guess <=> correct-answer

we get an error which looks something like::

	=== FAILURE ===
	in function 'main'
	in 'comparison = guess <=> correct-answer'
	in 'guess <=> correct-answer'
		No instance for 'compare(str, int)'

This is because the guess and the correct answer have different types, and
trying to compare them would be like comparing apples and oranges. Swail
doesn't know whether some string represents a larger number than an integer,
for the same reason that asking whether an elephant is bigger than the color
purple doesn't make sense. To make sure we compare sensibly, let's make the
guess into an integer first using the ``int`` function. Afterward, we can
compare it::

	require random
	
	def main():
		print("I'm thinking of a number...")
		correct-answer = random.uniform(1..100)
		guess = int(input())
		print(guess)
		print("The correct answer is:")
		print(correct-answer)
		comparison = guess <=> correct-answer
		print("The comparison is:")
		print(comparison)

When we run this version, the program tells us which number is bigger::

	$ swail guesser.swa
	I'm thinking of a number...
	> 37
	37
	The correct answer is:
	5
	The comparison is:
	ord.greater-than()
	$

(What happens when you enter input that doesn't make sense as an integer?)

The next step is to interpret the comparison in words instead of in code. We
will use the ``match`` statement for this. It takes a value and compares it
with various cases. The code that follows the first case that matches is used.
We can use the ``match`` statement like this::

	require random
	
	def main():
		print("I'm thinking of a number...")
		correct-answer = random.uniform(1..100)
		guess = int(input())
		print(guess)
		print("The correct answer is:")
		print(correct-answer)
		comparison = guess <=> correct-answer
		match comparison
		case ord.less-than():
			print("You guessed too small. Don't misunderestimate me!")
		case ord.equal():
			print("You guessed correctly, well done!")
		case ord.greater-than():
			print("You guessed too big. Don't get too ambitious!")

When we run the code now, we'll see more understandable messages::

	$ swail guesser.swa
	I'm thinking of a number...
	> 37
	37
	The correct answer is:
	57
	You guessed too small. Don't misunderestimate me!
	$

(What happens when we accidentally leave out one of the cases?)

We're nearly there! Now we need to allow the user to keep guessing until they get it right. To repeat code indefinitely, we can use the ``loop`` statement. If we want to stop looping, we can use the ``break`` statement which stops the execution of the loop immediately. It will also skip any statements that would be executed before the loop restarts! Placing the right parts of our code in a loop gives the following program::

	require random
	
	def main():
		print("I'm thinking of a number...")
		correct-answer = random.uniform(1..100)
		loop:
			guess = int(input())
			print(guess)
			print("The correct answer is:")
			print(correct-answer)
			comparison = guess <=> correct-answer
			match comparison
			case ord.less-than():
				print("You guessed too small. Don't misunderestimate me!")
			case ord.equal():
				print("You guessed correctly, well done!")
				break
			case ord.greater-than():
				print("You guessed too big. Don't get too ambitious!")

There's just one problem, can you spot it?::

	$ swail guesser.swa
	I'm thinking of a number...
	> 37
	37
	The correct answer is:
	64
	You guessed too small. Don't misunderestimate me!
	> 64
	64
	You guessed correctly, well done!
	$

The problem is that we still tell the user the correct answer! They should be
able to win in two rounds if they're paying attention. Just take out the calls
to ``print`` and we should have our very first guessing game::

	require random
	
	def main():
		print("I'm thinking of a number...")
		correct-answer = random.uniform(1..100)
		loop:
			guess = int(input())
			comparison = guess <=> correct-answer
			match comparison
			case ord.less-than():
				print("You guessed too small. Don't misunderestimate me!")
			case ord.equal():
				print("You guessed correctly, well done!")
				break
			case ord.greater-than():
				print("You guessed too big. Don't get too ambitious!")

It turns out this game has connections with certain very important problems in programming. If you're interested, check out the Wikipedia page on `binary search <https://en.wikipedia.org/wiki/Binary_search>`_ for more information.
