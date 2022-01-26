# TODO: Implement throttling

import time  # Getting the run time of threads
import multiprocessing  # Multitask password cracking
from multiprocessing import Queue


# Defining needed variables
password = "jbeee"  # Password to check against
max_size = 7  # Sets maximum size the cracker will go to before quitting
worker_threads = 3  # Number of threads/cores working at the same time. Increasing this increases cpu usage
length = 3  # Initial password length to check (Default: 2 characters)
current_processes = []  # Array full of Processes
thread_queue = []  # Queue containing all threads in a queue
data_pipe = Queue()  # Data pipe

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

    def start(self, data_pipe):  # Main method that loops through and iterates the iterators in the workers list
        self.startTime = time.time()

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
            data_pipe.put([self.id, True])  # Puts the attempt id and True(indicates the password was found)
            exit()
        else:
            print("[Thread " + str(self.id) + "]: Failed length " + str(self.length))
            data_pipe.put([int(self.id), False])  # Puts the attempt id and False(indicates the password WASN'T found)
            exit()


class Controller(object):  # Controller object that contains the method necessary to run the main loop
    def checkThreads(self):  # Makes sure that the number of workers in not greater than the maximum password length
        global worker_threads

        if worker_threads > max_size:  # Makes sure that number of threads does not exceed the max size.
            print("[MAIN]: Number of threads exceeds max size. Setting threads to max...", end="")
            worker_threads = worker_threads - max_size  # Configures the number workers to reasonable number
            print("Done!\n[MAIN]: Thread count now", worker_threads)

    def killIdleThreads(self):  # Kills all idle threads that have finished
        global current_processes

        try:
            for x in range(0, data_pipe.qsize()):  # Cannot iterate through the values of a multiprocess.Queue(), so a range is used
                process_code = data_pipe.get()  # Gets the data from each attempt's finish
                if process_code[1]:  # If the password was found
                    print("[MAIN]: Exiting...")
                    exit()
                else:
                    for process in current_processes:
                        if process.name == str(process_code[0]):  # Finds the process who's id matches the process that is idle
                            process.terminate()
                            current_processes.remove(process)

        except KeyboardInterrupt:  # Adds a "safety net" that prevents a big error message if the user forcefully exits
            print("[Main]: Exiting...")
            exit()

    def mainLoop(self):
        global run, current_processes, length, thread_queue, data_pipe

        if multiprocessing.cpu_count() > worker_threads:  # Makes sure user doesn't set core count higher than what is possible
            print("[MAIN]: Maximum core count exceeded. Exiting...")
            exit()

        print("[MAIN]: Populating thread queue...", end="")
        thread_queue = []  # Queue for upcoming processes
        current_processes = []  # Contains all processes
        data_pipe = Queue()  # One way pipe that feeds data from the attempt objects to the main loop

        for x in range(length, max_size):
            atmpt = attempt(x, length)
            thread_queue.append(multiprocessing.Process(name=str(x), target=atmpt.start, args=(data_pipe,), daemon=True))
            length += 1
        print("Done!")

        print("[MAIN]: Queuing initial threads...", end="")
        for x in range(0, worker_threads):  # Puts first processes in current_processes and starts them
            current_processes.append(thread_queue[0])
            thread_queue.remove(thread_queue[0])
            current_processes[-1].start()
        print("Done!")

        print(f"[MAIN]: Brute forcing password with {worker_threads} cores...")
        while len(current_processes) > 0:  # Main loop that continuously starts processes if a process dies
            processes1 = len(current_processes)
            self.killIdleThreads()
            processes2 = len(current_processes)

            if processes1 > processes2:  # If the number of processes changed after killing idle threads
                for x in range(0, processes1 - processes2):
                    try:
                        print("[MAIN]: Started thread for length " + str(thread_queue[0].name))
                        current_processes.append(thread_queue[0])  # Add beginning of thread_queue to current processes
                        thread_queue = thread_queue[1:]  # Remove first thread from thread_queue
                        current_processes[-1].start()  # Starts the new thread
                    except IndexError:
                        for process in current_processes:  # For catching when the queue's run out of threads
                            process.join()  # Waits for all threads to finish, then stops
                        print("[MAIN]: Exiting...")
                        exit()

        print("[MAIN]: Exiting...")
        exit()


if __name__ == "__main__":
    controller = Controller()
    controller.mainLoop()  # Starts the main loop for the cracking process to begin
