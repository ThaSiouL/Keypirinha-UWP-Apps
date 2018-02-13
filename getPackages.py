import ctypes
import os
import subprocess
import xml.etree.cElementTree as ET


"""
Docume

DLL Call:
HRESULT SHLoadIndirectString(
  _In_       PCWSTR pszSource, #Input example: @{Microsoft.Camera_6.2.8376.0_x64__8wekyb3d8bbwe? ms-resource://Microsoft.Camera/resources/manifestAppDescription}
  _Out_      PWSTR  pszOutBuf, #Emtpy Pointer Filled during excecution
  _In_       UINT   cchOutBuf, #lengh of Pointer.
  _Reserved_ void   **ppvReserved #Reserved, currently null
); # Returns positive if
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
		#print(self.installLocation)
		readPackageManifest(self)

def getAppXPackagesRaw():
	try:
		output = subprocess.check_output(["powershell.exe", "Get-AppXPackage"]
										, shell=True)
		return output.decode('UTF-8')
	except subprocess.CalledProcessError as err:
		print("subproces CalledProcessError.output = " + err.output)

def readPackageManifest(appXPackage):
	manifestPath = r'\AppxManifest.xml'
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
	for a in root.findall('./' + namespace + 'Properties/' + namespace + 'DisplayName'):
		if a.text[0:12] == 'ms-resource:':
			readPriPackage(appXPackage ,a.text)
		else:
			print(a.text)

def readPriPackage(appXPackage, resourceText):
	SHLWAPIDLL = ctypes.WinDLL("C:\\Windows\\System32\\shlwapi.dll")

	# SHLoadIndirectStringProto = ctypes.WINFUNCTYPE(
	# 				ctypes.c_bool,
	# 				ctypes.c_wchar_p,
	# 				ctypes.POINTER(ctypes.c_wchar_p),
	# 				ctypes.c_uint,
	# 				ctypes.c_void_p)

	inputString = ctypes.c_wchar_p('@{' + appXPackage.installLocation + '\resources.pri? ' + resourceText + '}')
	inputPointer = ctypes.pointer(inputString)
	pBuf = ctypes.create_string_buffer(50)
	pPoint = ctypes.pointer(pBuf)
	Test = SHLWAPIDLL.SHLoadIndirectString(inputPointer,pPoint,50,0)
	print(Test ,repr(pPoint.contents.value))


rawPackages = getAppXPackagesRaw().split("\r\n\r\n")
appXPackages = []
for rawPackage in rawPackages:
	rawPackage = rawPackage.split("\r\n")
	if 17 <= len(rawPackage) <= 19:
		appXPackages.append(AppXPackage(rawPackage))
		# RawPackageList.append(rawPackage)


# print(RawPackageList)
