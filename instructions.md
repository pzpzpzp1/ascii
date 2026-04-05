the purpose of this codebase is to convert images into ascii art. but do so in a way that from the start is about assessing the quality of different approaches. the point isn't to write one method, but to try many and evaluate results. 
create a folder of sample images of varying size pngs called test images. these are the ones that will be used for evaluation.
one main evaluate.py script will take no arguments and will run the evaluation on all samples across all methods and put all outputs in the output folder.
.gitignore the output folder. I want the test images to be commited but .pngs and .jpgs to generally be git ignored.

Create a python script in charge of enumerating all valid characters to be used. it can be a list or bounds on codes. Think about a good representation for these. I don't want basic alphanumeric limitations, good ascii art uses things like ;, or sometimes japanese characters. Put docstrings at the top to describe how you arrived at the 'valid' set of characters.

create an AsciiImage class that stores a 2d array of ascii. the class has save(outname :str) function that 'renders' the ascii image as a png saved to outname using PIL Image. 
The class has a from_image(img: Image, scale: float, method, misc_args) function that takes a PIL image, and a scale by which to shrink or grow the image before asciifying it. method enumerates the choice of method.

Onto the method(s). Lets start with a single method but the code shoudl be written to support extending with new methods that may share steps. The first method is to first center-crop the image to an aspect ratio that can be rendered by ascii text in the first place. this should be reused by all methods. next lets try the greedy method. convert image to greyscale, chooose a threshold by percentile, and do pixel-wise IOU metric to find the best character to use. This greedily builds the ascii image. I guess this one method already counts as several since threshold is variable. 

the methods to evaluate should be listed in a yaml file wil misc_args filled in appropriate to each method. so for this first greedy match method for example, the grayscale prctile is specified in yaml and used to build misc_args.

Evaluation: this pipeline should save out a left-to-right concatenated rgb image post center-crop, the greyscale, the thresholded, and the ascii render. Make sure a vertical red bar of 2 pixel width separates each image before concatenation. Output folder should be split by method, in each method, a list of concated pngs should be there.

Make a readme that is very very minimal. it should say how to set up the python .venv, and install needed dependencies. All dependencies should be in the venv. then list the main .py files to run. namely a python incantation example to run a specific method, and a python incantation to run the full evaluation pipeline. 