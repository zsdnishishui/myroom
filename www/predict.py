from __future__ import absolute_import, division, print_function, unicode_literals

import os

from tensorflow import keras

import tensorflow as tf
import numpy as np
def get_winstate(img_url):
    model = keras.models.load_model('/home/pi/tf_model/my_model.h5')
    
    #model.summary()
    #Then you have to compile the model in order to make predictions.
    lable_hua=['chuang_close', 'chuang_open']
    image=tf.keras.preprocessing.image
    #model.compile(optimizer = 'adam', loss = 'binary_crossentropy', metrics = ['accuracy'])
    test_image = image.load_img(img_url, target_size = (256, 256)) 
    test_image = image.img_to_array(test_image)
    test_image = np.expand_dims(test_image, axis = 0)
    #predict the result
    result = model.predict(test_image)
    index=np.argmax(result[0])
    return lable_hua[index]
    