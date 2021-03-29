#! /bin/bash/python3

import requests
import json
import base64
import cv2
import copy
import numpy as np
from requests_html import HTMLSession

url = "http://104.197.195.221:8085/"
r = requests.get(url)

#repeat 500 times again
for b in range(500):
    #find the image in the response, and download it
    img_path = r.text[r.text.find('./static/chall-images')+2:(r.text.find('.jpg')+4)]
    img_url = url + img_path
    img_data = requests.get(img_url).content
    with open('img.jpg', 'wb') as handler:
        handler.write(img_data)

    #load the image with opencv
    img = cv2.imread('img.jpg', cv2.IMREAD_GRAYSCALE)
    im_x = img.shape[1]
    im_y = img.shape[0]


    ### Find the right place to cut the full image into the smaller pokemon
    # sum the pixel values of the image vertically, to get an estimate of how much whitespace is at that current position
    vert_sum = [sum(255 - img[0:im_y, x]) for x in range(im_x)]
    cut = [0, None, None, None, im_x]
    

    # Find the first cut point
    cut_off1 = int(im_x/8)
    cut_off2 = int(3*im_x/8)
    cut[1] = vert_sum[cut_off1:cut_off2].index(min(vert_sum[cut_off1:cut_off2])) + cut_off1

    # Recalculate the regions where we're looking for the cut points, and then find the second one
    cut_off2 = int(1*(im_x-cut[1])/6) + cut[1]
    cut_off3 = int(3*(im_x-cut[1])/6) + cut[1]
    cut_off4 = int(5*(im_x-cut[1])/6) + cut[1]
    cut[2] = vert_sum[cut_off2:cut_off3].index(min(vert_sum[cut_off2:cut_off3])) + cut_off2
    
    # Recalculate the region again, and find the third cut point
    cut_off3 = int(1*(im_x-cut[2])/4) + cut[2]
    cut_off4 = int(3*(im_x-cut[2])/4) + cut[2]
    cut[3] = vert_sum[cut_off3:cut_off4].index(min(vert_sum[cut_off3:cut_off4])) + cut_off3

    # Cut the image into 4 for feature matching
    p1 = img[0:im_y, 0:cut[1]]
    p2 = img[0:im_y, cut[1]:cut[2]]
    p3 = img[0:im_y, cut[2]:cut[3]]
    p4 = img[0:im_y, cut[3]:im_x]
    mon = [p1, p2, p3, p4]

    ### Feature matching on all 151 gen 1 pokemon using SIFT/FLANN
    # Initiate SIFT detector
    sift = cv2.SIFT_create()
    pnums = [None]*4

    #Loop for each pokemon
    for j, p in enumerate(mon):
        pmatches = [None]*151
        # Loop for each gen 1 pokemon to compare against
        for i in range(151):
            #grab the sprite of the ith pokemon
            cmpp = cv2.imread("gray/" + str(i+1) + ".png")
            
            # find the keypoints and descriptors with SIFT
            kp1, des1 = sift.detectAndCompute(p,None)
            kp2, des2 = sift.detectAndCompute(cmpp,None)

            # FLANN parameters
            FLANN_INDEX_KDTREE = 1
            index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 7)
            search_params = dict(checks=50)   # or pass empty dictionary
            flann = cv2.FlannBasedMatcher(index_params,search_params)
            matches = flann.knnMatch(des1,des2,k=2)

            matches_num = 0
            # ratio test as per Lowe's paper
            # if the feature passes the test, we consider the a match and increment the number of matches
            for k,(m,n) in enumerate(matches):
                if m.distance < 0.7*n.distance:
                    matches_num += 1
            pmatches[i] = matches_num
            
        # Find the pokemon that had the highest number of matches, and get it's pokedex number
        pnums[j] = pmatches.index(max(pmatches))+1

    # Construct our guess and the response
    ans = str(pnums[0]) + " " + str(pnums[1]) + " " + str(pnums[2]) + " " + str(pnums[3])
    data = {'guess': ans}
    r = requests.post(url, data=data, cookies = r.cookies)
    print(b, "guess:", ans)

# Print the response containing the flag!
print(r.text) # UMASS{1ts_m3_4nd_y0u!!P0k3m0n}