import xml.etree.ElementTree as ET
import time

def check_open (fileName, mode):
    try:
        fileOpen = open(fileName,mode)
    except (OSError,IOError):
        print( "Error, Unable to open file! Please check that the following file exists and is not already open :"+fileName)
        raw_input("Press enter to continue") 
        exit()
    return fileOpen

def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i
            
def getBaseName(name):
    splitName = name.split('_')
    if (splitName[-1].isdigit()==True):
        newlist = splitName[:-1]
        newName = '_'.join(map(str, newlist))   
        return newName
    return name

def getBoundaryName(name):
    splitName = name.split('_i')
    if (splitName[-1].isdigit()==True):
        newName = splitName[0]  
        return newName
    return name

def findExistingPatch(projectname, names,modulename, check):
    tree = ET.parse(projectname)
    root = tree.getroot()
    for i in xrange(len(names)):
        found=0
        for module in root.getiterator('module'):
            if(module.get("type")==modulename):
                for bc in module.getiterator('bc'):
                    if(bc.get("patch")==names[i]): 
                        check.append(True)
                        found=1
        if(found==0):
            check.append(False)
            
def clearProject(tree):
    sim = tree.getroot()
    modules = sim.findall('module')
    for module in modules:
        bcs = module.findall('bc')
        for bc in bcs:
            module.remove(bc) 
        vcs = module.findall('vc')
        for vc in vcs:
            module.remove(vc) 
    for module in modules:
        sim.remove(module)

    
                    
def getBaseNameTest(name):
    initName=name
    for i in xrange(0,10):
        splitName = initName.split('_')
        if (splitName[-1].isdigit()==True):
            newlist = splitName[:-1]
            initName = '_'.join(map(str, newlist))   
    return initName  

def findExisting(allnames,existingnames,checklist):
    s = set(existingnames)
    for i in xrange(0,len(allnames)):
        if allnames[i] in s:
            checklist[i]=True  
            
def getOrigNameVol(namelist,degennames):
    for i in xrange(0,len(degennames)):
        #name= getBaseNameTest(degennames[i])
        name = getBaseName(degennames[i])          
        namelist.append(name)
        
def getOrigNameSurf(namelist,degennames):
    for i in xrange(0,len(degennames)):
        #name= getBaseNameTest(degennames[i])
        name1 = getBoundaryName(degennames[i])
        name = getBaseName(name1)
        namelist.append(name)
            
def linkNames(orignames,degennames,indexlist):
#    s = set(degennames)
    for i in xrange(0,len(degennames)):
        for j in xrange(0,len(orignames)):
            if(degennames[i]==orignames[j]):
                indexlist[i]=j
                
def linkNamesDict(orignames,degennames,indexlist):
    index_dict = dict((value, idx) for idx,value in enumerate(orignames))
    for i in xrange(0,len(degennames)):
        try:
            indexlist[i]=index_dict[degennames[i]]
        except (KeyError):
            continue


begin = time.time()
setupFileName = "VehicleThermalInput.txt"
inputFile = check_open(setupFileName,'r')
for line in inputFile:
    words=line.split()
    if len(words)==0:
        continue
    if words[0]=="#":
        continue
##    if words[0]=="execution_mode":
##        mode=words[1]
    if words[0]=="material_file":
        materialFileName=words[1]
    if words[0]=="volume_file":
        volumeFileName =words[1]
    if words[0]=="surface_file":
        surfaceFileName=words[1]
    if words[0]=="input_project":
        initialProject=words[1]
    if words[0]=="output_project":
        finalProject=words[1]     
    if words[0]=="mode":
        runMode=words[1] 

inputFile.close()

if(runMode != "create" and runMode != "setup"):
    print("Error! Incorrect Mode: Please specify either 'create' mode to create csv files or 'setup' mode to set conditions in project.")
    raw_input("Press enter to continue") 
    exit()

xml_encoding="ISO-8859-1"

materials=[]
matType = []
matDensity=[]
matViscosity=[]
matConductivity=[]
matCapacity=[]

materialFile = check_open(materialFileName,'r')
for line in materialFile:
    words=line.split(',')
    if len(words)==0:
        continue
    if words[0]=="Material Name":
        continue    
    materials.append(words[0])    
    matType.append(words[1])
    matDensity.append(words[2])
    matViscosity.append(words[3])
    matConductivity.append(words[4])
    cap=words[5].split()
    matCapacity.append(cap[0])
    
materialFile.close()

tree = ET.parse(initialProject)
root = tree.getroot()

boundaries=[]
interfaces=[]
volumes=[]

for module in root.getiterator('module'):
    if(module.get("type")=="flow"):
        for bc in module.getiterator('bc'):
            if (bc.get('type')=="default_interface"):
                interfaces.append(bc.get('patch'))
            else:
                boundaries.append(bc.get('patch'))
    if(module.get("type")=="share"):                
        for vc in module.getiterator('vc'):
                volumes.append(vc.get('volume'))


