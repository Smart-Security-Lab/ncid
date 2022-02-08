import subprocess
import sys
import PySimpleGUI as sg
import time
import threading
from random import seed
from random import randint

# Set seed for randomizing ciphers and lines
seed(1)

# Array with all ciphertexts
ciphertextArray = ['amsco',
'autokey',
'baconian',
'bazeries',
'beaufort',
'bifid',
'cadenus',
'checkerboard',
'columnar_transposition',
'condi',
'cmbifid',
'digrafid',
'foursquare',
'fractionated_morse',
'grandpre',
'grille',
'gromark',
'gronsfeld',
'headlines',
'homophonic',
'key_phrase',
'monome_dinome',
'morbit',
'myszkowski',
'nicodemus',
'nihilist_substitution',
'nihilist_transposition',
'numbered_key',
'periodic_gromark',
'phillips',
'phillips_rc',
'plaintext',
'playfair',
'pollux',
'porta',
'portax',
'progressive_key',
'quagmire1',
'quagmire2',
'quagmire3',
'quagmire4',
'ragbaby',
'railfence',
'redefence',
'route_transposition',
'running_key',
'seriated_playfair',
'slidefair',
'swagman',
'tridigital',
'trifid',
'tri_square',
'two_square',
'variant',
'vigenere']

# Class for runCommand thread
# Parameter name and window (to refresh it in the sub-thread)
class commandThread(threading.Thread):
    def __init__(self, name, window):
        threading.Thread.__init__(self)
        self.name = name
        self.window = window

    def run(self):
        runCommand(window=self.window)

# Boolean variables for killing the threads at the end of the program
stop_thread_runCommand = False
stop_thread_loading = False

# Class for loading (gear) thread
# Parameter name and window (to refresh it in the sub-thread)
class loadingThread(threading.Thread):
    def __init__(self, name, window):
        threading.Thread.__init__(self)
        self.name = name
        self.window = window
    
    def run(self):
        while True:
            if stop_thread_loading: # if thread stopped, stop animation of gear
                break
            self.window.Element('-loading-').UpdateAnimation('..\\files\\gear.gif', time_between_frames=50)

def main():
    # Global variables for killing the threads at the end of the program
    global stop_thread_runCommand, stop_thread_loading
    
    # Design of the program
    ncidTheme = {'BACKGROUND': '#ffffff',
                    'TEXT': '#000000',
                    'INPUT': '#000000',
                    'TEXT_INPUT': '#000000',
                    'SCROLL': '#c7e78b',
                    'BUTTON': ('red', '#ffffff'),
                    'PROGRESS': ('#01826B', '#D0D0D0'),
                    'BORDER': 1,
                    'SLIDER_DEPTH': 0,
                    'PROGRESS_DEPTH': 0}

    # Add dictionary to the PySimpleGUI themes
    sg.theme_add_new('ncidTheme', ncidTheme)

    # Switch theme to use the newly added one
    sg.theme('NCID Theme')

    # Setting the font of the program
    font = ("Courier New", 25, "bold")

    # Final layout
    layout = [  [sg.Text(key='-plaintext-', font=font)],
                [sg.Text(key='-key-', font=font)], 
                [sg.Text(key='-ciphertext-', font=font)],                               
                [sg.Image('..\\files\\gear.gif', key='-loading-')],
                [sg.Text(key='-output-', font=font)],   
            ]

    # Create Window with customized layout
    window = sg.Window('NCID', layout, margins=(500, 250), element_justification='c')
    window.Finalize()
    window.Maximize()

    # Variable for starting the program once
    started = False

    # Event loop
    while True:
        # Run the window
        event, values = window.Read(timeout=3)
        if started == False: # if started once, do not start it another time
            event = 'Run'
            started = True
        
        if event in (None, 'Exit'): # check if user want to exit
            stop_thread_runCommand = True # kill all threads
            stop_thread_loading = True
            break

        # Start first thread
        if event == 'Run':
            thread1 = commandThread(1, window)
            thread1.start()               
            

    window.Close()

