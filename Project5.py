from PIL import Image
import os

# CITE: PIL Docs https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.new
# HELP: Used to create an empty image 4x as large as the original

def highResUpscale(image):
    
    output = brighten(extraSmoothing(lowResUpscale(image)))
    return output

def lowResUpscale(image):
    
    output = overlay(leftoverPixels(smooth(image, 10)), leftoverPixels2(upscale(image),20))
    return output

def extraSmoothing(image):
    
    output = overlay(leftoverPixels(smooth(image, 40)), leftoverPixels2(upscale(image),100))
    return output
    
def upscale(image):
    
    image_out = Image.new('RGB', (image.width*2, image.height*2))
    for x in range(image.width):
        for y in range(image.height):
            (r,g,b) = image.getpixel((x, y))
            image_out.putpixel((x*2, y*2),(r,g,b))
            image_out.putpixel((x*2-1, y*2-1),(r,g,b))
            image_out.putpixel((x*2, y*2-1),(r,g,b))
            image_out.putpixel((x*2-1, y*2),(r,g,b))
    return image_out

def corners(p1,p2,p3,source_image,scale,copied_out,origin):
    
    (r1,g1,b1) = source_image.getpixel(p1)
    (r2,g2,b2) = source_image.getpixel(p2)
    (r3,g3,b3) = source_image.getpixel(p3)
    redavg = (r1+r2+r3)/3
    greenavg = (g1+g2+g3)/3
    blueavg = (b1+b2+b3)/3
    if abs(redavg - source_image.getpixel(p2)[0]) < scale and abs(greenavg - source_image.getpixel(p2)[1]) < scale and abs(blueavg - source_image.getpixel(p2)[2]) < scale:
        copied_out.putpixel(origin,source_image.getpixel(p2))

def smooth(image,scale):
            
    source_image = upscale(image)
    copied_out = upscale(image)
    for x in range(1,image.width-1):
        for y in range(1,image.height-1):
            corners((x*2, y*2+1),(x*2+1, y*2+1),(x*2+1, y*2),source_image,scale,copied_out,(x*2, y*2))
            corners((x*2-1, y*2-2),(x*2-2, y*2-2),(x*2-2, y*2-1),source_image,scale,copied_out,(x*2-1, y*2-1))
            corners((x*2-1, y*2+1),(x*2-2, y*2+1),(x*2-2, y*2),source_image,scale,copied_out,(x*2-1, y*2))
            corners((x*2+1, y*2-1),(x*2+1, y*2-2),(x*2, y*2-2),source_image,scale,copied_out,(x*2, y*2-1))
    return copied_out

def leftoverPixels(image):
    image_out = image.copy()
    for x in range(1,image.width-1):
        for y in range(1,image.height-1):
            if image.getpixel((x+1, y)) == image.getpixel((x, y+1)) != image.getpixel((x+1, y+1)):
                image_out.putpixel((x, y),image.getpixel((x+1, y)))
            elif image.getpixel((x-1, y)) == image.getpixel((x, y-1)) != image.getpixel((x-1, y-1)):
                image_out.putpixel((x, y),image.getpixel((x-1, y)))
            elif image.getpixel((x-1, y)) == image.getpixel((x, y+1)) != image.getpixel((x-1, y+1)):
                image_out.putpixel((x, y),image.getpixel((x-1, y)))
            elif image.getpixel((x+1, y)) == image.getpixel((x, y-1)) != image.getpixel((x+1, y-1)):
                image_out.putpixel((x, y),image.getpixel((x+1, y)))
    return image_out

def putAverageColor(image_in,image_out,p1,p2,p3,scale2,origin):
    
    colors1 = image_in.getpixel(p1)
    colors2 = image_in.getpixel(p2)
    colors3 = image_in.getpixel(p3)
    Ravg = round((colors1[0] + colors2[0])/2)
    Bavg = round((colors1[1] + colors2[1])/2)
    Gavg = round((colors1[2] + colors2[2])/2)
    combinedColor = (Ravg, Bavg, Gavg)
    if abs(colors1[0] - colors2[0]) < scale2 and abs(colors1[1] - colors2[1]) < scale2 and abs(colors1[2] - colors2[2]) < scale2:
        image_out.putpixel(origin,combinedColor)

def leftoverPixels2(image,scale2):
    image_out = image.copy()
    for x in range(1,image.width-1):
        for y in range(1,image.height-1):
            putAverageColor(image,image_out,(x+1, y),(x, y+1),(x+1, y+1),scale2,(x,y))
            putAverageColor(image,image_out,(x-1, y),(x, y-1),(x-1, y-1),scale2,(x,y))
            putAverageColor(image,image_out,(x-1, y),(x, y+1),(x-1, y+1),scale2,(x,y))
            putAverageColor(image,image_out,(x+1, y),(x, y-1),(x+1, y-1),scale2,(x,y))
    return image_out
                
