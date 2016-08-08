# AUTHOR: Christina Davis

import matplotlib as mpl
import matplotlib.patches as mpatches
import subprocess
import graphviz as gv
import functools
import numpy as np

childrenlist=open('childrenlist.txt', 'r') #opens a file containing all children_xxx.txt files
redshift=open('redshifts.list', 'r')

#PARAMETERS
numberofsnaps=50
halochoice=37
#also change which dotfile to write to at the bottom

foundhalo=False #flag


#create array of snaps from childrenlist where i=0 corresponds to children_001.txt
snaparray=[]
familytree1=[] #first dimension of familytree array contains parentsnap, groupnum, childsnap, childnum
familytree=[] #2d array of all history of halo
familytreei=[] #initial family tree, will be used to help create actual familytree
parents=[] #holding array for all parent infos. 2d array. each elmt contains all info about that parent
children=[] #holding array for all children 2d array. each elmt contains all info about that child
familytree2=[] #holding array. similar to familytree1 except for all halos other than papa


for i in range (0, numberofsnaps):
    snap0=childrenlist.readline()
    snap=snap0.strip('\n')
    snaparray.append(snap)

#count backwards through snaps. want to start with snap 50 since this is z=0 to look for papa ID
for i2 in range (50, 50-numberofsnaps, -1):
    if foundhalo==False:
        count=i2-1  #so count should match snap number
        x=snaparray[count]
        y=open(x, 'r') #open the first snap starting with 50 to look for halochoice
        ParentSnap, GroupNum, HaloID, ChildNum, ChildSnap,childmass, childid=np.loadtxt(snaparray[count], usecols=(0,1,2,6,8,5,7), unpack=True)
        numrows=len(HaloID) #how many items are in the arrays
        for rowcounter in range (0, numrows):  #look through the rows in this snap to find halochoice
            if HaloID[rowcounter]==halochoice: #if you find it, save the info for all occurances
                currentsnap=ParentSnap[rowcounter]
                parentgroup=GroupNum[rowcounter]
                nextsnap=ChildSnap[rowcounter]
                childgroup=ChildNum[rowcounter]
                familytree1.append(currentsnap)
                familytree1.append(parentgroup)
                familytree1.append(nextsnap)
                familytree1.append(childgroup)
                familytree1.append(0)
                familytree1.append(HaloID[rowcounter])
                familytree1.append(childmass[rowcounter])
                familytreei.append(familytree1)
                familytree1=[] #empty this array to use for next occurance
        foundhalo=True #you've now found your papa halo so move to children

#familytree has [current snap, parent group, next snap, childgroup, dotid, haloid]



identity=1
#now we've found the papa and all it's activity. move on to iterate through children by using groupnum
parents=familytreei
for i3 in range (0, numberofsnaps-1): #iterate 50 times
    numparents=len(parents)
    for i4 in range (0, numparents): #loop through parent columns for their children
        snapnumber=int(parents[i4][2])
        x=snaparray[snapnumber-1]
        y=open(x, 'r')
        ParentSnap, GroupNum, HaloID, ChildNum, ChildSnap, ChildMass, chlildid=np.loadtxt(snaparray[snapnumber-1], usecols=(0,1,2,6,8,5,7), unpack=True)
        numrows=len(HaloID)
        for rowcounter in range (0, numrows): #look for matches and store info in children array
            if GroupNum[rowcounter]==parents[i4][3]:
                currentsnap=ParentSnap[rowcounter]
                parentgroup=GroupNum[rowcounter]
                nextsnap=ChildSnap[rowcounter]
                childgroup=ChildNum[rowcounter]
                haloid=HaloID[rowcounter]
                childmass=ChildMass[rowcounter]
                children.append([currentsnap, parentgroup, nextsnap, childgroup, identity, haloid,childmass])
                identity=identity+1

    for i5 in range (0, numparents):
        familytree.append(parents[i5])
    parents=children
    children=[]

print "currentsnap, parentgroup, nextsnap, childgroup, identity, haloid, childmass"
for i in range (0, 20):
    print familytree[i]

familytreefile=open("familytree.txt", 'w')
familytreefile.close()
familytreefile=open("familytree.txt", 'a')
np.savetxt('familytree.txt', familytree, delimiter=',', fmt='%d')



#making the .dot file!!!
testdot = open("testdot37.dot", 'w')
testdot.close()
testdot=open("testdot37.dot", 'a')
testdot.write("graph {\n ")
testdot.write("rankdir=TD;\n")