# This function does the actual "running" of the command
def runCommand(window=None):

    # Initialize thread for loading
    thread2 = loadingThread(2, window)

    # Global variables
    global stop_thread_runCommand, stop_thread_loading

    # Get random cipher (0 - 54) and random line in the cipher (.txt file) (0 - 173)
    randACACipher = randint(0,54)
    f = open('..\\files\\ciphers\\' + ciphertextArray[randACACipher] + '.txt')
    fplain = open('..\\files\\bible_pt.txt')

    randACALine = randint(0,173)
    lines=f.readlines()
    fplines = fplain.readlines()

    # currentCipherText contains current cipher and key
    currentCipherText = lines[randACALine]
    currentCipherText = currentCipherText.split(',', 1)
    currentPlainText = fplines[randACALine]

    # Remove output
    window['-output-'].update("")

    # Set command for new execution of eval.py
    cmd = "python eval.py --model=../data/models/t128_ffnn_final_100.h5 single_line --ciphertext=\"" + currentCipherText[0] + "\""
    
    # Change ciphertext, key and plaintext string in window
    window['-ciphertext-'].update('Ciphertext: ' + currentCipherText[0])
    window['-key-'].update('Key: ' + currentCipherText[1])
    window['-plaintext-'].update('Plaintext: ' + currentPlainText)

    # Variable for starting loading thead again
    stop_thread_loading = False

    # Call subprocess
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    # Update loading gear
    window['-loading-'].update("..\\files\\gear.gif")

    # Start loading thread again
    thread2.start()

    # The following lines are there for sanitizing the output
    # Variable for saving output - gets true when line is at the first cipher probability
    add = False

    # Define the size of the 2-dimensional array (all ciphers with their probability)
    i, j = 56, 2
    outputArray = [[0 for x in range(j)] for y in range(i)] # array for every cipher

    # Loop for adding lines to the outputArray
    i = 0
    for line in p.stdout:        
        line = line.decode(errors='replace' if (sys.version_info) < (3, 5) else 'backslashreplace').rstrip()
        if line[0:5] == "amsco": # only add needed output
            add = True

        if line == "":
            add = False        
        
        if add == True:
            outputArray[i] = line.split() # split current line into cipher and percentage
            outputArray[i][1] = float(outputArray[i][1][:-1]) # remove % from percentage
            i += 1       
        
        window.Refresh() if window else None
    
    # Call function which returns the 5 highest probabilities beginning at the most probably
    final_list = getMaxValues(outputArray)

    # Add " * " to the actual cipher (if applicable)
    final_list_index = 0
    while final_list_index < 5:
        if ciphertextArray[randACACipher] in final_list[0][final_list_index]:
            final_list[0][final_list_index] = "* " + final_list[0][final_list_index]
        final_list_index += 1

    # Define an output string and format it
    outputString = ''
    for i in range(0, 5):
        outputString += final_list[0][i] + " " + str(final_list[1][i]) + "%\n"
    
    # Update window and print outputString
    if stop_thread_runCommand == False:
        window['-output-'].update(outputString)

    # Setting stop variable for stopping loading thread
    stop_thread_loading = True

    # Connect the threads
    thread2.join()

    #Timeout (5 seconds before the next round starts)
    time.sleep(5)
    
    # Call function recursively
    if stop_thread_runCommand == False:
        runCommand(window=window)

# Function to get the 5 highes probabilities
def getMaxValues(outputArray):

    # Define a two dimensional array
    k, m = 5, 2
    final_list = [[0 for x in range(k)] for y in range(m)]

    # Variable for the current maximum value
    maxj = 0

    # Variable for the complete length of the output array (56 ciphers) (null is included)
    outputLen = 56

    # for loop to get the 5 most likely ciphers
    for i in range(0, 5):
        # Variable for the maximum value of the percentage
        max1 = 0

        for j in range(outputLen):
            if outputArray[j][1] > max1: # Check if current output value is larger than the current maximum value 
                max0 = outputArray[j][0] # Variable for the maximum cipher (not a number, only string)
                max1 = outputArray[j][1]
                maxj = j

        # Remove maximum value and find the next one
        del outputArray[maxj]
        outputLen -= 1
        final_list[0][i] = max0
        final_list[1][i] = max1

    return final_list        

main()