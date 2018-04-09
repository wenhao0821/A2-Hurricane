"""
this program is used to analyze hurricane records file under the instructions of assignment 2 in 590PR.

"""
import datetime
from pygeodesy import ellipsoidalVincenty as ev

def get_one_storm_data(infile):
    """
    This function is used to get all the data for one storm at a time and put them in a dictionary.
    :param infile: the file pointer of the file we like to process
    :return: data_dic: the data dictionary contains all the data for one storm
    :return: terminal_flag: the flag to indicate if the file has reached the end
    """
    data_dic = {}  # use dictionary to record one storm
    terminal_flag = False
    line = infile.readline()
    if line == '':  # if we reach the end of the file, break
        terminal_flag = True
    elif line[0].isalpha():  # find every header in the file
        header = line.split(",")  # split the csv format data with comma and get the list
        storm_ID = header[0]  # The ID will be the first item in the list
        if "UNNAMED" not in header[1]:  # if the header has a real name, record it, else, set the name to null
            storm_name = header[1].lstrip(' ')
        else:
            storm_name = 'NA'
        data_dic['ID'] = storm_ID
        data_dic['name'] = storm_name
        data_line_number = header[2]  # set the number of lines of data to an integer variable
        for index in range(int(data_line_number)):
            line = infile.readline()
            data = line.split(',')
            data_dic[index] = data
    return data_dic,terminal_flag


def calculateTotaldistance(data_dic):
    """
    This function takes the storm data dictionary and return the total distance this storm moved.
    :param data_dic: the data dictionary used to store all the data of one storm
    :return: total_distance: the total distance one storm moved
    """
    total_distance = 0
    if len(data_dic)==3:#if the list only contains one data, then pass
        pass
    else:
        for index in range(1,len(data_dic)-2):#go through the list and calculate the distance between every two adjoint data
            if [data_dic[index-1][4],data_dic[index-1][5]]==[data_dic[index][4],data_dic[index][5]]:#if the location of both items are equal, pass
                pass
            else:#else, set the two locations to point_a and point_b, then calculate the distance between a and b
                point_a = myLatLon(data_dic[index-1][4],data_dic[index-1][5])  # set the previous location as point a
                point_b = myLatLon(data_dic[index][4],data_dic[index][5])  # set the following location as point b
                total_distance+=point_a.distanceTo(point_b)  # add the distance to total_distance

    return total_distance

def flip_direction(direction: str) -> str:
    """Given a compass direction 'E', 'W', 'N', or 'S', return the opposite.
    Raises exception with none of those.

    :param direction: a string containing 'E', 'W', 'N', or 'S'
    :return: a string containing 'E', 'W', 'N', or 'S'
    """
    if direction == 'E':
        return 'W'
    elif direction == 'W':
        return 'E'
    elif direction == 'N':
        return 'S'
    elif direction == 'S':
        return 'N'
    else:
        raise ValueError('Invalid or unsupported direction {} given.'.format(direction))


def myLatLon(lat: str, lon: str):
    """Given a latitude and longitude, normalize them if necessary,
    to return a valid ellipsoidalVincenty.LatLon object.

    :param lat: the latitude as a string
    :param lon: the longitude as a string
    """

    # get number portion:
    if lon[-1] in ['E', 'W']:
        lon_num = float(lon[:-1])
        lon_dir = lon[-1]
    else:
        lon_num = float(lon)
    if lon_num > 180.0:  # Does longitude exceed range?
        lon_num = 360.0 - lon_num
        lon_dir = flip_direction(lon_dir)
        lon = str(lon_num) + lon_dir

    return ev.LatLon(lat, lon)

def calculate_speed(data_dic,distance):
    """
    This function takes storm data dictionary and the total distance this storm moved and return the max and mean speed.
    :param data_dic: the data dictionary used to store all the data of one storm
    :param distance: the total distance one storm moved
    :return: Max_speed: Maximum propagation speed of this storm
    :return: Average_speed: Mean propagation speed of this storm
    """
    Max_speed = 0
    Average_speed=0
    speed_list = []
    total_time=0
    if len(data_dic)==3:  # if the list only contains one data, then pass
        pass
    else:
        for index in range(1,len(data_dic)-2):#go through the list and calculate the distance between every two adjoint data

            if [data_dic[index-1][4],data_dic[index-1][5]]==[data_dic[index][4],data_dic[index][5]]:#if the location of both items are equal, pass
                pass
            else:#else, set the two locations to point_a and point_b, then calculate the distance between a and b
                point_a = myLatLon(data_dic[index-1][4],data_dic[index-1][5])  # set the previous location as point a
                point_b = myLatLon(data_dic[index][4],data_dic[index][5])  # set the following location as point b
                time1 = transform_date_time(data_dic[index-1][0],data_dic[index-1][1].lstrip(' '))
                time2 = transform_date_time(data_dic[index][0],data_dic[index][1].lstrip(' '))
                time_duration = (time2-time1).seconds / 3600
                total_time+= time_duration
                speed=point_a.distanceTo(point_b)/1852/time_duration #add the distance to total_distance
                speed_list.append(speed)

        if speed_list!= []:
            Max_speed = max(speed_list)
            Average_speed = distance/total_time

    return Max_speed,Average_speed

