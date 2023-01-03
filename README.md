# Synacor-Challenge

My solution to the synacor challenge

Google the synacor challenge to find the website.  
  arch-spec gives you all the instructions you need to build a vm that can run....
  challenge.bin - contains all the data and code that forms the second part of the challenge.
  
The first part of the challenge is to use the arch-spec to build a vm in any language you like (mine is python3) that can run the binary.  You collect some codes along the way that you can input into the synacor challenge website to track your progress.

The challenge.bin file contains a lot of self-testing code that validates whether your vm is conformant to the arch-spec or not.  If it is, then you get to the second part of the challenge - an old fashioned text adventure game.

As well as the usual text adventure game stuff (exploring; collecting and using certain objects; avoiding dying, etc.), you will also have to solve some puzzles.  Two can be solved either by writing a short program, or even pen and paper.  One of the problems seemed to require some disassembly and analysis of a portion of code, and then some minor changes to the code run in the vm to make the solution work.  There are probably multiple ways to crack that one.

Along the way, my vm (vm.py) grew as I added a means of regurgitating game text instructions (instr.txt) into the vm (to save typing the same stuff time and again).  I also added special codes into the insgtruction file and the function that processes it to do various things like speed up, slow down the vm, output the current vm program code (it modifies itself in-game I think), and some trace and disassembly functions.

Rather than a massive 'case' type statement or if, elif, etc for each instruction in the VM, I have used a dictionary of opcodes that point to the respective functions, so the despatcher to call the right function is really neat and simple.  Most of the vm instructions are handled in one-line functions in python.

Rather enjoyed this challenge - the grin on my face when my VM passed the self tests in challenge.bin and booted up an adventure game was worth the effort.
