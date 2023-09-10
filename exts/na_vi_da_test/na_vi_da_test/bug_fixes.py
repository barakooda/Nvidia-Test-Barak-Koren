
from pxr import UsdGeom, Vt


NEW_UVS = Vt.Vec2fArray([
            (0, 0), (1, 0), (1, 1), (0, 1),
            (1, 0), (1, 1), (0, 1), (0, 0),
            (1, 1), (0, 1), (0, 0), (1, 0),
            (0, 1), (0, 0), (1, 0), (1, 1),
            (0, 0), (1, 0), (1, 1), (0, 1),
            (1, 0), (1, 1), (0, 1), (0, 0)])

def fix_cube_uv(cube):
    mesh = UsdGeom.Mesh(cube)
    
    uv_attr = mesh.GetPrimvar('st')
    
    uv_primvar = UsdGeom.Primvar(uv_attr)
    
    uv_primvar.Set(NEW_UVS)
    