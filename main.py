# TODO: Make program stop completely after finishing password cracking
# TODO: Once thread stops execution, make it start on new length to prevent thread downtime
# TODO: Look at https://docs.python.org/3/library/multiprocessing.shared_memory.html
# TODO: Prevent user from using more cores than is possible
# TODO: Implement throttling

import sys
import time  # Getting the run time of threads
import multiprocessing  # Multitask password cracking
from multiprocessing import Queue


# Defining needed variables
max_size = 7  # Sets maximum size the cracker will go to before quitting
worker_threads = 2  # Number of threads/cores working at the same time. Increasing this increases cpu usage
length = 2  # Initial password length to check (Default: 2 characters)
current_processes = []  # Array full of Processes
thread_queue = Queue()
password = "jbee"  # Password to check against
run = True  # Main loop variable
data_pipe = Queue()

chars = \
    [  # List of characters used in combinations. Decreasing the size of this will catch fewer passwords, but run faster
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
    ')', '!', '@', '#', '$', '%', '^', '&', '*', '('
    ]


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
    def __init__(self, id=-1, length=0):
        self.id = id  # Thread id
        self.length = length
        self.workers = []
        for _ in range(0, length):  # Populates worker list with iterators with a size equal to the length param
            self.workers.append(iterator(_))

        self.run = True  # Main control flag

        self.startTime = 0
        self.endTime = 0

    def start(self, run, data_pipe):  # Main method that loops through and iterates the iterators in the workers list
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
            data_pipe.put([self.id, True])
            sys.exit()
        else:
            print("[Thread " + str(self.id) + "]: Failed length " + str(self.length))
            data_pipe.put([int(self.id), False])
            sys.exit()


class Controller(object):
    def checkThreads(self):
        global worker_threads

        if worker_threads > max_size:  # Makes sure that number of threads does not exceed the max size.
            print("[MAIN]: Number of threads exceeds max size. Setting threads to max...", end="")
            worker_threads = worker_threads - max_size
            print("Done!\n[MAIN]: Thread count now", worker_threads)

    def startAttempts(self):
        global current_processes

        print("[MAIN]: Starting threads...")
        for process in current_processes:  # Begin worker processes
            process.start()
            print("[MAIN]: Started thread")

    def killIdleThreads(self):
        global current_processes

        for x in range(0, data_pipe.qsize()):
            process_code = data_pipe.get()
            if process_code[1]:
                exit()
            else:
                for process in current_processes:
                    if process.name == str(process_code[0]):
                        process.terminate()
                        current_processes.remove(process)

    def mainLoop(self):
        global run, current_processes, length, thread_queue, data_pipe

        print("[MAIN]: Populating thread queue...", end="")
        thread_queue = []
        current_processes = []
        data_pipe = Queue()

        for x in range(length, max_size):
            atmpt = attempt(x, length)
            thread_queue.append(multiprocessing.Process(name=str(x), target=atmpt.start, args=(run, data_pipe), daemon=True))
            length += 1
        print("Done!")

        print("[MAIN]: Queuing initial threads...", end="")
        for x in range(0, worker_threads):
            current_processes.append(thread_queue[0])
            thread_queue.remove(thread_queue[0])
            current_processes[-1].start()
        print("Done!")

        print(f"[MAIN]: Brute forcing password with {worker_threads} cores...")
        while len(current_processes) > 0:
            processes1 = len(current_processes)
            self.killIdleThreads()
            processes2 = len(current_processes)

            if processes1 > processes2:
                for x in range(0, processes1 - processes2):
                    try:
                        print("[MAIN]: Started thread for length " + str(thread_queue[0].name))
                        current_processes.append(thread_queue[0])
                        thread_queue = thread_queue[1:]
                    except IndexError:
                        for process in current_processes:
                            process.join()
                        exit()
                    current_processes[-1].start()

        print(current_processes)
        print(thread_queue)
        exit()


if __name__ == "__main__":
    controller = Controller()
    controller.mainLoop()
