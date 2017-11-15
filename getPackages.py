import subprocess

def getAppXPackages():
    try:
        output = subprocess.check_output(["powershell.exe", "Get-AppXPackage"]
                                         , shell=True)
        return output.decode('UTF-8')
    except subprocess.CalledProcessError as e:
        print("subproces CalledProcessError.output = " + e.output)

print(getAppXPackages())
