import serial
import readline
import signal
import sys
import curses

ser=serial.Serial("/dev/tty.usbmodem641", 9600, timeout=1)

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

def wireInt(i):
    return chr(int(i))

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
        elif len(result) == 2:
            direction = result[0]
            steps = result[1]
            if len(direction) == 1 and direction in ['d','u','l','r','q','x'] \
                    and steps.isdigit():
                if direction in ["q", "x"]: # commands
                    cmd(direction, wireInt(steps))
                else: # directions
                    work(direction, int(steps))
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
