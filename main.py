# Image manipulation
#
# You'll need Python 3 and must install these packages:
#
#   numpy, PyOpenGL, Pillow
#
# First, set up a virtual environment in a 'venv' directory:
#
#   python3 -m venv venv
#
# Then use pip to install numpy and, if necessary, Pillow.
#
# On Linux, install the python3-opengl package to get PyOpenGL.  On
# other systems, try using pip.
#
# Note that file loading and saving (with 'l' and 's') are not
# available if 'haveTK' below is False.  If you manage to install
# python-tk, you can set that to True.  Otherwise, you'll have to
# provide the filename in 'imgFilename' below.
#
# Note that images, when loaded, are converted to the YCbCr
# colourspace, and that you should manipulate only the Y component 
# of each pixel when doing intensity changes.


import sys, os, numpy, math, time

try: # Pillow
    from PIL import Image
except:
    print( 'Error: Pillow has not been installed.' )
    sys.exit(0)

try: # PyOpenGL
    from OpenGL.GLUT import *
    from OpenGL.GL import *
    from OpenGL.GLU import *
except:
    print( 'Error: PyOpenGL has not been installed.' )
    sys.exit(0)



haveTK = False # sys.platform != 'darwin'


# Globals

windowWidth  = 600 # window dimensions
windowHeight = 800

localHistoRadius = 5  # distance within which to apply local histogram equalization



# Current image

imgDir      = 'images'
imgFilename = 'mandrill.png'

currentImage = Image.open( os.path.join( imgDir, imgFilename ) ).convert( 'YCbCr' ).transpose( Image.FLIP_TOP_BOTTOM )
tempImage    = None



# File dialog (doesn't work on Mac OSX)

if haveTK:
    import Tkinter, tkFileDialog
    root = Tkinter.Tk()
    root.withdraw()



# Apply brightness and contrast to tempImage and store in
# currentImage.  The brightness and constrast changes are always made
# on tempImage, which stores the image when the left mouse button was
# first pressed, and are stored in currentImage, so that the user can
# see the changes immediately.  As long as left mouse button is held
# down, tempImage will not change.
#
# A 'brightness' of 0 does not change the image.  A 'contrast' of 1
# does not change the image.  Contrast changes do not have any effect
# on the mid-brightness pixels (i.e. those with brightness 128 in a
# [0,255] brightness scale).

def applyBrightnessAndContrast( brightness, contrast ):

    print( 'adjust brightness = %f, contrast = %f' % (brightness,contrast) )

    width  = currentImage.size[0]
    height = currentImage.size[1]

    srcPixels = tempImage.load()
    dstPixels = currentImage.load()

    # YOUR CODE HERE

    #itterate through all pixels 
    for i in range(0,width):
        for k in range(0,height):

            #get pixel values
            [y,Cr,Cb] = srcPixels[i,k]

            #apply brightness and contrast to luma component
            y = int(round(contrast*y+brightness))

            #place new pixel value into destination pixels
            dstPixels[i,k] = tuple([y,Cr,Cb])
    print("brightness and contrast changes applied.\n")


    

# Perform local histogram equalization on the current image using the
# given radius.
  


def performHistoEqualization( radius ):

    print( 'starting local histogram equalization with radius %d' % radius )

    global currentImage

    pixels = currentImage.load()
    width  = currentImage.size[0]
    height = currentImage.size[1]

    # YOUR CODE HERE
    #make temp copy of pixels so all changes are applied at once
    temp_pixels = currentImage.copy().load()

    for i in range(0,width):
        for k in range(0,height):
            #get bounds of neighborhood and bound check
            xstart = i-radius
            if xstart < 0:
                xstart=0

            ystart = k-radius
            if ystart < 0:
                ystart=0
        
            xend = i+radius
            if xend >= width:
                xend = width-1
            
            yend = k+radius
            if yend >= height:
                yend = height-1
            
            #initialize array of luma values
            lumaArray=[0]*(((radius*2+1)**2))
            count=0

            #fill luma array with luma values from all neighboring pixels
            #need to add 1 to end vals as center pixel not included in range
            for x in range(xstart,xend+1):
                for y in range(ystart,yend+1):
                    luma= pixels[x,y][0]
                    
                    lumaArray[count]=luma
                    count=count+1
            
            #obtain sum of luma array then take average of local luma values using sum amd count
            sum=0
            for y in lumaArray:
                sum=sum+y
            equalizedPixelVal=sum/count
            #place equalized pixel into copy of pixels
            [y,Cr,Cb] = pixels[i,k]
            y = int(round(equalizedPixelVal))
            temp_pixels[i,k] = tuple([y,Cr,Cb])

    for x in range(0,width):
        for y in range(0,height):
            #copy equalized image to original image
            pixels[x,y]=temp_pixels[x,y]
    
    print( 'done local histogram' )



