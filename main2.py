# TODO: Make program stop completely after finishing password cracking
# TODO: Once thread stops execution, make it start on new length to prevent thread downtime
# TODO: Look at https://docs.python.org/3/library/multiprocessing.shared_memory.html
# TODO: Prevent user from using more cores than is possible
# TODO: Implement throttling

import sys
import time  # Getting the run time of threads
import multiprocessing  # Multitask password cracking
from threading import Thread
from multiprocessing import Queue


# Defining needed variables
max_size = 7  # Sets maximum size the cracker will go to before quitting
worker_threads = 2  # Number of threads/cores working at the same time. Increasing this increases cpu usage
length = 2  # Initial password length to check (Default: 2 characters)
length_buffer = 0
attempts = []  # Array full of Processes
thread_queue = Queue()
password = "jbe"  # Password to check against
run = True  # Main loop variable

chars = \
    [  # List of characters used in combinations. Decreasing the size of this will catch fewer passwords, but run faster
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
    ')', '!', '@', '#', '$', '%', '^', '&', '*', '('
    ]


class Checker(Thread):
    def run(self):
        global attempts
        while True:
            for attempt in attempts:
                if not attempt.is_alive():
                    attempts.append(thread_queue.get())
                    attempts.remove(attempt)

                    # print("Thread killed with id: ", attempt.name)
            # time.sleep(0.1)


class iterator(object):  # Iterator object that controls the logic of each character within the attempt
    def __init__(self, id=-1):
        self.i = 0  # Index of chars list that represents the iterator
        self.digit = chars[0]  # The character that the iterator initializes on
        self.id = id  # ID of the iterator

        self.reset = False  # Used to tell if the current character has reset or not

    def nextIteration(self, step=1, workers=None):
        if workers is None:
            workers = []
        global chars

        self.reset = False
        if self.i + step >= len(chars):  # If the character is going to exceed the bounds of the chars list:
            if self.id != 0:  # Make sure the iterator is not the first in workers (Making sure program doesn't try to access index before 0)
                workers[self.id - 1].nextIteration(step, workers)  # Iterates the iterator before the current one
            self.i = 0  # Set char index to 0
            self.reset = True  # Sets the reset flag to True
        else:
            self.i += step  # Adds the step to the character
        self.digit = chars[self.i]  # Sets the digit to the current index


def concatenateDigits(workerlst):  # Concatenates the digits of all workers from a given list of workers
    """ Concatenate all digits across all workers to create the password attempt"""
    out = ""
    for worker in workerlst:
        out += worker.digit
    return out


def getTime(startTime, endTime):  # Generates the time taken from a start and end time
    totalTime = endTime - startTime

    # Converts from seconds into either hours, minutes, or seconds
    if totalTime >= 3600:
        return str(totalTime / 3600.0) + " hours"
    elif totalTime >= 60:
        return str(totalTime / 60.0) + " minutes"
    else:
        return str(totalTime) + " seconds"


class attempt(object):  # Main object that
    def __init__(self, id=-1, length=0, run=True):
        self.id = id  # Thread id
        self.length = length
        self.workers = []
        for _ in range(0, length):  # Populates worker list with iterators with a size equal to the length param
            self.workers.append(iterator(_))

        self.run = run  # Main control flag

        self.startTime = 0
        self.endTime = 0

    def start(self, run):  # Main method that loops through and iterates the iterators in the workers list
        self.startTime = time.time()
        self.run = run
        while concatenateDigits(self.workers) != password and self.run:  # While loop that controls the iterations
            self.workers[-1].nextIteration(step=1, workers=self.workers)  # Iterates last iterator

            if self.workers[0].reset:  # If the first iterator resets
                self.workers[0].reset = False
                if len(self.workers) + 1 <= self.length:
                    self.workers.append(iterator(len(self.workers)))
                else:
                    break

        self.endTime = time.time()

        if concatenateDigits(self.workers) == password and self.run:  # Makes sure that the password has been found
            self.run = False
            print("[Thread " + str(self.id) + "]: Found password \"" + concatenateDigits(self.workers) + "\" in", getTime(self.startTime, self.endTime))
            sys.exit()
        else:
            print("[Thread " + str(self.id) + "]: Failed length " + str(self.length))
            sys.exit()


class Controller(object):
    def checkThreads(self):
        global worker_threads

        if worker_threads > max_size:  # Makes sure that number of threads does not exceed the max size.
            print("[MAIN]: Number of threads exceeds max size. Setting threads to max...", end="")
            worker_threads = worker_threads - max_size
            print("Done!\n[MAIN]: Thread count now", worker_threads)

    def startChecker(self):
        checkThread = Checker()
        checkThread.start()

    def populateAttempts(self):
        global length_buffer, attempts

        for x in range(0, worker_threads):  # Populate workers
            atmpt = attempt(x, length + length_buffer, run)
            print("[MAIN]: Created thread with id: " + str(length + length_buffer))
            attempts.append(multiprocessing.Process(name=str(x), target=atmpt.start, args=(run,), daemon=True))
            length_buffer += 1

        length_buffer -= 1

    def startAttempts(self):
        global attempts

        print("[MAIN]: Starting threads...")
        for process in attempts:  # Begin worker processes
            process.start()
            print("[MAIN]: Started thread")

    def mainLoop(self):
        global run, attempts, length, thread_queue

        print("Populating thread queue...", end="")
        thread_queue = Queue()
        for x in range(0, max_size):
            atmpt = attempt(x, length, run)
            thread_queue.put(multiprocessing.Process(name=str(x), target=atmpt.start, args=(run,), daemon=True))
            length += 1
        print("Done!")

        self.checkThreads()
        self.startChecker()
        self.populateAttempts()
        self.startAttempts()

        print("[MAIN]: Brute forcing password..")


if __name__ == "__main__":
    controller = Controller()
    controller.mainLoop()
