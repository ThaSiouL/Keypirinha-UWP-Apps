import ctypes
import os
import subprocess
import xml.etree.cElementTree as ET
import timeit


"""
Documetation:
The CMDlet Get-AppXPackage is called and the output is used

DLL Call:
https://msdn.microsoft.com/en-us/library/windows/desktop/bb759919(v=vs.85).aspx
HRESULT SHLoadIndirectString(
  _In_	   PCWSTR pszSource, #Input example: @{Microsoft.Camera_6.2.8376.0_x64__8wekyb3d8bbwe? ms-resource://Microsoft.Camera/resources/manifestAppDescription}
  _Out_	  PWSTR  pszOutBuf, #Emtpy Pointer Filled during excecution
  _In_	   UINT   cchOutBuf, #lengh of Pointer.
  _Reserved_ void   **ppvReserved #Reserved, currently null
); # Should return 0 (H_OK Signal)
"""

H_OK = 0
SHLWAPIDLL = ctypes.WinDLL("shlwapi.dll")


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
		print(format(self.displayName))

def getAppXPackagesRaw():
	try:
		output = subprocess.check_output(["powershell.exe", "Get-AppXPackage"]
										, shell=True)
		return output.decode('UTF-8')
	except subprocess.CalledProcessError as err:
		print("subproces CalledProcessError.output = " + err.output.decode(encoding='utf-8'))

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
	appXPackage.name = root.find('./' + namespace +'Identity').get('Name')
	for tag in root.findall('./' + namespace + 'Properties/' + namespace + 'DisplayName'):
		appXPackage.displayName = formatResourceText(appXPackage, tag.text)

def formatResourceText(appXPackage,resourceText):
	if resourceText[0:12] == 'ms-resource:':
		prefix = resourceText[0:12]
		key = resourceText[12:]
		if key[0:2] == "//":
			parsed = prefix + key
		elif key[0:1] == "/":
			parsed = prefix + "//" + key
		elif key.find('/') != -1:
			parsed = prefix + "/" + key
		else:
			parsed = prefix + "///resources/" + key
		return(readPriPackage(appXPackage ,'@{{{}\\resources.pri? {}}}'.format(appXPackage.installLocation,parsed)))
	else:
		return(resourceText)

def readPriPackage(appXPackage, resourceText):
	BufferLength = 500
	inputBuffer = ctypes.create_unicode_buffer(
		resourceText, BufferLength)
	inputPointer = ctypes.pointer(inputBuffer)
	outputBuffer = ctypes.create_unicode_buffer(BufferLength)
	outputPointer = ctypes.pointer(outputBuffer)
	H_Status = SHLWAPIDLL.SHLoadIndirectString(inputPointer,outputPointer,ctypes.c_int(BufferLength) ,0)
	if H_Status == H_OK:
		result = outputBuffer.value
		return(result)
	#TODO: Handle Errors

def getPicture(appXpackage):
	pass

rawPackages = getAppXPackagesRaw().split("\r\n\r\n")
appXPackages = []
for rawPackage in rawPackages:
	rawPackage = rawPackage.split("\r\n")
	if 17 <= len(rawPackage) <= 19:
		appXPackages.append(AppXPackage(rawPackage))