#plotting the snapshot list
z=np.fromfile(redshift, dtype=float, sep=" ")[::-1]
i=numberofsnaps
for j in range (0, numberofsnaps):
    testdot.write("snap"+str(i))
    testdot.write(" -- {")
    testdot.write("snap"+str(i-1))
    testdot.write("};\n")
    testdot.write("snap"+str(i)+' [shape=box, peripheries=1, color=palegreen, labelfontsize=16, style=filled, label="z={:6.3f}"'.format(z[j])+"];\n")
    i=i-1
testdot.write('snap0 [shape=box, peripheries=1, color=palegreen, style=filled, label="z=21.170"]\n')


#plotting the mergertree
for i6 in range (0, len(familytree)):
     testdot.write("snap"+str(int(familytree[i6][0]))+"group"+str(int(familytree[i6][1])))
     testdot.write("--{")
     for i7 in range (0, len(familytree)):
        if familytree[i6][2]==familytree[i7][0] and familytree[i6][3]==familytree[i7][1]:
            testdot.write("snap"+str(int(familytree[i7][0]))+"group"+str(int(familytree[i7][1]))+" ")
     testdot.write("};\n")
     if familytree[i6][5]==halochoice:
         testdot.write("snap"+str(int(familytree[i6][0]))+"group"+str(int(familytree[i6][1]))+'[shape=circle, peripheries=1, color=hotpink, style=filled, label=" "];\n') #this is the primary halo
     else:
         testdot.write("snap"+str(int(familytree[i6][0]))+"group"+str(int(familytree[i6][1]))+'[shape=circle, peripheries=1, color=lightpink, style=filled, label=" "];\n') #these are halos other than primary halo, if you want to see them change color from lightpink

"""
#adding grey to most massive halo in each snapshot
childmasses=[]
childmasses0=[]
bigchild=[]#this array will hold all child masses from one step and then we will take the max
for i11 in range (50, 1, -1): #this is mad if it runs out of snaps, so change the end snap with wherever the tree ends.
    for i12 in range (0, len(familytree)):
        if familytree[i12][0]==i11:
            childmasses0.append(familytree[i12][6])
            childmasses0.append(i11)
            childmasses0.append(familytree[i12][1])
            childmasses.append(childmasses0)
            childmasses0=[]

    biggestmass=max([poop[0] for poop in childmasses])
    x=[x for x in childmasses if biggestmass in x][0]
    index=childmasses.index(x)
    biggestsnap=childmasses[index][1]
    biggestgroup=childmasses[index][2]
    testdot.write("snap"+str(int(biggestsnap))+"group"+str(int(biggestgroup))+'[shape=circle, peripheries=1, color=slategrey, style=filled, label=" "];\n')
    childmasses=[]
"""



#add rank to mergertree
for i8 in range (1, 51):
    for i9 in range (0, len(familytree)):
        if i8==familytree[i9][0]:
            testdot.write("{ rank = same; ")
            testdot.write("snap"+str(i8)+"; ")
            testdot.write("snap"+str(int(familytree[i9][0]))+"group"+str(int(familytree[i9][1]))+"};\n")



#adding flybys
flybys=open("fof_to_subhalo_mergers.txt", 'r')
snap, parentgroup, parentmass, flybygroup, flybymass, tag, subhaloID=np.loadtxt(flybys, usecols=(0,1,3,4,6,12,5), unpack=True)
flybycount=0 #numberoflybysfound
for i9 in range (0, len(familytree)):    #i9 goes through each elmt of familytree
    for i10 in range (0, len(snap)):     #i10 goes through giant flyby list
        if familytree[i9][5]==halochoice and familytree[i9][0]==snap[i10] and familytree[i9][1]==parentgroup[i10] and tag[i10]==3 or tag[i10]==5:
#        if familytree[i9][0]==snap[i10] and familytree[i9][1]==parentgroup[i10] and tag[i10]==3 or tag[i10]==5:
#            print snap[i10], subhaloID[i10]
            masslarge=max(parentmass[i10], flybymass[i10])
            masssmall=min(parentmass[i10], flybymass[i10])
            massratio=masslarge/masssmall
            if massratio <=1000000:
                testdot.write("{ rank = same; ")
                testdot.write("snap")
                testdot.write(str(int(snap[i10])))
                testdot.write("; flyby"+str(int(flybycount)))
                testdot.write("};\n")
                testdot.write("flyby"+str(int(flybycount))+' [shape=circle, peripheries=2, color=lightblue, style=filled, label=" "];\n')
                flybycount=flybycount+1




testdot.write("}")
