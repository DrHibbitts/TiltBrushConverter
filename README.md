Tilt Brush Converter V0.1

General Requirements:
- Tilt Brush
- Python 2.7
- PySide (pip install PySide if you don't have it)

Required for FBX Export:
- Autodesk FBX Python SDK (http://images.autodesk.com/adsk/files/fbx20151_fbxpythonsdk_win.exe)

Usage:
- Export some files from Tilt Brush
- Edit config.py to point at the relevant paths on your Computer
  - If your python is 64 bit use the _x64 autodesk folder otherwise use _x86
- Run TiltBrushConverter.py
- Select the file type you want to convert to
- Select exported Tilt Brush files you want to convert
- Set the export options to your liking
- Hit the convert button at the bottom. All ticked files will be converted

ToDos:
- Allow custom naming schemes