def transform_date_time(date,time):
    """
    This function takes date and time(optional) and return a new time in datetime format.
    :param date: the date with only digits
    :param time: the time with only digits
    :return: new time in datetime format
    """
    if date=='' or time=='':
        pass
    else:
        year = date[0:4]
        month = date[4:6]
        day = date[6:8]
        hour = time[0:2]
        minute = time[2:4]
        new_time = datetime.datetime.strptime(year + '-' + month + '-' + day + ' ' + hour + ':' + minute + ':00',
                                           '%Y-%m-%d %H:%M:%S')
    return new_time

def get_max_sustained_wind(data_dic):
    """
    This functions is used to find out the highest max sustained wind and the first date and time it happened.
    :param data_dic: the data dictionary used to store all the data of one storm
    :return: max: the highest max sustained wind
    :return: date_time: the first date and time the highest wind happened
    """
    max = 0
    date_time = ''
    for index in range(len(data_dic)-2):
        if int(data_dic[index][6])>max:
            max = int(data_dic[index][6])
            date_time = data_dic[index][0]+data_dic[index][1]
    return max,date_time

def get_date_range(data_dic):
    """
    This function is used to find out the date range of one storm.
    :param data_dic: the data dictionary used to store all the data of one storm
    :return: initial_date: the date the tracing began
    :return: last_date: the date the tracing ended
    """
    initial_date = data_dic[0][0]+data_dic[0][1].lstrip(' ')
    last_date = data_dic[len(data_dic)-3][0]+data_dic[len(data_dic)-3][1].lstrip(' ')
    return initial_date,last_date

def get_landfall_count(data_dic):
    """
    This function is used to calculate the number of times one storm had landfalls.
    :param data_dic: the data dictionary used to store all the data of one storm
    :return: count: the number of times one storm had landfalls
    """
    count = 0
    for index in range(len(data_dic) - 2):
        if 'L' in data_dic[index][2]:
            count+=1
    return count

def get_storm_count(data_dic,year_dic):
    """
    This function is used to keep updating the record of numbers of storms and hurricanes every year.
    :param data_dic: the data dictionary used to store all the data of one storm
    :param year_dic: the dictionary used to record the number of storms and hurricanes every year
    :return: year_dic: the new year_dic
    """
    HU_flag = False
    year = data_dic['ID'][4:]
    if year not in year_dic:
        year_dic[year] = [0,0]
    for index in range(len(data_dic)-2):
        if 'HU' in data_dic[index][3]:
            HU_flag = True
    if HU_flag==True:
        year_dic[year][0]+=1
        year_dic[year][1]+=1
    else:
        year_dic[year][0]+=1
    return year_dic

def find_direction(single_list):
    """
        This function is used to get the quadrant with the highest winds from the data dictionary.
        :param single_list: a single line of the data dictionary
        :return: direction: the quadrant with the highest winds
        """
    index=0
    single_list =single_list[:-1]

    while int(single_list[index - 1])+int(single_list[index - 2])+int(single_list[index - 3])+int(single_list[index - 4])<=0 and index>-7:
        index=index-4
    new_list=[]
    new_list.append(int(single_list[index - 1]))
    new_list.append(int(single_list[index - 2]))
    new_list.append(int(single_list[index - 3]))
    new_list.append(int(single_list[index - 4]))

    if max(new_list)==new_list[3]:
        direction= ['northeastern']
        if new_list[3]==new_list[2]:
            direction.append('southeastern')
            if new_list[3]==new_list[1]:
                direction.append('southwestern')
            elif new_list[3]==new_list[0]:
                direction.append('northwestern')
        elif new_list[3]==new_list[1]:
            direction.append('southwestern')
            if new_list[3]==new_list[0]:
                direction.append('northwestern')
    elif max(new_list)==new_list[2]:
        direction = ['southeastern']
        if new_list[2] == new_list[1]:
            direction.append('southwestern')
            if new_list[2]==new_list[0]:
                direction.append('northwestern')
        elif new_list[2] == new_list[0]:
            direction.append('northwestern')
    elif max(new_list) == new_list[1]:
        direction = ['southwestern']
        if new_list[1] == new_list[0]:
            direction.append('northwestern')
    else:
        direction= ['northwestern']
    if new_list[0]==new_list[1]==new_list[2]==new_list[3]:
        direction=0
    if max(new_list)<= 0:
        direction=0

    return direction

