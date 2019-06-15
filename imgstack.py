import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont


def write_txt(txt,size,color,myfont,ftsize = 100,ftcolor=(0,0,0)):
    
    font = ImageFont.truetype(myfont,ftsize)
    img=Image.new("RGBA", size, color)
    draw = ImageDraw.Draw(img)
    w,h = draw.textsize(txt, font=font)
    draw.text(((size[0]-w)/2,(size[1]-h)/2),txt,ftcolor,font=font)
    draw = ImageDraw.Draw(img)
    return img.convert('RGB')

def v_stack(imgs):
    t_width = imgs[0].size[0]
    imgs_comb = np.vstack([np.asarray(i.resize( (t_width, t_width * i.size[1]/i.size[0]) )) for i in imgs])
    return Image.fromarray(imgs_comb)


def h_stack(imgs):
    t_height = imgs[0].size[1]
    imgs_comb = np.hstack([np.asarray(i.resize( (int(float(t_height*i.size[0]))/i.size[1], t_height) )) for i in imgs])
    return Image.fromarray(imgs_comb)

def horizontal_img(A,B,S,P):
    
    temp = [write_txt(S,(150,100),(255,255,255),"Times New Roman.ttf",65), write_txt(P,(150,100),(230,230,230),"Times New Roman.ttf",65)]
    temp_v = Image.fromarray(np.vstack(temp))
    
    color = (130,130,130)
    if S != "0-0":
        
        if S == P:
            color = (0,175,0)
        elif (S[0] > S[2]) == (P[0] > P[2]):
            color = (195,195,0)
        else:
            color = (175,0,0)
    im=Image.new("RGB", (20,200), color)
    
    imgs = [Image.open("./resources/"+A.replace(" ", "")+".jpg"),temp_v,im,Image.open("./resources/"+B.replace(" ", "")+".jpg")]
        
    return h_stack(imgs)


def header_gen():
    A = write_txt("Team 1",(250, 100),(0,0,0),"Arial.ttf",50,(255,255,255))
    S = write_txt("Score",(140, 50),(0,0,0),"Arial.ttf",25,(255,255,255))
    P = write_txt("Prediction",(140, 50),(0,0,0),"Arial.ttf",25,(255,255,255))
    B = write_txt("Team 2",(250, 100),(0,0,0),"Arial.ttf",50,(255,255,255))

    SP = v_stack([S,Image.new("RGB", (300, 5), (255,255,255)),P])
    combo = h_stack([A,Image.new("RGB", (2, 100), (255,255,255)), SP, Image.new("RGB", (2, 100), (255,255,255)), B])
    return v_stack([Image.new("RGB", (1000, 10), (255,255,255)), combo, Image.new("RGB", (1000, 10), (255,255,255))])


def vertical_img(imgs1,imgs2, title = ""):
    
    brk = Image.open("./resources/break3.jpg")
    
    imgs1.insert(0,header_gen())
    result1 = [brk] * (len(imgs1) * 2 - 1)
    result1[0::2] = imgs1
    stack1 = v_stack(result1)
    
    imgs2.insert(0,header_gen())
    result2 = [brk] * (len(imgs2) * 2 - 1)
    result2[0::2] = imgs2
    stack2 = v_stack(result2)

    stack3 = h_stack([stack1,Image.new("RGB", (100, 1500), (255,255,255)),stack2])
    result = [stack3]
    
    if title != "":
        title = title[:5]+" "+title[5:-1]+" "+title[-1]
        result.insert(0,write_txt(title,(1220,150),(250,156,29),"Times New Roman Bold.ttf"))

    return v_stack(result)


def save_img(im,name,disp=False):
    if disp:
        im.show()
    im.save(name)

def main():
    pass


if __name__ == "__main__":
    main()
