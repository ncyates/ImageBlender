# ImageBlender
This is a collection of python modules that can be run on sets of images to blend them and create an interesting abstract final result.
I was inspired to code this by seeing [Photographs of Films](http://www.jasonshulmanstudio.com/photographs-of-films/) by Jason Shulman - a collection of images made from taking long-exposure photos of films - and after a doing a project learning OpenCV.
I imagined I could generate similar results programmatically, so I wrote the code to grab frames from a video (framegrabber.py) and to blend the grabbed frames into one image (imageblender.py).
While coding this project, I asked a friend with a large collection of images that document his everyday life for access to his source material so I could experiment with different datasets than just sequential video frames. 
Some of the modules contained in this repository are a result of the challenges faced in processing that data: clearExif.py which strips the EXIF data from the images to ensure proper image orientation
and compare-filter.py which compares the images in a set to eliminate images that are too-similar (works on the assumption that similar images are consecutive)
The results from the blending are usually fairly lackluster and gray until an auto white balance operation is performed on them (I use GIMP for this, and am currently looking for ways to automate this into the processing of the final result.)

### Here are some examples of the generated images:
Link to the first video I used as source material: ![My one-second-a-day video project from 2013](https://vimeo.com/87742679)

#### The resulting image from blending all frames grabbed (after white balancing):
![The resulting image after white balance ](https://github.com/ncyates/ImageBlender/blob/master/samples/year2013wb.jpg)

#### The pre-white-balanced image:
![The pre-white-balanced image](https://github.com/ncyates/ImageBlender/blob/master/samples/year2013.jpg)

#### ImageBlend from my wedding day:
![Photos from my wedding day](https://github.com/ncyates/ImageBlender/blob/master/samples/weddingDay.jpg)

**framegrabber.py** will grab frames from a video and write them to a directory.

**compare-filter.py** will take a directory of images and exclude those that are too similar to one another.

**imageblender.py** will blend the images into a final result.

**smallblend** is a version of the process in imageblender, but for small sets of images that don't need multiprocessing optimization.

**createVid.py** will create a short video sequence from a directory of images.