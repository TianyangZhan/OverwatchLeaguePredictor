import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont


def scoregen(score,size,color,myfont):
    
    font = ImageFont.truetype(myfont,100)
    img=Image.new("RGBA", size, color)
    draw = ImageDraw.Draw(img)
    w,h = draw.textsize(score, font=font)
    draw.text(((size[0]-w)/2,(size[1]-h)/2),score,(0,0,0),font=font)
    draw = ImageDraw.Draw(img)
    return img.convert('RGB')


def horizontal_img(A,B,S,P):

    color = (130,130,130)
    
    if S != "0-0":
        
        if S == P:
            color = (0,175,0)
        elif (S[0] > S[2]) == (P[0] > P[2]):
            color = (195,195,0)
        else:
            color = (175,0,0)

    im=Image.new("RGB", (10,200), color)
    
    imgs = [Image.open("./resources/"+A.replace(" ", "")+".jpg"), scoregen(S,(300,200),(255,255,255),"Times New Roman.ttf"), Image.open("./resources/"+B.replace(" ", "")+".jpg"), scoregen(P,(300,200),(230,230,230),"Times New Roman.ttf"),im]

    # pick the image which is the smallest, and resize the others to match it
    min_shape = sorted( [(np.sum(i.size), i.size ) for i in imgs])[0][1]
    imgs_comb = np.hstack( [np.asarray( i.resize(min_shape) ) for i in imgs ] )
    return Image.fromarray(np.hstack(imgs))


def vertical_img(imgs, title = ""):
    
    imgs.insert(0,Image.open("./resources/header4.jpg"))
    
    if title != "":
        title = title[:5]+" "+title[5:-1]+" "+title[-1]
        imgs.insert(0,scoregen(title,(1210,150),(250,156,29),"Times New Roman Bold.ttf"))

    brk = Image.open("./resources/break2.jpg")
    result = [brk] * (len(imgs) * 2 - 1)
    result[0::2] = imgs
    return Image.fromarray(np.vstack(result))

def save_img(im,name,disp=False):
    if disp:
        im.show()
    im.save(name)

def main():

    '''
    lst = []
    for i in range(3):
        lst.append(horizontal_img(A,B,S,P))
    im = verticaltal_img(lst)
    im.show()
    '''


if __name__ == "__main__":
    main()
