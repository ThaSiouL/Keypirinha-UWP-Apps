import subprocess
import os
import ctypes

"""
Docume
"""

SHLWAPIDLL = ctypes.WinDLL("C:\\Windows\\System32\\shlwapi.dll")

SHLoadIndirectStringProto = ctypes.WINFUNCTYPE(
				ctypes.c_wchar_p,
				ctypes.c_wchar_p,
				ctypes.c_uint,
				ctypes.c_void_p)

class AppXPackage:
	def __init__(self, rawPackageElement):
		elems = [[ell.strip() for ell in el.split(" : ")]
											for el in rawPackageElement if el.count(" : ") == 1]
		elemDict = dict(el for el in elems)
		self.framework = elemDict.get('isFramework')
		self.resourcePackage = elemDict.get('isResourcePackage')
		self.packageFamilyName = elemDict.get('PackageFamilyName')
		self.installLocation = elemDict.get('InstallLocation')
		print(self.installLocation)





def getAppXPackagesRaw():
	try:
		output = subprocess.check_output(["powershell.exe", "Get-AppXPackage"]
										, shell=True)
		return output.decode('UTF-8')
	except subprocess.CalledProcessError as err:
		print("subproces CalledProcessError.output = " + err.output)

rawPackages = getAppXPackagesRaw().split("\r\n\r\n")
appXPackages = []
for rawPackage in rawPackages:
	rawPackage = rawPackage.split("\r\n")
	if 17 <= len(rawPackage) <= 19:
		appXPackages.append(AppXPackage(rawPackage))
		# RawPackageList.append(rawPackage)


# print(RawPackageList)
