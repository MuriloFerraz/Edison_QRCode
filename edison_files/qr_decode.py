#! /usr/bin/python

import cv2
import numpy
import socket
import zbar
import Image
import time
import mraa

## LED
led = mraa.Gpio(2)
led.dir(mraa.DIR_OUT)
led.write(0)

## OpenCV e mraa Version
OpenCV_version = str(cv2.__version__)
mraa_version = str(mraa.getVersion())

## Config Comunicacao
TCP_IP = ''
TCP_PORT = 5052
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind((TCP_IP,TCP_PORT))
serverSocket.listen(True)

## Hello!
print "Intel Edison"
print "OpenCV Version: " + OpenCV_version
print "mraa Version: "+ mraa_version
print "QR Code Decoder"

## Config captura

cap = cv2.VideoCapture(0)
print 'Resolucao padrao: (' + str(cap.get(3)) + ' x ' + str(cap.get(4)) + ')'
cap.set(3, 320)
cap.set(4, 240)
print 'Resolucao ajustada para: (' + str(cap.get(3)) + ' x ' + str(cap.get(4)) + ')'
encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]

## Config ZBar
scanner = zbar.ImageScanner()
scanner.parse_config('enable')

print 'Tudo pronto, aguardando a aplicacao cliente'
conn, add = serverSocket.accept()
print 'Transmitindo, aguardando QR Code ...'

while True:
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    pil = Image.fromarray(gray).convert('L')

    #raw = gray.tostring()
    raw = pil.tostring()
    image = zbar.Image(320, 240, 'Y800', raw) ## ???
    scanner.scan(image)

    for symbol in image:
        print 'Decoded', symbol.type, 'symbol', '"%s"' %symbol.data
        
        ## controle do led
        if symbol.data == '01':
            led.write(1)

        elif symbol.data == '00':
            led.write(0)

        #else:
        
        

    
    result, imgEncode = cv2.imencode('.jpg', frame, encode_param)
    #result, imgEncode = cv2.imencode('.jpg', image, encode_param)

    data = numpy.array (imgEncode)
    stringData = data.tostring()
    conn.send(str(len(stringData)).ljust(16));
    conn.send(stringData)

cap.release()    


