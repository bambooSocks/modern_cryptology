import random
from aes import SI, encrypt, r_con, subWord, rotWord, Nk, Nb, Nr

# Prepares a lambda set
# randomValue - initial value in the positions besides the chosen index
# chosenIndex - index at which the values with the XOR property are written to
def generateLambdaSet(randomValue=0, chosenIndex=0):
    lambdaSet = []
    for index in range(256):
        currentState = [randomValue] * 16
        currentState[chosenIndex] = index
        lambdaSet.append(currentState)
    return lambdaSet

# Encrypts lambda set
def encryptLambdaSet(lambdaSet, key):
    # apply encryption with provided key on each of the states in lambda set
    return [encrypt(state, key) for state in lambdaSet]

# Reverse the value of a byte using given guess and position
def reverseGuessPositionValue(guess, position, lambdaState):
    # remove guess from the value at the position and invert the S-box
    return SI[lambdaState[position]^guess]

# Verify a guess at given position
def verifyGuessPosition(guess, position, encryptedLambdaSet):
    result= 0
    # loop through all states in lambda set and verify that the XOR property holds for given guess
    for lambdaState in encryptedLambdaSet:
        result ^= reverseGuessPositionValue(guess, position, lambdaState) 
    return result == 0

# Finds all possible guesses for given position in the last round key
# position - position in the last round key to be guessed
# encryptedLambdaSets - list of lambda sets encrypted by the key to be guessed    
def checkAllGuesses(position, encryptedLambdaSet):
    correctGuesses = []
    # go through all possible guesses and append it to the result if the guess is correct
    for guess in range(256):
        if verifyGuessPosition(guess, position, encryptedLambdaSet):
            correctGuesses.append(guess)
    return correctGuesses

# Finds the correct guess for given position in the last round key
# position - position in the last round key to be guessed
# encryptedLambdaSets - list of lambda sets encrypted by the key to be guessed
def getFinalGuess(position, encryptedLambdaSets):
    # get all the guesses for the first lambda set
    correctGuesses = checkAllGuesses(position, encryptedLambdaSets[0])
    
    # in case that there is only one guess return
    if len(correctGuesses)==1:
        return correctGuesses[0]

    # check for the rest of lambda sets
    for idx in range(1,len(encryptedLambdaSets)):
        # check guesses for next lambda set
        cg = checkAllGuesses(position, encryptedLambdaSets[idx])
        # find intersection of the previous guesses and the new ones
        # this should reduce the set of initial guesses to one value
        correctGuesses=[value for value in cg if value in correctGuesses]
        # in case that there is only one guess return
        if len(correctGuesses)==1:
            return correctGuesses[0]
    # in the case that the lambda sets do not reduce the guesses to only one guess
    # then the function throws an exception
    raise Exception("couldn't find final guess")

# Helper function reversing word order of 4-word lists
# wordList - 16-byte list
def reverseWordListOrder(wordList):
    result = []

    # loop in reverse through each word and copy the bytes in correct order
    for i in reversed(range(4)):
        result.append(wordList[4 * i])
        result.append(wordList[4 * i + 1])
        result.append(wordList[4 * i + 2])
        result.append(wordList[4 * i + 3])

    return result

# lastRoundKey is 4 byte list
# reverseExpandedKey (Nr + 1) keys * 16 bytes = 80 bytes
def invertKeySchedule(lastRoundKey):
    # put the last round key into the reverse expanded key buffer in reverse word order
    revExK = reverseWordListOrder(lastRoundKey)

    # loop through all 4 words in each round (4x4 times)
    for i in range(0, Nb * Nr):
        # figure out indices for word which is 4-words ahead and 3-words ahead
        ahead4wIdx = 4 * i
        ahead3wIdx = ahead4wIdx + Nk
        # get the words for the given indices
        prevRound = [revExK[ahead4wIdx], revExK[ahead4wIdx + 1], revExK[ahead4wIdx + 2], revExK[ahead4wIdx + 3]]
        temp = [revExK[ahead3wIdx], revExK[ahead3wIdx + 1], revExK[ahead3wIdx + 2], revExK[ahead3wIdx + 3]]

        # if it is the start word (since the buffer is reversed it is the last one in round key) apply the diffusion algorithm on the 3-words ahead word 
        if i % Nk == 3:
            temp = subWord(rotWord(temp))
            # the r_con index also needs to be inverted hence number of rounds - current round
            temp[3] ^= r_con[Nk - (i / Nk)]

        # revert the final XOR and append the result to the inverted expanded key buffer
        for j in range(0, 4):
            revExK.append(temp[j] ^ prevRound[j])

    # return the last 4 words (representing the key) in reverse word order
    return reverseWordListOrder(revExK[-16:])

# Key guessing function
# encrypredLambdaSets - list of lambda sets encrypted by the key to be guessed
def crack(encryptedLambdaSets):
    lastRoundKey= []

    # guess each key byte separately
    for position in range(16):
        lastRoundKey.append(getFinalGuess(position, encryptedLambdaSets))
    
    # return original key
    return invertKeySchedule(lastRoundKey)

if __name__ == "__main__":
    # test key randomly generated
    keyToGuess = [random.randint(0x00, 0xFF) for _ in range(16)]

    # four lambda sets used to crack the key
    lambdaSets = [generateLambdaSet(0x00), generateLambdaSet(0x12), generateLambdaSet(0x34), generateLambdaSet(0xFF)]
    # encrypted lambda sets (by the test key) used for cracking
    encryptedLambdaSets = map(lambda ls: encryptLambdaSet(ls, keyToGuess), lambdaSets)

    guessedKey = crack(encryptedLambdaSets)

    print("Key to guess:", keyToGuess)
    print("Guessed key:", guessedKey)
