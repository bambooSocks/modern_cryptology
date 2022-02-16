import random
from aes import SI, encrypt, r_con, subWord, rotWord, Nk, Nb, Nr

# Prepares a delta set
# randomValue - initial value in the positions besides the chosen index
# chosenIndex - index at which the values with the XOR property are written to
def generateDeltaSet(randomValue=0, chosenIndex=0):
    deltaSet = []
    for index in range(256):
        currentState = [randomValue] * 16
        currentState[chosenIndex] = index
        deltaSet.append(currentState)
    return deltaSet

# Encrypts delta set
def encryptDeltaSet(deltaSet, key):
    # apply encryption with provided key on each of the states in delta set
    return [encrypt(state,key) for state in deltaSet]

# Reverse the value of a byte using given guess and position
def reverseGuessPositionValue(guess, position, deltaState):
    # remove guess from the value at the position and invert the S-box
    return SI[deltaState[position]^guess]

# Verify a guess at given position
def verifyGuessPosition(guess, position, encryptedDeltaSet):
    result= 0
    # loop through all states in delta set and verify that the XOR property holds for given guess
    for deltaState in encryptedDeltaSet:
        result ^= reverseGuessPositionValue(guess, position, deltaState) 
    return result == 0

# Finds all possible guesses for given position in the last round key
# position - position in the last round key to be guessed
# encryptedDeltaSets - list of delta sets encrypted by the key to be guessed    
def checkAllGuesses(position, encryptedDeltaSet):
    correctGuesses = []
    # go through all possible guesses and append it to the result if the guess is correct
    for guess in range(256):
        if verifyGuessPosition(guess, position, encryptedDeltaSet):
            correctGuesses.append(guess)
    return correctGuesses

# Finds the correct guess for given position in the last round key
# position - position in the last round key to be guessed
# encryptedDeltaSets - list of delta sets encrypted by the key to be guessed
def getFinalGuess(position, encryptedDeltaSets):
    # get all the guesses for the first delta set
    correctGuesses = checkAllGuesses(position, encryptedDeltaSets[0])

    # check for the rest of delta sets
    for idx in range(1,len(encryptedDeltaSets)):
        # in case that there is only one guess return
        if len(correctGuesses)==1:
            return correctGuesses[0]
        # check guesses for next delta set
        cg = checkAllGuesses(position, encryptedDeltaSets[idx])
        # find intersection of the previous guesses and the new ones
        # this should reduce the set of initial guesses to one value
        correctGuesses=[value for value in cg if value in correctGuesses]
    # in the case that the delta sets do not reduce the guesses to only one guess
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
    reverseExpandedKey = reverseWordListOrder(lastRoundKey)

    # loop through all 4 words in each round (4x4 times)
    for i in range(Nk, Nb * (Nr + 1)):
        # figure out indices for word which is 4-words ahead and 3-words ahead
        prevRoundIdx = 4 * (i - Nk)
        nextPrevRoundIdx = prevRoundIdx + Nk
        # get the words for the given indices
        prevRound = [reverseExpandedKey[prevRoundIdx], reverseExpandedKey[prevRoundIdx + 1], reverseExpandedKey[prevRoundIdx + 2], reverseExpandedKey[prevRoundIdx + 3]]
        temp = [reverseExpandedKey[nextPrevRoundIdx], reverseExpandedKey[nextPrevRoundIdx + 1], reverseExpandedKey[nextPrevRoundIdx + 2], reverseExpandedKey[nextPrevRoundIdx + 3]]

        # if it is the start word (since the buffer is reversed it is the last one in round key) apply the diffusion algorithm on the 3-words ahead word 
        if i % Nk == 3:
            temp = subWord(rotWord(temp))
            # the r_con index also needs to be inverted hence number of rounds - current round
            temp[3] ^= r_con[(Nk + 1) - (i / Nk)]

        # revert the final XOR and append the result to the inverted expanded key buffer
        for j in range(0, 4):
            reverseExpandedKey.append(temp[j] ^ prevRound[j])

    # return the last 4 words (representing the key) in reverse word order
    return reverseWordListOrder(reverseExpandedKey[-16:])

# Key guessing function
# encrypredDeltaSets - list of delta sets encrypted by the key to be guessed
def crack(encryptedDeltaSets):
    lastRoundKey= []

    # guess each key byte separately
    for position in range(16):
        lastRoundKey.append(getFinalGuess(position, encryptedDeltaSets))
    
    # return original key
    return invertKeySchedule(lastRoundKey)

if __name__ == "__main__":
    # test key randomly generated
    keyToGuess = [random.randint(0x00, 0xFF) for _ in range(16)]

    # four delta sets used to crack the key
    deltaSets = [generateDeltaSet(0x00), generateDeltaSet(0x12), generateDeltaSet(0x34), generateDeltaSet(0xFF)]
    # encrypted delta sets (by the test key) used for cracking
    encryptedDeltaSets = map(lambda ds: encryptDeltaSet(ds, keyToGuess), deltaSets)

    guessedKey = crack(encryptedDeltaSets)

    print("Key to guess:", keyToGuess)
    print("Guessed key:", guessedKey)