def truepercent(data_dic):
    """
    This function is used to get the event times that were true and the total event times, then return these as integers.
    :param data_dic: the data dictionary used to store all the data of one storm
    :return: true_event: the event times this was true
    :return: event: the total event times
    """
    true_event = 0
    event = 0
    if len(data_dic)==3:#if the list only contains one data, then pass
        pass
    else:
        for index in range(1,len(data_dic)-2):#go through the list and calculate the distance between every two adjoint data

            if [data_dic[index-1][4],data_dic[index-1][5]]==[data_dic[index][4],data_dic[index][5]]:#if the location of both items are equal, jump out of the loop
                continue
            if find_direction(data_dic[index])==0:  #if the return direction equals to 0, jump out of the loop
                continue
            else:#else, set the two locations to point_a and point_b, then calculate the distance between a and b
                point_a = myLatLon(data_dic[index-1][4],data_dic[index-1][5])  # set the previous location as point a
                point_b = myLatLon(data_dic[index][4],data_dic[index][5])  # set the following location as point b
                bearing1 = point_a.bearingTo(point_b)+90
                bearing2 = point_a.bearingTo(point_b) + 45
                wind_direction1=get_direction(bearing1)
                wind_direction2 = get_direction(bearing2)
                if wind_direction1 in find_direction(data_dic[index]) or wind_direction2 in find_direction(data_dic[index]):
                    true_event= true_event+1
                    event = event +1
                else:
                    event= event+1

    return true_event, event

def get_direction(bearing):
    """
        This function is used to get the storm’s recent direction of movement and return it as a string.
        :param bearing: the bearing degree between two points
        :return: wind_direction: the recent direction of movement
        """
    if bearing >= 360:
        bearing = bearing - 360
    if bearing >= 0 and bearing <= 90:
        wind_direction = 'northeastern'
    elif bearing > 90 and bearing <= 180:
        wind_direction = 'southeastern'
    elif bearing > 180 and bearing <= 270:
        wind_direction = 'southwestern'
    elif bearing > 270 and bearing < 360:
        wind_direction = 'northwestern'
    else:
        wind_direction='NA'
    return wind_direction

def main():
    try:
        file_name = input("Please input the file you want to process: ")#get the filename
        outfile = open(file_name.rstrip('.txt')+'-Storminfo.txt','w')#this file stores all the information that relates to each storm.
        outfile2 = open(file_name.rstrip('.txt')+'-SUMMARY.txt', 'w')#this file stores the information of numbers of storms and huriicanes for each year.
        with open(file_name,'r') as infile:

            storm_hurricane_count = {}
            true_event= 0
            event=0
            while 1:
                result,flag = get_one_storm_data(infile)
                if flag == True:
                    break

                else:
                    max_sustained_wind,max_date = get_max_sustained_wind(result)

                    initial_date,last_date = get_date_range(result)
                    landfall_count = get_landfall_count(result)
                    storm_hurricane_count = get_storm_count(result,storm_hurricane_count)
                    distance = calculateTotaldistance(result)/1852.00
                    Max_speed, Average_speed= calculate_speed(result,distance)
                    tnum , enum = truepercent(result)
                    true_event=true_event+ tnum
                    event=event+ enum
                    if result["name"]=='NA':
                        print("The storm id is {}, the storm has no name".format(result["ID"]),
                              file=outfile)
                    else:
                        print("The storm id is {}, the storm name is {}".format(result["ID"],result["name"]),file=outfile)  # print the results
                    print("Date range is from {} to {}".format(transform_date_time(initial_date[0:8],initial_date[8:12]), transform_date_time(last_date[0:8],last_date[8:12])),file=outfile)
                    if max_sustained_wind==0:
                        print('There is no maximum sustained wind of this storm.',file = outfile)
                    else:
                        print("The highest Maximum sustained wind is {}, and the date it first occured is {}".format(
                        max_sustained_wind, transform_date_time(max_date[0:8],max_date[9:13])),file=outfile)
                    print("The number of times it had a 'landfall is {}".format(landfall_count),file=outfile)
                    print("the TOTAL distance is {}".format(distance),file=outfile)
                    print("the Maximum propagation speed is {}".format(Max_speed),file=outfile)
                    print("the Mean propagation speed is {}".format(Average_speed),file=outfile)
                    print('\n',file=outfile)
            for k in storm_hurricane_count.keys():

                print("In", k, ", there are",storm_hurricane_count[k][0],"storms and",
                      storm_hurricane_count[k][1],"hurricanes", file=outfile2)
        print('On {}% of the time, the hypothesis was true.'.format(true_event/event*100))
    except FileNotFoundError:
        print("File not found.")
    else:
        print('successfully loaded')

if __name__ == '__main__':
    main()
