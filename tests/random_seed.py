# Make the seed logged such that the test runs can be reproduced
from random import randint

test_seed = randint(0, 1000000)
print(f"\n\nThe seed for the random module was: {test_seed}\n")
