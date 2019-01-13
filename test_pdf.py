from PIL import Image
from fpdf import FPDF
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.firefox.options import Options
import math
from stat import S_ISREG, ST_CTIME, ST_MODE
import os, sys, time

# Add this options argument to driver initialization to create a headless browser
options = Options()
options.headless = True

# Initialize the firefox webdriver for selenium
fp = webdriver.FirefoxProfile('C:/Users/Akisame/AppData/Roaming/Mozilla/Firefox/Profiles/qt1b0nuu.default')
driver = webdriver.Firefox(executable_path="C:/Users/Public/drivers/geckodriver.exe",firefox_profile=fp)

# Set the viewport size to UA Panel size (250 x 800)
def set_viewport_size(driver, width, height):
    window_size = driver.execute_script("""return [window.outerWidth - window.innerWidth + arguments[0], window.outerHeight - window.innerHeight + arguments[1]];""", width, height)
    driver.set_window_size(*window_size)

src_dir = 'D:/UA panels/'    # Source directory for the UA Panel html files
target_dir = 'D:/ScreenShots/'      # Destination Directory for storing the viewport screenshots
screenShotCount = 0     # Index for counting screenshots
entries = (os.path.join(src_dir, fn) for fn in os.listdir(src_dir))
entries = ((os.stat(path), path) for path in entries)

# leave only regular files, insert creation date
entries = ((stat[ST_CTIME], path)
           for stat, path in entries if S_ISREG(stat[ST_MODE]))
print(entries)
#NOTE: on Windows `ST_CTIME` is a creation date 
#  but on Unix it could be something else
#NOTE: use `ST_MTIME` to sort by a modification date
countPages = 0
UAPanels = []
for cdate, path in sorted(entries):
    UAPanels.append(os.path.basename(path))
    print(time.ctime(cdate), os.path.basename(path))

for ind,page in enumerate(UAPanels):
    file = os.path.join(src_dir,page)
    if os.path.isdir(page):
        pass
    else:
        driver.get(f"file:///{file}");
        driver.maximize_window()
        set_viewport_size(driver, 263, 808)
        viewportWidthX = 250
        viewportHeightY = 700
        scrMaxY = driver.execute_script('''return window.scrollMaxY''')
        nScreenShots = math.ceil(scrMaxY/viewportHeightY)
        remainder = scrMaxY%viewportHeightY
        for i in range(nScreenShots+1): 
            if i == nScreenShots and remainder != 0:
                scrollPos = (i-1)*viewportHeightY+remainder
            else:
                scrollPos = i*viewportHeightY
            screenShotCount += 1
            driver.execute_script('''return window.scrollTo(0, arguments[0])''',scrollPos)
            driver.save_screenshot(f'{target_dir}screen_shot{screenShotCount}.png')

src_dir = 'D:/ScreenShots/' # Source Directory in which all screenshots are stored
target_dir = 'D:/Collages/' # Target location for storing the created collages ( which are then converted to pdf pages)
listofimages=os.listdir(src_dir) # Create a list for files in the source directory
listofimages = [os.path.join(src_dir, f) for f in listofimages] # add path to each file
listofimages.sort(key=lambda x: os.path.getmtime(x)) # Sort the files not by name but by their modified time

def create_collage(width, height, listofimages):
    cols = 3
    rows = 1
    nIm = 1 # Number of collage images to creates
    nIm = math.ceil(len(listofimages)/cols)
    remainder = len(listofimages)%cols
    for i in range(nIm):
        imagesForThePage = []
        if i == nIm-1 and remainder != 0:
            imagesForThePage = (listofimages[i*cols+n] for n in range(remainder))
            nCols = remainder
        else:
            imagesForThePage = (listofimages[i*cols+n] for n in range(cols))
            nCols = cols
        thumbnail_width = width//cols
        thumbnail_height = height//rows
        # Xpadding = 25
        size = thumbnail_width, thumbnail_height
        new_im = Image.new('RGB', (width, height),"white")
        ims = []
        for p in imagesForThePage:
            im = Image.open(p)
            im.thumbnail(size)
            ims.append(im)
        k = 0
        x = round((thumbnail_width-250)/2)
        y = 0
        for col in range(nCols):
            for row in range(rows):
                new_im.paste(ims[k], (x, y))
                k += 1
                y += thumbnail_height
            x += thumbnail_width
            y = 0
        new_im.save(f"{target_dir}Collage{i}.jpg")
create_collage(850, 800, listofimages)

# FPDF.set_compression(compress,False)
pdf = FPDF('P', 'mm', (210, 210))

collageList = os.listdir(target_dir)
listOfCollages = [os.path.join(target_dir, f) for f in collageList] # add path to each file
listOfCollages.sort(key=lambda x: os.path.getmtime(x)) # Sort the files not by name but by their modified time
for image in listOfCollages:
    pdf.add_page()
    pdf.image(image,15,15,180,180)
pdf.output(f"D:/UAPanels.pdf", "F")
os.system("D:/UAPanels.pdf")