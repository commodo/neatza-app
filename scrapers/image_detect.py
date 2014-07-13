
import sys
import os
import cv2 # Python OpenCV to be more exact
import tempfile

def detectObjects(img_url, cl_xml):
    """Converts an image to grayscale and prints the locations of any
       faces found"""

    temp = tempfile.NamedTemporaryFile(delete = False)
    d = urllib.urlopen(img_url).read()
    temp.write(d)
    temp.close()

    image = cv2.imread(temp.name)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    os.remove(temp.name)

    cl = cv2.CascadeClassifier( cl_xml )
    objs = cl.detectMultiScale( gray, 1.3, 5 )

    return (objs) 

def has_human(img_url):
    """Returns true if at least one human profile was detected
    """

    # XML taken from https://github.com/Itseez/opencv
    test_profiles = [ 'haarcascade_frontalface_default.xml',
                      'haarcascade_profileface.xml',
                      'haarcascade_upperbody.xml',
                      'haarcascade_fullbody.xml',
                      'haarcascade_mcs_mouth.xml',
                      'haarcascade_mcs_nose.xml',
                    ]

    for t in test_profiles:
        if len( detectObjects( img_url, t ) ) > 0:
            return True

    return False

