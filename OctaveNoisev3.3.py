import numpy
from PIL import Image,ImageDraw
import pygame
#import tkinter

#http://effbot.org/tkinterbook/tkinter-color-dialogs.htm

frame=0
framePause=0#the script runs faster, but this here is to smooth out the frame rate so the transistions seem smoother.
interpolationFrames=30#set to 1 to have no interpolation frames.

#image parameters
usePallet=True
randomPallet=False
palletsize=6
animate=True
IMAGESTYLE=Image.NEAREST #options are Image.NEAREST Image.BILINEAR Image.BICUBIC Image.ANTIALIAS(slow!)
octaves=9#octave level of 9 would match in resolution with 256, but it looks a bit better if we up scale it by a factor of 2. less grainy.

outputSize=(600,600)#this is just the window size. the octave count determines the scale of the output colors.

colorPallet=[(28,93,215),(28,93,215),(174,158,93),(82,83,39),(189,75,24),(255,255,255)]
if(randomPallet):
    colorPallet=[]#clear it out!
    for r in range(0,palletsize):
        colorPallet.append((numpy.random.randint(255),numpy.random.randint(255),numpy.random.randint(255)))#fill it up



size=2**octaves

def cubicImage(images,time):
    numpyImages=[]
    for tuna in images:
        numpyImages.append(numpy.array(tuna,dtype=numpy.float))#make a list of our numpyImages.
    numpyPicture=numpyImages[1]+0.5*time*(numpyImages[2]-numpyImages[0]+time*(2.0*numpyImages[0]-5.0*numpyImages[1]+4.0*numpyImages[2]-numpyImages[3]+time*(3.0*(numpyImages[1]-numpyImages[2])+numpyImages[3]-numpyImages[0])));
    numpyPicture=numpy.array(numpy.round(numpyPicture),dtype=numpy.uint8)#make into int, rather than float.
    return Image.fromarray(numpyPicture,mode="RGB")

def cubicInterp(points,time):
    pixel=[0,0,0]
    for a in range(0,3): #for each channel in the pixel, run the interpolation algorithm, and save it as the resulting pixel.
        pixel[a]=points[1][a]+0.5*time*(points[2][a]-points[0][a]+time*(2.0*points[0][a]-5.0*points[1][a]+4.0*points[2][a]-points[3][a]+time*(3.0*(points[1][a]-points[2][a])+points[3][a]-points[0][a])));
    return (int(pixel[0]),int(pixel[1]),int(pixel[2]))

def linearInterp(points, time):
    pixel=[0,0,0]
    for a in range(0,3): #for each channel in the pixel, run the interpolation algorithm, and save it as the resulting pixel.
        pixel[a]=((1-time)*point[0][a])+(time*point[1][a]);#use a linear interpolation algorithm among the first 2 keyframes
    return (int(pixel[0]),int(pixel[1]),int(pixel[2]))

def makeOctaves(quantity):#use a fromarray function here instead?
    listOfOctaves=[]
    for a in range(0,quantity):#for each of the number of desired octaves
        imarray = numpy.random.rand(2**a,2**a,3) * 255 #create a bunch of random colors, in an array. this is a signifigantly faster method than doing nested for loops.
        noiseImage=Image.fromarray(imarray.astype('uint8')).convert('RGB')#convert that array into an image type.
        listOfOctaves.append(noiseImage.resize((size,size),IMAGESTYLE))#scale up the image to full size, and save it into out list of octaves.
    return listOfOctaves

def makeColorOctaves(quantity,pallet):#Due to the specificity of the color pakllet, there will be a slow down incurred by the picky colors.
    listOfOctaves=[]
    for a in range(0,quantity):#for each of the number of desired octaves
        imarray=numpy.zeros((2**a,2**a,3),numpy.float)
        for y in range(0,2**a):
            for x in range(0,2**a):
                imarray[x][y]=pallet[numpy.random.randint(len(pallet))]#Picks a random color in the list of colors in our color pallet.
        noiseImage=Image.fromarray(imarray.astype('uint8')).convert('RGB')#convert that array into an image type.
        listOfOctaves.append(noiseImage.resize((size,size),IMAGESTYLE))#scale up the image to full size, and save it into out list of octaves.
    return listOfOctaves

def combineOctaves(images): #http://stackoverflow.com/a/17383621
    arr=numpy.zeros((size,size,3),numpy.float)
    for im in images:
        imgArr=numpy.array(im,dtype=numpy.float)
        arr=arr+imgArr/octaves
    arr=numpy.array(numpy.round(arr),dtype=numpy.uint8)#make into int, rather than float.
    return Image.fromarray(arr,mode="RGB")

def makeImage():
    if usePallet:
        return combineOctaves(makeColorOctaves(octaves,colorPallet))
    else:
        return combineOctaves(makeOctaves(octaves))

listOfPictures=[makeImage(),makeImage(),makeImage(),makeImage()]#populate the start list.

def offsetList(targetList):
    targetList.pop(0)#chop off the first item of the list, and add the new image.
    targetList.append(makeImage()) #this is non pythonic.
    return targetList
#main loop

canvas = pygame.Surface(outputSize)
window = pygame.display.set_mode(outputSize)
pygame.display.set_caption("OctaveNoise!")
#populate our list of frames. we need four for the splining algorithm to work.

print "testing"
while animate:
    listOfPictures=offsetList(listOfPictures)
    #print "Keyframe"
    for a in range(0,interpolationFrames):
        canvas = pygame.image.fromstring(cubicImage(listOfPictures,float(a)/float(interpolationFrames)).resize(outputSize,Image.NEAREST).tobytes(),outputSize,"RGB")
        window.blit(canvas,(0,0))#write new pixels to display
        pygame.time.wait(framePause)
        pygame.display.flip() #update display.
        #print "tweenFrame"
    for event in pygame.event.get(): #code for closing the window whent he X button is pressed
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
#if we dont animate, then just generate one image, display it, and endlessly loop, waiting for the window to be closed
canvas = pygame.image.fromstring(makeImage().tostring(),(size,size),"RGB")
window.blit(canvas,(0,0))#write new pixels to display
pygame.display.flip() #update display.
while True:
    for event in pygame.event.get(): #code for closing the window whent he X button is pressed
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