volumeOrigNames=[]
boundaryOrigNames=[]
interfaceOrigNames=[]

getOrigNameVol(volumeOrigNames,volumes)
getOrigNameSurf(boundaryOrigNames,boundaries)
getOrigNameSurf(interfaceOrigNames,interfaces)


if (runMode=="create"):
    surfaceNRNames = list(set(boundaryOrigNames+interfaceOrigNames))
    volumeNRNames = list(set(volumeOrigNames))
    surfaceNRNames.sort()
    volumeNRNames.sort()
    bcFile = check_open(surfaceFileName,'w')
    bcFile.write("Surface Name,BC Type,Temperature,HeatFlux,Convection,T Ref,Emmissivity,CAF"+"\n")
    for i in xrange (0,len(surfaceNRNames)):
        bcFile.write(surfaceNRNames[i]+ ",heatflux,300,0,0,300,0.7,1"+"\n")
    bcFile.close()
    
    volFile = check_open(volumeFileName,'w')
    volFile.write("Volume Name,Volume Material"+"\n")
    for i in xrange(0,len(volumeNRNames)):
        volFile.write(volumeNRNames[i]+ ",Steel"+"\n")
    volFile.close()
        
 
           
if (runMode=="setup"):
   
    clearProject(tree)
    
    volNames=[]
    volMaterials = []
    
    volumeFile = check_open(volumeFileName,'r')
    for line in volumeFile:
        words=line.split(',')
        if len(words)==0:
            continue
        if words[0]=="Volume Name":
            continue    
        volNames.append(words[0])  
        volmat = words[1].split()
        volMaterials.append(volmat[0])
    volumeFile.close()
    
    volMatIdx=[]
    
    for i in xrange(0,len(volNames)):
        volMatIdx.append(-1)
    
    linkNamesDict(materials,volMaterials,volMatIdx)
    
    for i in xrange(0,len(volNames)):
        if(volMatIdx[i]==-1):
            print ("Error: Could not find material information for "+volNames[i])
            print ("Error: Please provide information for material named "+volMaterials[i])
            raw_input("Press enter to continue") 
            exit()
    
    
    surfNames = []
    surfType=[]
    surfTemp=[]
    surfFlux=[]
    surfHTC=[]
    surfTref=[]
    surfEmiss=[]
    surfCAF=[]
    
    surfaceFile = check_open(surfaceFileName,'r')
    for line in surfaceFile:
        words=line.split(',')
        if len(words)==0:
            continue
        if words[0]=="Surface Name":
            continue    
        surfNames.append(words[0])  
        surfType.append(words[1])
        surfTemp.append(words[2])  
        surfFlux.append(words[3])  
        surfHTC.append(words[4])
        surfTref.append(words[5])
        surfEmiss.append(words[6])
        caf = words[7].split()
        surfCAF.append(caf[0])
    
    surfaceFile.close()
            
    volumeLink=[]
    boundaryLink=[]
    interfaceLink=[]
    
    for i in xrange(0,len(volumes)):
        volumeLink.append(-1)
    
    for i in xrange(0,len(boundaries)):
        boundaryLink.append(-1)
    
    for i in xrange(0,len(interfaces)):
        interfaceLink.append(-1)
    
    linkNamesDict(volNames, volumeOrigNames, volumeLink)
    elapsed = time.time() - begin
    linkNamesDict(surfNames, boundaryOrigNames, boundaryLink)
    elapsed = time.time() - begin
    linkNamesDict(surfNames, interfaceOrigNames, interfaceLink)
    elapsed = time.time() - begin
    
    module= ET.SubElement(root,'module')
    module.set('type','share')
    for ii in xrange(0,len(volumes)):
        linkIndex = volumeLink[ii]
        if(linkIndex!=-1):
            volumeName = volNames[linkIndex] 
            mi = volMatIdx[linkIndex]
            volType = matType[mi]
            volDensity = matDensity[mi]
            volViscosity = matViscosity[mi]
            volConductivity = matConductivity[mi]
            volCapacity = matCapacity[mi]   
            vc = ET.SubElement(module, 'vc')
            vc.set('volume',volumes[ii])
            if (volDensity=='Ideal Gas'):
                vc.set('type','ideal_gas_law')
            else:
                vc.set('type','const_density')
                vc.set('default','yes')
                vc.set('value',volDensity)    

    module= ET.SubElement(root,'module')
    module.set('type','flow')
    module.set('state','active')
    for ii in xrange(0,len(volumes)):
        linkIndex = volumeLink[ii]
        if(linkIndex!=-1):
            volumeName = volNames[linkIndex] 
            mi = volMatIdx[linkIndex]
            volType = matType[mi]
            volDensity = matDensity[mi]
            volViscosity = matViscosity[mi]
            volConductivity = matConductivity[mi]
            volCapacity = matCapacity[mi]   
            vc = ET.SubElement(module, 'vc')
            vc.set('volume',volumes[ii])
            if (volType=='Solid'):
                vc.set('type','blanked')
            else:
                vc.set('type','const_viscosity')
                vc.set('default','yes')
                vc.set('value',volViscosity)    
                
    module= ET.SubElement(root,'module')
    module.set('type','heat')
    module.set('state','active')
    for ii in xrange(0,len(volumes)):
        linkIndex = volumeLink[ii]
        if(linkIndex!=-1):
            volumeName = volNames[linkIndex] 
            mi = volMatIdx[linkIndex]
            volType = matType[mi]
            volDensity = matDensity[mi]
            volViscosity = matViscosity[mi]
            volConductivity = matConductivity[mi]
            volCapacity = matCapacity[mi]   
            vc = ET.SubElement(module, 'vc')
            vc.set('volume',volumes[ii])   
            if(volCapacity=="enth"):
                vc.set('type','user_expression')
                vc.set('expression_for_enthalpy',volCapacity)
            else:
                vc.set('type','const_capacity')
                vc.set('default','yes')
                vc.set('value',volCapacity)
            vc = ET.SubElement(module, 'vc')
            vc.set('volume',volumes[ii])
            vc.set('type','const_conductivity')
            vc.set('default','yes')
            vc.set('conductivity',volConductivity)  
    for i in xrange(0,len(boundaries)):
    #    boundaryName1 = getBoundaryName(boundaries[i])
    #    boundaryName = getBaseName(boundaryName1)
        linkIndex = boundaryLink[i]
        if(linkIndex!=-1):
            boundaryName = surfNames[linkIndex] 
            boundaryType = surfType[linkIndex]
            boundaryTemp = surfTemp[linkIndex]
            boundaryFlux = surfFlux[linkIndex]
            boundaryHTC = surfHTC[linkIndex]
            boundaryTref = surfTref[linkIndex]
            boundaryEmiss = surfEmiss[linkIndex]
            boundaryCAF = surfCAF[linkIndex]     
            if(boundaryType=="temperature"):
                bc=ET.SubElement(module,'bc')                          
                bc.set('patch',boundaries[i])                    
                bc.set('type','fix_t')
                bc.set('value',boundaryTemp)
            elif (boundaryType=="convection"):
                bc=ET.SubElement(module,'bc')                          
                bc.set('patch',boundaries[i])                 
                bc.set('type','external_flux')
                bc.set('exchange_coefficient',str(float(boundaryHTC)*float(boundaryCAF)))
                bc.set('ambient_temperature',boundaryTref)
            elif(boundaryType=="heatflux" and float(boundaryFlux)!=0):
                bc=ET.SubElement(module,'bc')                          
                bc.set('patch',boundaries[i])                 
                bc.set('type','fix_flux')
                bc.set('value',boundaryFlux)  

    module= ET.SubElement(root,'module')
    module.set('type','radiation')
    module.set('state','active')     
    for i in xrange(0,len(boundaries)):
    #    boundaryName1 = getBoundaryName(boundaries[i])
    #    boundaryName = getBaseName(boundaryName1)
        linkIndex = boundaryLink[i]
        if(linkIndex!=-1):
            boundaryName = surfNames[linkIndex] 
            boundaryType = surfType[linkIndex]
            boundaryTemp = surfTemp[linkIndex]
            boundaryFlux = surfFlux[linkIndex]
            boundaryHTC = surfHTC[linkIndex]
            boundaryTref = surfTref[linkIndex]
            boundaryEmiss = surfEmiss[linkIndex]
            boundaryCAF = surfCAF[linkIndex]  
            bc=ET.SubElement(module,'bc')                          
            bc.set('patch',boundaries[i]) 
            if(float(boundaryEmiss)!=0):                
                bc.set('type','radiate_bc')
                bc.set('emissivity',boundaryEmiss)
            else:                
                bc.set('type','open_bc')
                bc.set('temperature',boundaryTemp)    
    for i in xrange(0,len(interfaces)):
        linkIndex = interfaceLink[i]
        if(linkIndex!=-1):
            boundaryName = surfNames[linkIndex] 
            boundaryTemp = surfTemp[linkIndex]
            boundaryFlux = surfFlux[linkIndex]
            boundaryHTC = surfHTC[linkIndex]
            boundaryTref = surfTref[linkIndex]
            boundaryEmiss = surfEmiss[linkIndex]
            boundaryCAF = surfCAF[linkIndex]
            bc=ET.SubElement(module,'bc')                        
            bc.set('patch',interfaces[i])
            bc.set('type','radiate_intf')
            bc.set('emissivity',boundaryEmiss)                
                                                                                          
    indent(root)
    elapsed = time.time() - begin
    print ("Time taken to populate conditions: %.4f secs. Writing .spro now..." %(elapsed))
    tree.write(finalProject,encoding=xml_encoding)
    

elapsed = time.time() - begin
print ("Total time taken: %.4f secs" %(elapsed)) 
raw_input("Press enter to continue")  
