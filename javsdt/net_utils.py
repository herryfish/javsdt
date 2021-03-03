import io
from re import search

from PIL import Image
from requests import Session

from pyzbar.pyzbar import decode

# 处理图片 显示后输入或者其他方式输入后返回
def process_img(captchaimgtag):
    sc = captchaimgtag.screenshot()
    img = Image.open(io.BytesIO(sc))
    img.show(img)
    input_code = input('请输入图片显示的内容：')
    return input_code

def qr_analysis(img):
    return decode(img)

def test():
    image = 'D:\\downloads\\ダウンロード (2).png'
    img = Image.open(image)
    qrcoders = decode(img)
    for qrcoder in qrcoders:
        print(qrcoder.data.decode("utf-8"))

test()