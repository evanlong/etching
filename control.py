import serial
import readline
import signal
import sys
import curses
import math
import time

ser=serial.Serial("/dev/tty.usbmodem411", 9600, timeout=None)

def drawPoints(points):
    result = []
    for i in range(len(points)-1):
        p1 = points[i]
        p2 = points[i+1]
        h = p2[0] - p1[0]
        v = p2[1] - p1[1]
        hCmd = CMD_LEFT if h < 0 else CMD_RIGHT
        vCmd = CMD_UP if v < 0 else CMD_DOWN
        cmdVector(hCmd, abs(h)/2, vCmd, abs(v)/2)

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

def cmdVector(d1,s1,d2,s2):
    ser.write("v")
    ser.write(wireInt(d1))
    ser.write(wireInt(s1))
    ser.write(wireInt(d2))
    ser.write(wireInt(s2))
    while True:
        x = ser.read()
        if x == 'x':
            break
        time.sleep(.03)

def cursesSetup():
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(1)
    while 1:
        c = stdscr.getch()
        if c == ord('q'):
            break
        elif c == curses.KEY_LEFT:
            work("l", 1)
        elif c == curses.KEY_RIGHT:
            work("r", 1)
        elif c == curses.KEY_UP:
            work("u", 1)
        elif c == curses.KEY_DOWN:
            work("d", 1)
    curses.nocbreak()
    stdscr.keypad(0)
    curses.echo()
    curses.endwin()

if __name__ == "__main__":
    while True:
        data = raw_input("d,c> ")
        result = data.split(" ")
        if data == "screen":
            cursesSetup()
            continue
        elif data == "circle":
            for i in range(180):
                cmdBytePair(CMD_RIGHT, 200)
                vertical = math.sin(math.radians(i))
                if vertical < 0:
                    vertical = abs(vertical)
                    cmdBytePair(CMD_DOWN, vertical)
                else:
                    cmdBytePair(CMD_UP, vertical)
            continue
        elif data == "vtest":
            # while True:
            #     print "begin"
            #     cmdVector(CMD_RIGHT, 60, CMD_UP, 0)
            #     cmdVector(CMD_RIGHT, 0, CMD_DOWN, 60)
            #     cmdVector(CMD_LEFT, 60, CMD_DOWN, 0)
            #     cmdVector(CMD_RIGHT, 0, CMD_UP, 60)
            for i in range(100):
                cmdVector(CMD_RIGHT, 1, CMD_UP, 0)
                cmdVector(CMD_RIGHT, 0, CMD_UP, 60)
                cmdVector(CMD_RIGHT, 1, CMD_UP, 0)
                cmdVector(CMD_RIGHT, 0, CMD_DOWN, 60)
        elif len(result) == 2:
            direction = result[0]
            steps = result[1]
            if len(direction) == 1 and direction in ['d','u','l','r','q','x'] \
                    and steps.isdigit():
                if direction in ["q", "x"]: # commands
                    cmd(direction, wireInt(steps))
                else: # directions
                    if direction in DIR_TO_INDEX:
                        idx = DIR_TO_INDEX.index(direction)
                        cmdVector(idx, int(steps), (idx+2)%len(DIR_TO_INDEX), 0)
                continue
        elif len(result) == 1:
            good = True
            for c in result[0]:
                if c not in ['d','u','l','r','s']:
                    good = False
            if good:
                ser.write(result[0])
                continue
        print "invalid input"
