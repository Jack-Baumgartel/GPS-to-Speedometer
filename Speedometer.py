
#first let the user know it's working!
print('Welcome to the GPS speedometer, loading dependencies...')

#first import the libraries we'll probably need
import numpy as np
from math import sin, cos, sqrt, atan2, radians
from PIL import Image, ImageDraw, ImageFont
import cv2
from IPython.display import clear_output

#clear_output(wait=True)
print('Dependencies loaded! \n')

#get the location of the coordinate list
filepath = "Coordinates.txt"

#assume likely sample rate based on calculated speed (rate is seconds between each reading)
sample_rate = .9

#give some user feedback
#clear_output(wait=True)
print("Running some calculations...")

#open the local coordinate txt file and read contents into a list
with open(filepath, 'rt', encoding="utf-8") as myfile:
    doc=myfile.read().split('\n')
    
#iterate over given string list and convert it to list of numpy floats
coordinate_list = []
for i in range(len(doc)):
    #seperate the lat & long then store them as floats
    list_items = doc[i].split(',')
    lat = float(list_items[0])
    long = float(list_items[1])
    
    coordinate_list.append([lat, long])
    
def getDistanceFromLatLonInKm(lat1,lon1,lat2,lon2):
    R = 6371 # Radius of the earth in km
    dLat = radians(lat2-lat1)
    dLon = radians(lon2-lon1)
    rLat1 = radians(lat1)
    rLat2 = radians(lat2)
    a = sin(dLat/2) * sin(dLat/2) + cos(rLat1) * cos(rLat2) * sin(dLon/2) * sin(dLon/2) 
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    d = R * c # Distance in km
    return np.round(d, 5)

#calculate distance between consecutive readings, and speed in metric & customary
distance_list = []
for start in range(len(coordinate_list)):
    start_lat = coordinate_list[start][0]
    start_long = coordinate_list[start][1]
    
    if start < len(coordinate_list)-1:
        end_lat = coordinate_list[start+1][0]
        end_long = coordinate_list[start+1][1]
    
    
        dist_km = getDistanceFromLatLonInKm(start_lat, start_long, end_lat, end_long)
        dist_ft = np.round(dist_km*3280.84, 2)

        distance_list.append([dist_km, dist_ft])
    else:
        pass
    
#convert those distances to speeds using the assumed sample rate

#get a list of the distances in ft only
dist_ft = np.array(distance_list)[:,1]
#use the sample rate to determine speed in mph
speed_mph = dist_ft/sample_rate*0.681818
#also back calculate speed in kmh
speed_kmh = speed_mph*1.60934

#store the calculated values together
speeds = np.array([speed_mph, speed_kmh])

#clear_output(wait=True)
print("Calculations complete! \n")

print("Generating template frame...")

#first create the template to use for all speed frames

#set final image width & height
width = 350
height = 100
green_frame = Image.new('RGB', (width, height), (55,255,51))

#text fill and stroke color
fill_c = (0,0,0)
stroke_c = (255,255,255)

#set fonts for each bout of text
big_font = ImageFont.truetype('/Library/Fonts/LCD.ttf', 100)
small_font = ImageFont.truetype('/Library/Fonts/LCD.ttf', 40)

#add the MPH to bottom right of text
x = ImageDraw.Draw(green_frame)
x.text((int(width*.72),int(height*.6)), "MPH", fill=fill_c,stroke_fill = stroke_c, stroke_width=2,
       anchor="lt", font=small_font)

def create_frame(green_frame, speed, index):
    current_speed = np.round(speed, 1)
    current_frame = green_frame.copy()

    d = ImageDraw.Draw(current_frame)

    #add the current speed
    d.text((int(width*.7),int(height*.9)), f"{current_speed}", 
           fill=fill_c, stroke_fill = stroke_c, stroke_width=2,
           align="center", anchor = "rb", font=big_font)
    
    #save the frame using the index as filename
    #current_frame.save(f'GreenBG Frames/Frame {index}.png')

    #return the image as an array
    return np.array(current_frame)


print("Generating successive frames and compiling video...")

#now turn all of the frames into a single video file
result_filename = f'Result {np.round(1/sample_rate,2)}hz.mp4'
out = cv2.VideoWriter(result_filename, cv2.VideoWriter_fourcc(*'avc1'), #use 'MP4V' or *'avc1' 
                      1/sample_rate, (width, height)) 


#iterate over speeds, create the frame, store it as an array and then write the file
for index, speed_mph in enumerate(speeds[0]):
    
    img = create_frame(green_frame, speed_mph, index)

    out.write(img)
    
out.release()
    
print(f"Video finished & saved as '{result_filename}'\n")

