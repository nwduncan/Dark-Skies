from PIL import Image, ImageDraw
from os import getcwd
from os.path import join

cwd = getcwd()

filename = join(cwd, 'images', 'test.png')
image = Image.new('RGBA', (900, 20), (128,128,128,128))
draw = ImageDraw.Draw(image)
draw.rectangle((0, 0, 300, 20), (255, 0, 0, 128))
draw.rectangle((490, 0, 900, 20), (0, 0, 255, 128))
image.save(filename)
