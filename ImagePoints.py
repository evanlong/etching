from PIL import Image
import math
from control import cmdRight, cmdLeft, cmdUp, cmdDown

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

def drawSolid(image):
    """ returns a list parameters that can be passed as params to cmdVector
    """
    pass

### end solid drawing

### begin draw low res bitmap

def drawBlock(size):
    for x in range(size):
        cmdDown(size)
        cmdUp(size)
        cmdRight(1)

def drawLowRes(image, pixelSize=15):
    """ Given a bitmap treat each pixel as a pixelSize x pixelSize unit on the etch-a-sketch
    """
    pixels = image.load()
    width, height = image.size
    for y in range(height):
        for x in range(width):
            if isBlack(pixels[x,y]):
                drawBlock(pixelSize)
            else:
                cmdRight(pixelSize)
        cmdLeft(width * pixelSize)

### end draw low res bitmap

def main():
    pass
    # image = Image.open("solid_test_bw.png")
    # points = gatherBlackPoints(image)
    # orderedPoints = orderPoints(points)

    # print points
    # print "====="
    # print orderedPoints

    # image = Image.open("a.png")
    # points = gatherBlackPoints(image)
    # outImage = Image.new("RGBA", image.size)
    # pixels = outImage.load()
    # for p in points:
    #     pixels[p[0],p[1]] = (0,0,0)
    # outImage.save("b.png")

if __name__ == "__main__":
    main()
