#!/usr/bin/env python

from PIL import Image
import math
import sys
import heapq
from collections import deque
import control

cmdRight = None
cmdLeft = None
cmdDown = None
cmdUp = None
cmdStop = None

def setupDeviceProxy(devicePath):
    control.setup(devicePath)

    global cmdRight
    global cmdLeft
    global cmdDown
    global cmdUp
    global cmdStop

    shouldLogToConsole = (devicePath == None)

    def _tmpCmdRight(d):
        if shouldLogToConsole:
            print "R %d" % d
        else:
            control.cmdRight(d)
    def _tmpCmdLeft(d):
        if shouldLogToConsole:
            print "L %d" % d
        else:
            control.cmdLeft(d)
    def _tmpCmdUp(d):
        if shouldLogToConsole:
            print "U %d" % d
        else:
            control.cmdUp(d)
    def _tmpCmdDown(d):
        if shouldLogToConsole:
            print "D %d" % d
        else:
            control.cmdDown(d)
    def _tmpCmdStop():
        if not shouldLogToConsole:
            control.cmdStop()

    cmdRight = _tmpCmdRight
    cmdLeft = _tmpCmdLeft
    cmdUp = _tmpCmdUp
    cmdDown = _tmpCmdDown
    cmdStop = _tmpCmdStop

def distance(p1, p2):
    x = abs(p1[0] - p2[0])
    y = abs(p1[1] - p2[1])
    return math.sqrt(x*x + y*y)

def isBlack(p):
    return p[0] == 0 and p[1] == 0 and p[2] == 0

def gatherBlackPoints(image):
    pixels = image.load()
    width, height = image.size
    result = []
    for x in range(width):
        for y in range(height):
            if isBlack(pixels[x,y]):
                result.append((x,y))
    return result

def closestToGroup(group, points):
    """ returns index of 'g' in group and index of 'p' in points that are closet to each other
    """

    # really doesn't make sense to call this with empty lists
    if len(group) == 0 and len(points) == 0:
        return -1

    gIdx = 0
    pIdx = 0
    for g in range(len(group)):
        for p in range(len(points)):
            if distance(group[gIdx], points[pIdx]) > distance(group[g], points[p]):
                gIdx = g
                pIdx = p

    return (gIdx, pIdx)

def clamp(minval, value, maxval):
    if value < minval:
        return minval
    elif value > maxval:
        return maxval
    else:
        return value

def distForPointsSequence(points):
    accum = 0
    for i in range(len(points)-1):
        accum += distance(points[i], points[i+1])
    return accum

def placePointInGroup(group, gIdx, p):
    """ p needs to be placed in group before or after gIdx 
        it's important to compare with both the previous and next gIdx +- 1 items in the mix
    """
    if len(group) == 0 or len(group) == 1:
        group.append(p)
        return

    # compare [gIdx-1,p,gIdx,gIdx+1] and [gIdx-1,gIdx,p,gIdx+1]
    beforeSubset = group[clamp(0,gIdx-1,gIdx) : gIdx+2]
    afterSubset = list(beforeSubset)

    if gIdx == 0:
        beforeSubset.insert(0, p)
        afterSubset.insert(1, p)
    else:
        beforeSubset.insert(1, p)
        afterSubset.insert(2, p)

    beforeDist = distForPointsSequence(beforeSubset)
    afterDist = distForPointsSequence(afterSubset)

    if beforeDist < afterDist:
        group.insert(gIdx, p)
    else:
        group.insert(gIdx+1, p)

def orderPoints(points):
    if len(points) == 0 or len(points) == 1: return points

    group = [points.pop()]

    while len(points) > 0:
        gIdx,pIdx = closestToGroup(group, points)
        p = points.pop(pIdx)
        placePointInGroup(group, gIdx, p)

    return group

### begin solid drawing

def newNxM(width,height,value=None):
    """ Create a width by height array. Indexable using: result[x][y]
    """
    return [ [value for j in range(height)] for i in range(width) ]

def pointsAroundP(P, width, height):
    """ Return a list of points surround P provided that P is within the bounds of the area
    """
    Px,Py = P
    if not(Px >= 0 and Px < width and Py >= 0 and Py < height):
        return []

    result = [
        (Px-1, Py),
        (Px+1, Py),
        (Px, Py-1),
        (Px, Py+1)
    ]
    result = [p for p in result if p[0] >= 0 and p[0] < width and p[1] >= 0 and p[1] < height]
    return result

def distFromAtoB(A,B):
    Ax,Ay = A
    Bx,By = B
    return abs(Ax-Bx) + abs(Ay-By)

def lineLength(line):
    return distFromAtoB(line.S, line.E)

class Line:
    """ All of these lines run horizontally
    """

    def __init__(self, S, E):
        self.adjacents = [] # sorted by distance to start point (use a heap?) depend on how we insert/visit nodes in bitmap
        self.S = S
        self.E = E

    def __hash__(self):
        return (self.S,self.E)

    def connect(self, line):
        if not self.isConnected(line):
            lineDist = distFromAtoB(self.S, line.S)
            heapq.heappush(self.adjacents, (lineDist, line))
            line.connect(self)

    def isConnected(self, line):
        return line in [L[1] for L in self.adjacents]

    def containsPoint(self, point):
        Px,Py = point
        Sx,Sy = self.S
        Ex,Ey = self.E
        return (Py == Sy and Py == Ey and Px >= Sx and Px <= Ex)

    def points(self):
        Sx,Sy = self.S
        Ex,Ey = self.E
        for x in range(Sx, Ex+1):
            yield (x, Sy)

