#!/usr/bin/env python

# Copyright 2016 Google Inc. All Rights Reserved.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#         http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This is sample Python 2.7 code to convert Tilt Brush export files
to .obj format.    There are various possible ways you might want it
converted:

- Should the entire sketch be converted to a single mesh? Or all
    strokes that use the same brush? Or maybe one mesh per stroke?
- Should backfaces be kept or removed?
- Should vertices be welded? How aggressively?

This sample keeps backfaces, merges all strokes into a single mesh,
and does no vertex welding. It can also be easily customized to do any
of the above."""

import argparse
import os
import sys
import config

def iter_tiltbrush_paths():
    import config
    yield r"C:\src\tb"
    yield config.tiltBrushInstallDir
    import _winreg, re
    base = _winreg.QueryValueEx(
        _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam"), "SteamPath")[0]
    yield os.path.join(base, "steamapps/common/Tilt Brush")
    try: config = file(os.path.join(base, "config/config.vdf")).read()
    except IOError: config = ""
    for match in re.finditer(r'"BaseInstallFolder_\d+"\s+"(.*?)"', config):
        yield os.path.join(match.group(1), "Tilt Brush")
for path in iter_tiltbrush_paths():
    sys.path.append(os.path.join(path, "Support"))

from tbdata.export import iter_meshes, TiltBrushMesh, SINGLE_SIDED_FLAT_BRUSH

def write_obj(mesh, outf_name):
    """Emit a TiltBrushMesh as a .obj file"""
    from cStringIO import StringIO
    tmpf = StringIO()

    for v in mesh.v:
        tmpf.write("v %f %f %f\n" % v)

    has_uv = any(uv is not None for uv in mesh.uv0)
    if has_uv:
        has_uv = True
        for uv in mesh.uv0:
            if uv is not None:
                tmpf.write("vt %f %f\n" % (uv[0], uv[1]))
            else:
                tmpf.write("vt 0 0\n")

    has_n = any(n is not None for n in mesh.n)
    if has_n:
        for n in mesh.n:
            if n is not None:
                tmpf.write("vn %f %f %f\n" % n)
            else:
                tmpf.write("vn 0 0 0\n")

    if has_n and has_uv:
        for (t1, t2, t3) in mesh.tri:
            t1 += 1; t2 += 1; t3 += 1
            tmpf.write("f %d/%d/%d %d/%d/%d %d/%d/%d\n" % (t1,t1,t1, t2,t2,t2, t3,t3,t3))
    elif has_n:
        for (t1, t2, t3) in mesh.tri:
            t1 += 1; t2 += 1; t3 += 1
            tmpf.write("f %d//%d %d//%d %d//%d\n" % (t1,t1, t2,t2, t3,t3))
    elif has_uv:
        for (t1, t2, t3) in mesh.tri:
            t1 += 1; t2 += 1; t3 += 1
            tmpf.write("f %d/%d %d/%d %d/%d\n" % (t1,t1, t2,t2, t3,t3))
    else:
        for (t1, t2, t3) in mesh.tri:
            t1 += 1; t2 += 1; t3 += 1
            tmpf.write("f %d %d %d\n" % (t1, t2, t3))


    with file(outf_name, 'wb') as outf:
        outf.write(tmpf.getvalue())

def convertFile(files, cooked):
    filename, output_filename = files
    meshes = list(iter_meshes(filename))
    for mesh in meshes:
        mesh.remove_degenerate()

    if cooked:
        for mesh in meshes:
            if mesh.brush_guid in SINGLE_SIDED_FLAT_BRUSH:
                mesh.add_backfaces()
        mesh = TiltBrushMesh.from_meshes(meshes)
        mesh.collapse_verts(ignore=('uv0', 'uv1', 'c', 't'))
        mesh.remove_degenerate()
    else:
        mesh = TiltBrushMesh.from_meshes(meshes)

    write_obj(mesh, output_filename)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Sample script to convert raw Tilt Brush geometry .obj format.")
    parser.add_argument('filename', help="Exported .json files to convert to obj")
    parser.add_argument('--cooked', action='store_true', dest='cooked', default=True,
                                            help="(default) Strip geometry of normals, weld verts, and give single-sided triangles corresponding backfaces.")
    parser.add_argument('--raw', action='store_false', dest='cooked',
                                            help="Emit geometry just as it comes from Tilt Brush. Depending on the brush, triangles may not have backfaces, adjacent triangles will mostly not share verts.")
    parser.add_argument('-o', dest='output_filename', metavar='FILE',
                                            help="Name of output file; defaults to <filename>.obj")
    args = parser.parse_args()
    if args.output_filename is None:
        args.output_filename = os.path.splitext(args.filename)[0] + '.obj'

    convertFile((args.filename, args.output_filename), cooked=args.cooked)
    print "Wrote", args.output_filename


if __name__ == '__main__':
    main()