def overlay(image1,image2):
    image_out = image1.copy()
    for x in range(image1.width):
        for y in range(image1.height):
            r = round((image1.getpixel((x, y))[0] + image2.getpixel((x, y))[0])/2)
            g = round((image1.getpixel((x, y))[1] + image2.getpixel((x, y))[1])/2)
            b = round((image1.getpixel((x, y))[2] + image2.getpixel((x, y))[2])/2)
            image_out.putpixel((x, y),(r,g,b))
    return image_out

def brighten(image):
    image_out = image.copy()
    for x in range(image.width):
        for y in range(image.height):
            r = image.getpixel((x, y))[0]
            g = image.getpixel((x, y))[1]
            b = image.getpixel((x, y))[2]
            image_out.putpixel((x, y),(r+4,g+4,b+4))
    return image_out

def createCustomGif(image_paths, output_filename='custom.gif', duration=75):
    """
    Create a GIF from a list of image file paths.
    
    Args:
        image_paths (list): List of file paths to images
        output_filename (str): Name of the output GIF file
        duration (int): Duration for each frame in milliseconds
    
    Returns:
        str: Path to the created GIF file, or None if error
    """
    try:
        images = []
        for image_path in image_paths:
            if os.path.exists(image_path):
                images.append(highResUpscale(Image.open(image_path)))
            else:
                print(f"Warning: Image file not found: {image_path}")
                continue
        
        if images:
            images[0].save(output_filename, save_all=True, append_images=images[1:], 
                         optimize=False, duration=duration, loop=0)
            return output_filename
        else:
            print("No valid images found to create GIF")
            return None
    except Exception as e:
        print(f"Error creating GIF: {e}")
        return None

def samusGif(output_dir=None):
    """
    Create Samus GIF with optional custom output directory.
    
    Args:
        output_dir (str): Directory to save the GIF (optional)
    """
    files = ["1.png","2.png","3.png","4.png","5.png","6.png","7.png","8.png","9.png","10.png"]
    
    # If output_dir is provided, prepend it to file paths
    if output_dir:
        files = [os.path.join(output_dir, f) for f in files]
    
    output_filename = 'samus.gif'
    if output_dir:
        output_filename = os.path.join(output_dir, output_filename)
    
    return createCustomGif(files, output_filename)
    
def feiGif(output_dir=None):
    """
    Create Fei GIF with optional custom output directory.
    
    Args:
        output_dir (str): Directory to save the GIF (optional)
    """
    files = ["1a.png","2a.png","3a.png","4a.png","5a.png","6a.png","7a.png","8a.png"]
    
    # If output_dir is provided, prepend it to file paths
    if output_dir:
        files = [os.path.join(output_dir, f) for f in files]
    
    output_filename = 'fei.gif'
    if output_dir:
        output_filename = os.path.join(output_dir, output_filename)
    
    return createCustomGif(files, output_filename)
    
def bartGif(output_dir=None):
    """
    Create Bart GIF with optional custom output directory.
    
    Args:
        output_dir (str): Directory to save the GIF (optional)
    """
    files = ["Bart1.png","Bart2.png","Bart3.png","Bart4.png","Bart5.png","Bart6.png","Bart7.png","Bart8.png","Bart9.png","Bart10.png"]
    
    # If output_dir is provided, prepend it to file paths
    if output_dir:
        files = [os.path.join(output_dir, f) for f in files]
    
    output_filename = 'bart.gif'
    if output_dir:
        output_filename = os.path.join(output_dir, output_filename)
    
    return createCustomGif(files, output_filename)
    
def main():
    
    loop = 1
    
    print("This is a program that upscales + smoothes pixel art!")
    print("")
    
    while loop == 1:
    
        choice = input("Type 'u' to upscale a pixel art image. Type 'g' to export an animated gif of one of 3 characters: ")
        
        if choice.lower() == "u":
            
            print("")
            try:
                input_image = input("Enter the filename (with extension) of the original resolution pixel art you would like to upscale: ")
                my_image = Image.open(input_image)
                my_image.show()
                highResUpscale(my_image).show()
                loop = 0
            except OSError:
                print("")
                print("File not found.")
                print("")
        
        elif choice.lower() == "g":
            
            print("")
            character = input("Enter 'f', 'b' or 's' to export a gif of Fei, Bart (both from Xenogears) or Samus (Metroid), respectively: ")
            
            if character.lower() == "s" or character.lower() == "f" or character.lower() == "b":
            
                print("")
                print("Processing")
                
                if character.lower() == "s":
                
                    samusGif()
                    
                if character.lower() == "f":
                
                    feiGif()
                    
                if character.lower() == "b":
                
                    bartGif()
                
                print("")
                print("gif exported")
                
                loop = 0
                
            else:
                
                print("")
                print("Enter 'f', 'b', or 's'.")
                print("")
            
        else:
            
            print("")
            print("Type 'u' to upscale a pixel art image, 'g' for an animated gif.")
            print("")

if __name__ == "__main__":
    main()