def pointToLine(lines, point):
    """ given lines in a row and a point determine if the point falls within in range of any line
    """
    for l in lines:
        if l.containsPoint(point):
            return l
    return None

def imageToHorizontalLines(image):
    """
      pointToLine[pointTuple] -> Line
      rowToLines[rowNumber] -> [Line]
    """
    pixels = image.load()
    width, height = image.size

    # the (S,E) pairs of lines that will be drawn on the device
    rowToLines = []
    lines = []
    for y in range(height):
        currentLines = []
        S = None
        E = None
        for x in range(width):
            if S is None: # searching
                if isBlack(pixels[x,y]):
                    searching = False
                    S = (x,y)
                    E = (x,y)
                else:
                    # white pixel is a continue
                    pass
            else: # collecting
                if isBlack(pixels[x,y]):
                    # continue we are looking for the end
                    # update the E to the current known end
                    E = (x,y)
                else:
                    # we hit a white pixel while we were collecting so the previous pixel is the end
                    # place the (S,E) pair in the lines list
                    # move back to a searching state
                    currentLines.append( Line(S,E) )
                    S = None
                    E = None
        if S and E: # last pixel in the row was black and we didn't get a chance to save it off
            currentLines.append( Line(S,E) )

        rowToLines.append(currentLines)
        lines.extend(currentLines)

    # now connect the lines to each other
    for r1 in range(1, len(rowToLines)):
        r0Lines = rowToLines[r1 - 1]
        r1Lines = rowToLines[r1]

        for l1 in r1Lines:
            for Px,Py in l1.points():
                aboveP = (Px,Py-1)
                l2 = pointToLine(r0Lines, aboveP)
                if l2:
                    l1.connect(l2)

    return lines

def drawCmdsFromPath(path):
    """ Assumes a grid based (non-diagonal) path
    """
    cmds = []

    for i in range(len(path)-1):
        P1x,P1y = path[i]
        P2x,P2y = path[i+1]

        cmd = None
        if P1x == P2x:
            cmd = cmdUp if P2y < P1y else cmdDown
        else: # P1y == P2y
            cmd = cmdLeft if P2x < P1x else cmdRight

        if len(cmds) == 0:
            cmds.append( (cmd, 1) )
        else:
            prevCmd = cmds[-1]
            if prevCmd[0] == cmd:
                cmds.pop()
                cmds.append( (cmd, prevCmd[1] + 1) )
            else:
                cmds.append( (cmd, 1) )

    for c,i in cmds:
        c(i)

def pathFromAtoB(image, A, B):
    """ Find a path from A to B that falls within the shaded area
    """
    pixels = image.load()
    width, height = image.size
    Ax,Ay = A
    Bx,By = B
    previous = newNxM(width, height)
    dist = newNxM(width, height, value=float("inf"))
    dist[Ax][Ay] = 0
    previous[Ax][Ay] = A

    # just a little dijkstra from A to B
    queue = []
    heapq.heappush(queue, (0, A))
    while len(queue) > 0:
        item = heapq.heappop(queue)[1]
        if item == B:
            # all done
            break
        else:
            points = pointsAroundP(item, width, height)
            for p in points:
                Px,Py = p

                # stay within the bounds
                if not isBlack(pixels[Px,Py]): continue

                if previous[Px][Py]: # seen this point before see if traveling to p via item is cheaper
                    # A->item->p < A->p?
                    alt = dist[item[0]][item[1]] + 1
                    if alt < dist[Px][Py]:
                        dist[Px][Py] = alt
                        previous[Px][Py] = item
                else: # new points that we should enqueue
                    distAtoP = dist[item[0]][item[1]] + 1
                    previous[Px][Py] = item
                    dist[Px][Py] = distAtoP
                    heapq.heappush(queue, (distAtoP, p) )

    p = B
    result = [B]
    while p != A:
        Px,Py = p
        prev = previous[Px][Py]
        result.append(prev)
        p = prev
    result.reverse()
    return result

def drawSolid(image):
    result = imageToHorizontalLines(image)

    # DFS visiting of adjacent lines
    stack = [result[0]]
    while len(stack) > 0:
        line = stack.pop()

        cmdRight(lineLength(line))
        cmdLeft(lineLength(line))

        # setup the next set of lines to draw
        tmp = []
        while len(line.adjacents) > 0:
            adjacent = heapq.heappop(line.adjacents)[1]
            tmp.append(adjacent)
            # remove line from adjacent so it doesn't get queued up again
            adjacent.adjacents = [x for x in adjacent.adjacents if x[1] != line]
            heapq.heapify(adjacent.adjacents)

        # reverse tmp so that we have the closest one on the top of the stack
        stack.extend(reversed(tmp))

        # position draw for next run through the loop
        if len(stack) > 0:
            last = stack[-1]
            path = pathFromAtoB(image, line.S, last.S)
            drawCmdsFromPath(path)

    cmdStop()

### end solid drawing

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Draws a black and white image on the Etch-a-Sketch')
    parser.add_argument("image", metavar="IMAGE",type=str, help="Path to an image file")
    parser.add_argument("--device", help="Path to Arduino such as /dev/tty.usbmodem1411. If DEVICE is not specified drawing commands will be logged to stdout.", type=str)
    args = parser.parse_args()

    setupDeviceProxy(args.device)

    image = Image.open(args.image)
    drawSolid(image)

if __name__ == "__main__":
    main()
