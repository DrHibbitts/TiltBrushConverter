Tilt Brush Converter V0.1

Requirements:
- Tilt Brush
- Python 2.7
- Autodesk FBX Python SDK (http://images.autodesk.com/adsk/files/fbx20151_fbxpythonsdk_win.exe)
- PySide (pip install PySide if you don't have it)

Usage:
- Export some files from Tilt Brush
- Edit config.py to point at the relevant paths on your Computer
  - If your python is 64 bit use the _x64 autodesk folder otherwise use _x86
- Run TiltBrushConverter.py (This will eventually support FBX or OBJ, currently will just got to FBX mode)
- Select exported Tilt Brush files you want to convert
- Set the export options to your liking
- Hit the convert button at the bottom. All ticked files will be converted

ToDos:
- Allow custom naming schemes