# Scale the tempImage by the given factor about the point
# (centreX,centreY) and store it in currentImage.  Use backward
# projection.  This is called when the mouse is moved with the right
# button held down.  Your code should NOT assume that (centreX,centreY)
# is the image centre.

def scaleImage( factor, centreX, centreY ):

    print( 'scale image by %f about (%d,%d)' % (factor,centreX,centreY) )

    width  = currentImage.size[0]
    height = currentImage.size[1]

    srcPixels = tempImage.load()
    dstPixels = currentImage.load()

    # YOUR CODE HERE
    #calculate new width by dividing original image width by scale factor
    NewWidth=width/factor
    newHeight=height/factor
    #get new x and y ranges based on calculated new scaled width and height
    xStart=centreX-int(round(NewWidth/2))
    if xStart < 0:
        xStart=0
    
    xEnd=centreX+int(round(NewWidth/2))
    if xEnd >= width:
        xEnd=width-1
    
    yStart=centreY-int(round(newHeight/2))
    if yStart < 0:
        yStart=0

    yEnd=centreY+int(round(newHeight/2))
    if yEnd >= height:
        yEnd=height-1
    
    #load currentImage as Image object and crop to new boundaries calculated above
    temp=currentImage.crop((xStart,yStart,xEnd,yEnd))
    #resize image such that it matches original height and width
    temp=temp.resize((width,height),Image.LANCZOS)
    #load image into srcPixels
    srcPixels=temp.load()

    #load src pixels into destination pixels
    for x in range(0,width):
        for y in range(0,height):
            dstPixels[x,y]=srcPixels[x,y]



    

# Set up the display and draw the current image

def display():

    # Clear window

    glClearColor ( 1, 1, 1, 0 )
    glClear( GL_COLOR_BUFFER_BIT )

    # rebuild the image

    img = currentImage.convert( 'RGB' )

    width  = img.size[0]
    height = img.size[1]

    # Find where to position lower-left corner of image

    baseX = (windowWidth-width)/2
    baseY = (windowHeight-height)/2

    glWindowPos2i( int(baseX), int(baseY) )

    # Get pixels and draw

    imageData = numpy.array( list( img.getdata() ), numpy.uint8 )

    glDrawPixels( width, height, GL_RGB, GL_UNSIGNED_BYTE, imageData )

    glutSwapBuffers()


    
# Handle keyboard input

def keyboard( key, x, y ):

    global localHistoRadius

    if key == b'\033': # ESC = exit
        glutLeaveMainLoop()

    elif key == b'l':
        if haveTK:
            path = tkFileDialog.askopenfilename( initialdir = imgDir )
            if path:
                loadImage( path )
        else:
            print( 'Package tk was not loaded, so images cannot be loaded or saved.' )

    elif key == b's':
        if haveTK:
            outputPath = tkFileDialog.asksaveasfilename( initialdir = '.' )
            if outputPath:
                saveImage( outputPath )
        else:
            print( 'Package tk was not loaded, so images cannot be loaded or saved.' )

    elif key == b'h':
        performHistoEqualization( localHistoRadius )

    elif key in [b'+',b'=']:
        localHistoRadius = localHistoRadius + 1
        print( 'radius =', localHistoRadius )

    elif key in [b'-',b'_']:
        localHistoRadius = localHistoRadius - 1
        if localHistoRadius < 1:
            localHistoRadius = 1
        print( 'radius =', localHistoRadius )

    elif key == b'?':

        print( '' )
        print( 'Controls:' )
        print( '' )
        print( '  ESC - exit' )
        print( '   l  - load image' )
        print( '   s  - save image' )
        print( '   h  - perform histogram equalization' )
        print( '   +  - increase local histogram radius' )
        print( '   -  - decrease local histogram radius' )
        print( '' )
        print( '  left mouse up/down    - adjust contrast' )
        print( '  left mouse left/right - adjust brightness' )
        print( '  right mouse up/down   - scale' )
        print( '' )
        

    else:
        print( 'key =', key )        # DO NOT REMOVE THIS LINE.  It might be used for automated marking.

    glutPostRedisplay()



