import ctypes
import os
import subprocess
import xml.etree.cElementTree as ET


"""
Documetation:
The CMDlet Get-AppXPackage is called and the output is used

DLL Call:
https://msdn.microsoft.com/en-us/library/windows/desktop/bb759919(v=vs.85).aspx
HRESULT SHLoadIndirectString(
  _In_       PCWSTR pszSource, #Input example: @{Microsoft.Camera_6.2.8376.0_x64__8wekyb3d8bbwe? ms-resource://Microsoft.Camera/resources/manifestAppDescription}
  _Out_      PWSTR  pszOutBuf, #Emtpy Pointer Filled during excecution
  _In_       UINT   cchOutBuf, #lengh of Pointer.
  _Reserved_ void   **ppvReserved #Reserved, currently null
); # Should return 0 (H_OK Signal)
"""



class AppXPackage:
	def __init__(self, rawPackageElement):
		elems = [[ell.strip() for ell in el.split(" : ")]
											for el in rawPackageElement if el.count(" : ") == 1]
		elemDict = dict(el for el in elems)
		self.framework = elemDict.get('isFramework')
		self.resourcePackage = elemDict.get('isResourcePackage')
		self.packageFamilyName = elemDict.get('PackageFamilyName')
		self.installLocation = elemDict.get('InstallLocation')
		self.displayNameRaw = ''
		self.displayName = ''
		self.name = ''
		#print(self.installLocation)
		readPackageManifest(self)
		print(self.displayName +'\r\n')

def getAppXPackagesRaw():
	try:
		output = subprocess.check_output(["powershell.exe", "Get-AppXPackage"]
										, shell=True)
		return output.decode('UTF-8')
	except subprocess.CalledProcessError as err:
		print("subproces CalledProcessError.output = " + err.output)

def readPackageManifest(appXPackage):
	manifestPath = '\\AppxManifest.xml'
	def getNamespace(name):
		if name[0] == "{":
			uri, tag = name[1:].split("}")
			return '{'+uri+'}'
		else:
			return ''

	tree = ET.parse(appXPackage.installLocation + manifestPath)
	root = tree.getroot()
	namespace = getNamespace(root.tag)
	print('new Line: ' + root.tag+ ' ' + appXPackage.installLocation)
	appXPackage.name = root.find('./' + namespace +'Identity').get('Name')
	for tag in root.findall('./' + namespace + 'Properties/' + namespace + 'DisplayName'):
		appXPackage.displayName = formatResourceText(appXPackage, tag.text)

def formatResourceText(appXPackage,resourceText):
	if resourceText[0:12] == 'ms-resource:':
		return(readPriPackage(appXPackage ,resourceText[0:12]+'//'+ appXPackage.name +'/resources/'+resourceText[12:]))
	else:
		return(resourceText)

def readPriPackage(appXPackage, resourceText):
	SHLWAPIDLL = ctypes.WinDLL("C:\\Windows\\System32\\shlwapi.dll")
	BufferLength = 500
	print(resourceText)
	inputBuffer = ctypes.create_string_buffer(bytes('@{' + appXPackage.installLocation + '\\resources.pri? ' + resourceText + '}','utf-8'), BufferLength)
	inputPointer = ctypes.pointer(inputBuffer)
	outputBuffer = ctypes.create_string_buffer(BufferLength)
	outputPointer = ctypes.pointer(outputBuffer)
	H_Status = SHLWAPIDLL.SHLoadIndirectString(inputPointer,outputPointer,ctypes.c_int(BufferLength) ,0)
	if H_Status == 0:
		result = ''.join([s.decode("utf-8") for s in outputPointer.contents if s != b'\x00'])
		return(result)

rawPackages = getAppXPackagesRaw().split("\r\n\r\n")
appXPackages = []
for rawPackage in rawPackages:
	rawPackage = rawPackage.split("\r\n")
	if 17 <= len(rawPackage) <= 19:
		appXPackages.append(AppXPackage(rawPackage))
