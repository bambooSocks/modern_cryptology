from aes import SI, encrypt

numberOfDeltaSets= 5
defaultKey = [ 0x2b, 0x7e, 0x15, 0x16,
        0x28, 0xae, 0xd2, 0xa6,
        0xab, 0xf7, 0x15, 0x88,
        0x09, 0xcf, 0x4f, 0x3c]

def generateDeltaSet(randomValue=0,chosenIndex=0):
    # Provide randomValue if it is 
    # needed in the non active indexes
    stateTemplate = [randomValue] * 16
    deltaSet = []
    for index in range(256):
        currentState = stateTemplate.copy()
        currentState[chosenIndex] = index
        deltaSet.append(currentState)
    return deltaSet

def encryptDeltaSet(deltaSet,key):
    return [encrypt(state,key) for state in deltaSet]

def reverseGuessPosition(guess,chosenIndex,deltaState):
    return SI[deltaState[chosenIndex]^guess]

def guessKeyValues(guess,chosenIndex,encryptedDeltaSet):
    result= 0
    for eachSet in encryptedDeltaSet:
        result ^= reverseGuessPosition(guess,chosenIndex,eachSet) 
    return result == 0
    
def checkAllGuesses(chosenIndex,encryptedDeltaSet):
    correctGuesses = []
    for guess in range(256):
        if guessKeyValues(guess,chosenIndex,encryptedDeltaSet):
            correctGuesses.append(guess)
    return correctGuesses

def getFinalGuess(chosenIndex,encryptedDeltaSets):
    correctGuesses = checkAllGuesses(chosenIndex, encryptedDeltaSets[0])
    for idx in range(1,len(encryptedDeltaSets)):
        if len(correctGuesses)==1:
            return correctGuesses[0]
        cg = checkAllGuesses(chosenIndex,encryptedDeltaSets[idx])
        correctGuesses=[value for value in cg if value in correctGuesses]
    raise Exception("couldn't find final guess")

def determineLastRoundKey(encryptedDeltaSets):
    lastRoundKey= []
    for position in range(16):
        lastRoundKey.append(getFinalGuess(position,encryptedDeltaSets))
    return lastRoundKey

def invertKeySchedule():
    return "Done"

def crack(key=defaultKey):
    encryptedDeltaSets=[]
    for index in range(numberOfDeltaSets):
        encryptedDeltaSets.append(encrypt(generateDeltaSet,key))
    lastRoundKey = determineLastRoundKey(encryptedDeltaSets)
    return invertKeySchedule()