# Load and save images.
#
# Modify these to load to the current image and to save the current image.
#
# DO NOT CHANGE THE NAMES OR ARGUMENT LISTS OF THESE FUNCTIONS, as
# they will be used in automated marking.


def loadImage( path ):

    global currentImage

    currentImage = Image.open( path ).convert( 'YCbCr' ).transpose( Image.FLIP_TOP_BOTTOM )


    
def saveImage( path ):

    global currentImage

    currentImage.transpose( Image.FLIP_TOP_BOTTOM ).convert('RGB').save( path )
    


# Handle window reshape


def reshape( newWidth, newHeight ):

    global windowWidth, windowHeight

    windowWidth    = newWidth
    windowHeight = newHeight

    glutPostRedisplay()



# Maintain our own event queue so that we can explicitly coalesce
# multiple adjacent mouse movement events into a single movement
# event.  If this is not done, the image transformation code will be
# called with each movement event.  Since the transformations take a
# long time, this will back up a long queue of movement events and
# make the UI unusable.
#
# Coalescing of movement events is normally done by GLUT, but GLUT's
# Python implementation seems not to do so.
#
# The event queue is processed by the idle() function during idle times.


class Event:
    def __init__( self, type, button, state, x, y ):
      self.type   = type
      self.button = button
      self.state  = state
      self.x      = x
      self.y      = y

eventQueue = []


# Mouse click/release: just store the event

def mouse( btn, state, x, y ):

    global eventQueue

    eventQueue.append( Event( 'click', btn, state, x, y ) )
    

# Mouse motion: just store the event

def motion( x, y ):

    global eventQueue

    eventQueue.append( Event( 'motion', None, None, x, y ) )


# Mouse state on initial click

button = None
initX = 0
initY = 0


# Idle state: process event queue

def idle():

    global eventQueue, button, initX, initY, tempImage

    # Sleep if no events are in the queue

    if eventQueue == []:
        time.sleep( 0.01 ) # one centisecond
        return

    # Skip over all but the last of a sequence of adjacent motion events
    #
    # (Comment this out and try to adjust the brightness to see what
    # it's like without our own event queue.)
    
    while len(eventQueue) > 1 and eventQueue[0].type == 'motion' and eventQueue[1].type == 'motion':
        eventQueue = eventQueue[1:]

    # Process next event

    event = eventQueue[0]
    eventQueue = eventQueue[1:]

    if event.type == 'click':

      if event.state == GLUT_DOWN:
          tempImage = currentImage.copy()
          button = event.button
          initX = event.x
          initY = event.y
      elif event.state == GLUT_UP:
          tempImage = None
          button = None

      glutPostRedisplay()

    elif event.type == 'motion':

      if button == GLUT_LEFT_BUTTON:  # note global 'button', not 'event.button', as this is the
                                      # button pressed at the *previous* click event
          diffX = event.x - initX
          diffY = event.y - initY

          applyBrightnessAndContrast( 255 * diffX/float(windowWidth), 1 + diffY/float(windowHeight) )

      elif button == GLUT_RIGHT_BUTTON:

          initPosX = initX - float(windowWidth)/2.0
          initPosY = initY - float(windowHeight)/2.0
          initDist = math.sqrt( initPosX*initPosX + initPosY*initPosY )
          if initDist == 0:
              initDist = 1

          newPosX = event.x - float(windowWidth)/2.0
          newPosY = event.y - float(windowHeight)/2.0
          newDist = math.sqrt( newPosX*newPosX + newPosY*newPosY )

          # Scale about the image centre.  But 'scaleImage' should be
          # implemented to scale about any point ... not only the
          # image centre.
          
          scaleImage( newDist / initDist, currentImage.size[0]/2, currentImage.size[1]/2 )

      glutPostRedisplay()

  

# Run OpenGL

glutInit()
glutInitDisplayMode( GLUT_DOUBLE | GLUT_RGB )
glutInitWindowSize( windowWidth, windowHeight )
glutInitWindowPosition( 50, 50 )

glutCreateWindow( 'imaging' )

glutDisplayFunc( display )
glutKeyboardFunc( keyboard )
glutReshapeFunc( reshape )
glutMouseFunc( mouse )
glutMotionFunc( motion )
glutIdleFunc( idle )

glutMainLoop()
