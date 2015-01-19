import serial
import readline
import signal
import sys
import curses
import math
import time
import logging

pathToUsb = ''
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print 'python %s "/dev/tty.usbmodem123"' % (sys.argv[0])
        sys.exit(1)
    pathToUsb = sys.argv[1]
else:
    pathToUsb = "/dev/tty.usbmodem1411"

ser=serial.Serial(pathToUsb, 9600, timeout=None)
time.sleep(1)

def distance(p1, p2):
    x = abs(p1[0] - p2[0])
    y = abs(p1[1] - p2[1])
    return math.sqrt(x*x + y*y)

def findPointForDist(points, dist):
    if len(points) == 0: return ([],points[1:])

    p0 = points[0]
    i = 1
    while i < len(points):
        if distance(p0, points[i]) >= dist:
            return ([p0,points[i]], points[i+1:])
        i += 1

    return ([p0], points[1:])

def smooth(points):
    MIN_DIST = 13
    result = []
    while len(points) > 0:
        p,points = findPointForDist(points, MIN_DIST)
        result.extend(p)
    return result

def drawPoints(points):
    points = smooth(points)
    for i in range(len(points)-1):
        p1 = points[i]
        p2 = points[i+1]
        h = p2[0] - p1[0]
        v = p2[1] - p1[1]
        hCmd = CMD_LEFT if h < 0 else CMD_RIGHT
        vCmd = CMD_UP if v < 0 else CMD_DOWN
        # cmdVector(hCmd, abs(h)/2, vCmd, abs(v)/2)
        cmdVector(hCmd, abs(h)*.75, vCmd, abs(v)*.75)

def handleInt(a,b):
    ser.close()
    print "\nclosed serial port\n"
    sys.exit(0)
signal.signal(signal.SIGINT, handleInt)

def work(direction, steps):
    for i in range(steps):
        ser.write(direction)

def cmd(cName, i):
    ser.write(cName)
    ser.write(i)

CMD_RIGHT=0
CMD_LEFT=1
CMD_UP=2
CMD_DOWN=3
DIR_TO_INDEX = ['r','l','u','d']
def cmdBytePair(a,b):
    ser.write(wireInt(a))
    ser.write(wireInt(b))
    
def wireInt(i):
    return chr(int(i))

def isHorDir(d):
    return d == CMD_RIGHT or d == CMD_LEFT

def isVerDir(d):
    return d == CMD_UP or d == CMD_DOWN

def _overFlowPair(s):
    overflow = int(s) / 255
    rest = int(s) % 255;
    return (chr(overflow), chr(rest))

def _dumbCmdVector(d1,s1,d2,s2):
    ser.write("v")

    ser.write(wireInt(d1))
    overflow1, rest1 = _overFlowPair(s1)
    ser.write(overflow1)
    ser.write(rest1)

    ser.write(wireInt(d2))
    overflow2, rest2 = _overFlowPair(s2)
    ser.write(overflow2)
    ser.write(rest2)
    
    while True:
        x = ser.read()
        if x == 'x':
            break
        time.sleep(.03)

PREV_HOR_DIR = CMD_RIGHT
PREV_VER_DIR = CMD_DOWN
def cmdVector(d1,s1,d2,s2):
    """ Tracks the previous direction of the motor. If the direction has changed then it
        will drive it 10 points extra to compensate for tension in the Etch-a-Sketch.
    """
    global PREV_HOR_DIR
    global PREV_VER_DIR
    dirs = sorted( [[d1,s1], [d2,s2]] )
    horizontal = dirs[0]
    vertical = dirs[1]

    if horizontal[0] != PREV_HOR_DIR and horizontal[1] > 0:
        horizontal[1] += 10
        PREV_HOR_DIR = horizontal[0]

    if vertical[0] != PREV_VER_DIR and vertical[1] > 0:
        vertical[1] += 10
        PREV_VER_DIR = vertical[0]

    _dumbCmdVector(horizontal[0], horizontal[1], vertical[0], vertical[1])

def cmdRight(d):
    cmdVector(CMD_RIGHT, d, CMD_DOWN, 0)

def cmdLeft(d):
    cmdVector(CMD_LEFT, d, CMD_DOWN, 0)

def cmdUp(d):
    cmdVector(CMD_RIGHT, 0, CMD_UP, d)

def cmdDown(d):
    cmdVector(CMD_LEFT, 0, CMD_DOWN, d)

def cmdStop():
    ser.write('s')

if __name__ == "__main__":
    while True:
        data = raw_input("> ")
        result = data.split(" ")
        if data == "help":
            printHelp()
        elif data == "vtest":
            points = []
            for offset in range(50):
                for i in range(0,361,1):
                    x = math.cos(math.radians(i)) * (100 - offset)
                    y = math.sin(math.radians(i)) * (100 - offset)
                    points.append((x,y))
            drawPoints(points)
        elif len(result) == 2:
            direction = result[0]
            steps = result[1]
            if len(direction) == 1 and direction in ['d','u','l','r','q','x'] and steps.isdigit():
                if direction in ["q", "x"]: # commands
                    cmd(direction, wireInt(steps))
                else: # directions
                    if direction in DIR_TO_INDEX:
                        idx = DIR_TO_INDEX.index(direction)
                        cmdVector(idx, int(steps), (idx+2)%len(DIR_TO_INDEX), 0)
        elif len(result) == 1:
            good = True
            for c in result[0]:
                if c not in ['d','u','l','r','s']:
                    good = False
            if good:
                ser.write(result[0])
        else:
            print "invalid input"
