from run_route_evaluation import coords_l

#read in faulty geometry
errorgeometry = coords_l[19]  #no maxspeed


geoms = []

# open file and read the content in a list
with open('errorgeoms.txt', 'r') as filehandle:
    for line in filehandle:
        # remove linebreak which is the last character of the string
        currentgeoms = line[:-1]
        # add item to the list
        geoms.append(currentgeoms)


#update list
geoms.append(errorgeometry)


#write list to file
with open('errorgeoms.txt', 'w') as f:
    for item in geoms:
        f.write("%s\n" % item)

#errorgeoms.txt is the name of the list with two error coordinates

#Read in the error geoms list




