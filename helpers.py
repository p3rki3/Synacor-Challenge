from itertools import permutations

def solve_coin_puzzle():
    coins = {"red": 2, "concave": 7, "corroded": 3, "blue": 9, "shiny": 5 }
    for perm in permutations(coins):
        if coins[perm[0]] + coins[perm[1]] * coins[perm[2]] ** 2 + coins[perm[3]] ** 3 - coins[perm[4]] == 399:
            #print("The correct order is as follows = ", perm, ". Inputting solution into VM...")
            return ''.join("use " + p + " coin\n" for p in perm), "Inputting corrent solution into VM...\n"
    print("Solution not found; very strange; exiting...")
    exit(1)

def calc_energy_level():
    stored_result = 25734       # Short circuit long boring calc - set to 0 if you really want to wait for it to work out the code
    for i in range(stored_result, 32768):
        if ack(ack(i, i), i) == 6:  # An Ackerman function I believe?
            #print("The target value for register 8 is",  i, "; calibrating the teleporter...")
            return i, "The target value for register 8 is " + str(i) + "; calibrating the teleporter...\n"
        #if i % 2000 == 0:
        #    print(f"Checking next 2000 candidate solutions, startng with {i:5d}")

def ack(i, j):
    ack_1, ack_2 = ack2(i, j + 1, 0x8000), ack2(i, j + 1, j * 0x8000) - 1
    return (ack_1 * ((j + 1) ** 2 + j) + ack_2 // j * (2 * j + 1)) & 0x7fff

def ack2(i, j, k):
    retval = 1
    for _ in range(i):
        retval = (retval * j) % k
    return retval

def mirror_me(code):
    mirror_code = ''
    for _, ch in enumerate(code[::-1]):
        if ch in 'wWYuUiIoOAHxXvVmM80':
            mirror_code += ch
        elif ch == 'p':
            mirror_code += 'q'
        elif ch == 'q':
            mirror_code += 'p'
        elif ch == 'd':
            mirror_code += 'b'
        elif ch == 'b':
            mirror_code += 'd'
        else:
            print('Error - unrecognised code: ', ch)
    return mirror_code