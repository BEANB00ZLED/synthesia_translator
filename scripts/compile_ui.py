import os
import subprocess


def compileUiFiles():
    scriptDir = os.path.dirname(os.path.abspath(__file__))
    projectRoot = os.path.dirname(scriptDir)
    uiDir = os.path.join(projectRoot, "ui")
    outputDir = uiDir
    uiFiles = [f for f in os.listdir(uiDir) if f.endswith(".ui")]

    for uiFile in uiFiles:
        baseName = os.path.splitext(uiFile)[0]
        inputPath = os.path.join(uiDir, uiFile)
        outputPath = os.path.join(outputDir, f"{baseName}.py")

        cmd = f"pyuic5 {inputPath} -o {outputPath}"
        try:
            subprocess.run(cmd, shell=True, check=True)
            print(f" Converted {uiFile} -> {baseName}.py")
        except subprocess.CalledProcessError as e:
            print(f" Error compiling {uiFile}: {e}")


if __name__ == "__main__":
    compileUiFiles()
