"""Independent five-parameter anime hair-card geometry.
Each station stores XYZ position, width, and thickness. Inspired by the
published CHARM representation; no CHARM source code or neural dependencies.
"""
from __future__ import annotations
from math import sqrt
from typing import Iterable, Sequence

Vec3 = tuple[float, float, float]
Face = tuple[int, ...]

def _add(a: Vec3, b: Vec3) -> Vec3:
    return (a[0]+b[0], a[1]+b[1], a[2]+b[2])

def _sub(a: Vec3, b: Vec3) -> Vec3:
    return (a[0]-b[0], a[1]-b[1], a[2]-b[2])

def _mul(a: Vec3, s: float) -> Vec3:
    return (a[0]*s, a[1]*s, a[2]*s)

def _dot(a: Vec3, b: Vec3) -> float:
    return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]

def _cross(a: Vec3, b: Vec3) -> Vec3:
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])

def _length(a: Vec3) -> float:
    return sqrt(_dot(a,a))

def _normalize(v: Vec3, fallback: Vec3=(1.0,0.0,0.0)) -> Vec3:
    n=_length(v)
    return _mul(v,1.0/n) if n>1.0e-10 else fallback

def _catmull_rom(points: Sequence[Vec3], steps: int) -> list[Vec3]:
    if len(points)<2 or steps<1:
        raise ValueError("a hair path needs at least two points and positive sampling")
    out=[]
    for i in range(len(points)-1):
        p0=points[max(0,i-1)]; p1=points[i]; p2=points[i+1]; p3=points[min(len(points)-1,i+2)]
        for j in range(steps):
            t=j/steps; t2=t*t; t3=t2*t
            out.append(tuple(0.5*(2*p1[k]+(-p0[k]+p2[k])*t+(2*p0[k]-5*p1[k]+4*p2[k]-p3[k])*t2+(-p0[k]+3*p1[k]-3*p2[k]+p3[k])*t3) for k in range(3)))
    out.append(tuple(points[-1]))
    return out

def hair_card_mesh(control_points: Sequence[Sequence[float]], *, face_hint: Vec3=(0.0,1.0,0.0), samples_per_segment: int=2) -> tuple[list[Vec3],list[Face]]:
    """Build a tapered closed low-poly lock from XYZ + width + thickness stations."""
    if len(control_points)<3:
        raise ValueError("a hair card requires at least three control points")
    points=[tuple(float(v) for v in p) for p in control_points]
    if any(len(p)!=5 for p in points):
        raise ValueError("each hair point must contain x, y, z, width, thickness")
    if any(not all(abs(v)<1.0e6 for v in p) for p in points):
        raise ValueError("hair control points must be finite and bounded")
    if any(w<=0.0 or d<=0.0 for _,_,_,w,d in points):
        raise ValueError("hair width and thickness must remain positive")
    if samples_per_segment<1:
        raise ValueError("samples_per_segment must be positive")
    centers=_catmull_rom([p[:3] for p in points],samples_per_segment)
    widths=[]; depths=[]
    for i in range(len(points)-1):
        for j in range(samples_per_segment):
            t=j/samples_per_segment
            widths.append(points[i][3]*(1-t)+points[i+1][3]*t)
            depths.append(points[i][4]*(1-t)+points[i+1][4]*t)
    widths.append(points[-1][3]); depths.append(points[-1][4])
    if len(face_hint) != 3:
        raise ValueError("face_hint must be an XYZ vector")
    hint=_normalize(tuple(float(v) for v in face_hint),(0.0,1.0,0.0))
    rings=[]; previous_width=None
    for i,center in enumerate(centers):
        before=centers[max(0,i-1)]; after=centers[min(len(centers)-1,i+1)]
        tangent=_normalize(_sub(after,before),(0.0,0.0,-1.0))
        if previous_width is None:
            width_axis=_cross(tangent,hint)
            if _length(width_axis)<1.0e-7:
                fallback=(1.0,0.0,0.0) if abs(tangent[0])<0.85 else (0.0,1.0,0.0)
                width_axis=_cross(tangent,fallback)
            width_axis=_normalize(width_axis)
        else:
            projected=_sub(previous_width,_mul(tangent,_dot(previous_width,tangent)))
            if _length(projected)<1.0e-7:
                projected=_cross(tangent,hint)
            width_axis=_normalize(projected,previous_width)
            if _dot(width_axis,previous_width)<0.0:
                width_axis=_mul(width_axis,-1.0)
        depth_axis=_normalize(_cross(width_axis,tangent),hint)
        previous_width=width_axis
        hw=widths[i]*0.5; hd=depths[i]*0.5
        rings.append([
            _add(_add(center,_mul(width_axis,hw)),_mul(depth_axis,hd)),
            _add(_sub(center,_mul(width_axis,hw)),_mul(depth_axis,hd)),
            _sub(_sub(center,_mul(width_axis,hw)),_mul(depth_axis,hd)),
            _add(_sub(center,_mul(width_axis,-hw)),_mul(depth_axis,-hd)),
        ])
    vertices=[v for ring in rings for v in ring]
    faces=[]
    for i in range(len(rings)-1):
        a=i*4; b=(i+1)*4
        for k in range(4):
            n=(k+1)%4
            faces.append((a+k,a+n,b+n,b+k))
    faces.append((3,2,1,0))
    end=(len(rings)-1)*4
    faces.append((end,end+1,end+2,end+3))
    volume6=0.0
    for face in faces:
        anchor=vertices[face[0]]
        for j in range(1,len(face)-1):
            volume6+=_dot(anchor,_cross(vertices[face[j]],vertices[face[j+1]]))
    if volume6<0.0:
        faces=[tuple(reversed(face)) for face in faces]
    return vertices,faces

def build_hair_cards(cards: Iterable[dict], *, samples_per_segment: int=2) -> list[tuple[str,list[Vec3],list[Face]]]:
    """Build named cards; each record has name, control_points, and face_hint."""
    output=[]
    for index,card in enumerate(cards):
        name=str(card.get("name",f"HairCard_{index:02d}"))
        hint=tuple(card.get("face_hint",(0.0,1.0,0.0)))
        if len(hint)!=3:
            raise ValueError(f"{name}: face_hint must be XYZ")
        vertices,faces=hair_card_mesh(card["control_points"],face_hint=hint,samples_per_segment=samples_per_segment)
        output.append((name,vertices,faces))
    return output
