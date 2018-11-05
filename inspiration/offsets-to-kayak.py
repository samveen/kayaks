#!/usr/bin/env python
#Sam Calisch, calisch@mit.edu, 2012
#Single chined kayak cutfile generation from table of offsets.
# http://fab.cba.mit.edu/classes/863.12/people/calisch/8/week8.html

from __future__ import division
import rhinoscriptsyntax as rs
from math import *
from convenience import *

def lengths(objs):
	t = 0
	for obj in objs:
		t+=rs.CurveLength(obj)
	return t

def SetupLayers():
	rs.AddLayer ("frames", green)
	rs.AddLayer ("seams", blue)
	rs.AddLayer ("layout", magenta)

def draw_frame(s):
	objs=[]
	objs.append(rs.AddLine([s.section,0,s.keel_hab],[s.section,s.chine_hb,s.chine_hab]))
	objs.append(rs.AddLine([s.section,s.chine_hb,s.chine_hab],[s.section,s.gunwale_hb,s.gunwale_hab]))
	objs.append(rs.AddLine([s.section,s.gunwale_hb,s.gunwale_hab],[s.section,s.deckridge_hb,s.deckridge_hab]))
	if(s.deckridge_hb != 0):
		objs.append(rs.AddLine([s.section,s.deckridge_hb,s.deckridge_hab],[s.section,0.,s.deckridge_hab]))
	rs.MirrorObjects(objs,[0,0,0],[1,0,0],copy=True)	

def make_chine_edge(p1,p2,wc,wg,l1,l2,p_top):
	objs = []
	l = normalized(sd(p2,p1))
	p = sm(wc,unit_perp(l,[1,0,0]))
	p3 = sd(ss(p1,sm(l1,l)),p)
	p4 = sd(sd(p2,sm(l2,l)),sm(wg/wc,p))

	up = normalized(sd(p_top,p2))
	if up[2]==0:
		p2 = sd(p2,[0,sqrt(wg**2+(l1*l[1])**2),0])
	else:
		t = ((p2[1]-p4[1])/up[1] - (p2[2]-p4[2])/up[2])/(l[1]/up[1] - l[2]/up[2])
		p2 = ss(p4,sm(t,l))

	p1 = sd(p1,p)
#	p2 = sd(p2,[0,(wg/wc)*p[1],0])
#	p2 = sd(p2,[0,sqrt(wg**2+(l2*l[1])**2),0])
	objs.append(rs.AddLine(p1,ss(p1,sm(l1,l))))
	objs.append(rs.AddLine(p3,ss(p,p3)))
	objs.append(rs.AddLine(p2,p4))
	objs.append(rs.AddLine(p4,ss(sm(wg/wc,p),p4)))
	p5 = mid(p1,p2)
	objs.append(rs.AddArc3Pt(ss(p,p3),ss(sm(wg/wc,p),p4),p5))
	return rs.JoinCurves(objs,delete_input=True)

def make_deck_edge(p1,p2,wd,wg,l,p3,deck_string_place):
	objs = []
	slope = (p2[2]-p1[2])/(p2[1]-p1[1])
	up = sd(p2,p1)	
	ll = normalized(sd(p1,p3))
	p = sm(wg,unit_perp(ll,[1,0,0]))
	p4 = sd(sd(p1,sm(l,ll)),p)

#	p1 = sd(p1,[0,p[1],0])
	if slope==0:
		p1 = sd(p1,[0,sqrt(wg**2+(l*ll[1])**2),0])
	else:
		t = ((p1[1]-p4[1])/up[1] - (p1[2]-p4[2])/up[2])/(ll[1]/up[1] - ll[2]/up[2])
		p1 = ss(p4,sm(t,ll))
	if deck_string_place:
		if(p2[1]!=0):
			objs.append(rs.AddLine(p2,[p2[0],0,p2[2]]))
		#assume deck_string_place is outside p2[1]
		topside = [p2[0],deck_string_place-.5*wd,  p2[2] + slope*(deck_string_place-.5*wd-p2[1]) ]
		drop = slope*wd
		objs.append(rs.AddLine(p2,topside))
		objs.append(rs.AddLine(topside,ss(topside,[0,0,-l+.5*drop])))
		objs.append(rs.AddLine(ss(topside,[0,0,-l+.5*drop]),ss(topside,[0,wd,-l+.5*drop])))
		objs.append(rs.AddLine(ss(topside,[0,wd,-l+.5*drop]),ss(topside,[0,wd,drop])))
		objs.append(rs.AddLine(ss(topside,[0,wd,drop]),p1))
	else:
		if(p2[1]==0):
			objs.append(rs.AddLine(p1,p2))
		else:
			objs.append(rs.AddLine(p1,p2))
			objs.append(rs.AddLine([p2[0],p2[1],p2[2]],[p2[0],0,p2[2]]))
	return objs

def make_floor_board(b):
	l = b.tof[4].section - b.tof[3].section - .5/12
	rs.AddRectangle([0,0,0],l,2./12)

def x_rectangle_cut_out(p,width,height,w_i,h_i):
	objs = []
	objs.append(rs.AddLine(p,ss(p,[0,.5*width,0])))
	objs.append(rs.AddLine(ss(p,[0,.5*width,0]),ss(p,[0,.5*width,height])))
	objs.append(rs.AddLine(ss(p,[0,.5*width,height]),ss(p,[0,.5*w_i,height])))
	objs.append(rs.AddLine(ss(p,[0,.5*w_i,height]),ss(p,[0,.5*w_i,height-h_i])))
	objs.append(rs.AddLine(ss(p,[0,.5*w_i,height-h_i]),ss(p,[0,0,height-h_i])))
	objs.extend(rs.MirrorObjects(objs,p,ss(p,[1,0,0]),copy=True))
	return rs.JoinCurves(objs,delete_input=True)


def make_jigs(b,diam,bdiam):
	jig_base_height = 4./12
	jig_clearance = .25/12

#	for s in [b.tof[i] for i in [0,2,5,7]]:
	for s in b.tof:
		r = 90

		width = 5*b.deckString.thickness
		height = s.keel_hab+ 2*b.deckString.width + jig_base_height
		p = [s.section,0,0]
		rect = x_rectangle_cut_out(p,width,height, b.deckString.thickness+2*jig_clearance, height-jig_base_height+jig_clearance+b.deckString.width)
		rect = [rs.MoveObject(rect,[0,0,-jig_base_height])]
		plane = rs.PlaneFromNormal([s.section,0,0],[1,0,0])
		holes = [rs.MoveObject(rs.AddCircle(plane,diam/2),[0,1.5*b.deckString.thickness,s.keel_hab+b.deckString.width])]
		holes.extend(rs.MirrorObjects(holes,p,ss(p,[1,0,0]),copy=True))
		bhole = rs.MoveObject(rs.AddCircle(plane,bdiam/2),[0,0,47./64/12-jig_base_height])
		holes.extend([bhole,rs.CopyObject(bhole,[0,0,1.5/12])])
		rs.RotateObjects(rect+holes,p,90,[0,1,0])

def make_keel_edge(p1,p2,w,l,p3):
	objs = []
	p1 = ss(p1,[0,0,l])
	ll = normalized(sd(p3,p2))
	p = sm(w,unit_perp(ll,[1,0,0]))
	p2 = sd(p2,p)
	v = normalized(sd(ss(p1,[0,.5*w,-l]),p2))
	objs.append(rs.AddLine(p1,ss(p1,[0,.5*w,0])))	
	p3 = ss(p1,[0,.5*w,-l])
	objs.append(rs.AddLine(ss(p1,[0,.5*w,0]),p3))
#	objs.append(rs.AddArcPtTanPt(p2,v,p3))
	objs.append(rs.AddInterpCurve([p2,p3],degree=3,knotstyle=0,start_tangent=v,end_tangent=[0,v[1],0]))
	return objs


def make_stem_pieces(b):
	obj1 = []
	h = (b.tof[0].chine_hab - b.tof[1].chine_hab)*(b.tof[0].section-b.chine)/(b.tof[1].section - b.tof[0].section ) + b.tof[0].chine_hab 
	p1 = [b.chine,0,h]
	obj1.append(rs.AddLine([0,0,b.bow],p1))
	obj1.append(rs.AddLine([0,0,b.bow],[b.stem_width,0,b.bow]))
	obj1.append(rs.AddLine([b.stem_width,0,b.bow],ss(p1,[b.stem_width,0,0])))
	obj1.append(rs.AddLine(ss(p1,[b.stem_width,0,0]),p1))
	obj1 = rs.MoveObjects(rs.JoinCurves(obj1,delete_input=True),sm(-1,p1))


	obj2 = []
	h = (b.tof[-1].chine_hab - b.tof[-2].chine_hab)*(b.loa-b.aft-b.tof[-1].section)/(b.tof[-1].section - b.tof[-2].section ) + b.tof[-1].chine_hab 
	p2 = [b.loa-b.aft,0, h]
	obj2.append(rs.AddLine([b.loa,0,b.stern], p2))
	obj2.append(rs.AddLine([b.loa,0,b.stern], [b.loa-b.stem_width,0,b.stern]))
	obj2.append(rs.AddLine([b.loa-b.stem_width,0,b.stern], ss(p2,[-b.stem_width,0,0])))
	obj2.append(rs.AddLine(ss(p2,[-b.stem_width,0,0]), p2))
	obj2 = rs.MoveObjects(rs.JoinCurves(obj2,delete_input=True),sm(-1,p2))

	return rs.RotateObjects(obj1+obj2,[0,0,0],90,[1,0,0])

def draw_frame_layout(s,keel_str,chine_str,gunwale_str,deck_str,diam,bdiam):
	objs=[]
	t = [0,2*s.gunwale_hb,0]
	r = 90
#	t = [0,0,0]
#	r = 0

	objs.append(rs.AddLine([s.section,0,s.keel_hab],[s.section,s.chine_hb,s.chine_hab]))
	objs.append(rs.AddLine([s.section,s.chine_hb,s.chine_hab],[s.section,s.gunwale_hb,s.gunwale_hab]))
	objs.append(rs.AddLine([s.section,s.gunwale_hb,s.gunwale_hab],[s.section,s.deckridge_hb,s.deckridge_hab]))
	if(s.deckridge_hb != 0):
		objs.append(rs.AddLine([s.section,s.deckridge_hb,s.deckridge_hab],[s.section,0.,s.deckridge_hab]))
	objs.extend(rs.MirrorObjects(objs,[0,0,0],[1,0,0],copy=True))
	objs = rs.JoinCurves(objs,delete_input=True)

	#ins = rs.OffsetCurve(objs,[s.section,0,.5*s.deckridge_hab],s.width + .75*deck_str.width,normal=[1,0,0])
#	if not ins: ins = []
	ins = []
	rs.DeleteObjects(objs)

	chine_edge = make_chine_edge([s.section,s.chine_hb,s.chine_hab],[s.section,s.gunwale_hb,s.gunwale_hab],chine_str.thickness, gunwale_str.thickness, chine_str.width, gunwale_str.width, [s.section,s.deckridge_hb,s.deckridge_hab])
	keel_edge = make_keel_edge([s.section,0,s.keel_hab],[s.section,s.chine_hb,s.chine_hab],keel_str.thickness, keel_str.width, [s.section,s.gunwale_hb,s.gunwale_hab])
	deck_edge = make_deck_edge([s.section,s.gunwale_hb,s.gunwale_hab],[s.section,s.deckridge_hb,s.deckridge_hab],deck_str.thickness, gunwale_str.thickness,deck_str.width, [s.section,s.chine_hb,s.chine_hab],s.deck_string_place)

	edges = chine_edge+keel_edge+deck_edge
	edges.extend(rs.MirrorObjects(edges,[0,0,0],[1,0,0],copy=True))
	edges = rs.JoinCurves(edges,delete_input=True)
	edges.extend(rs.OffsetCurve(edges,[s.section,0,.5*s.deckridge_hab],s.width,normal=[1,0,0],style=3))
	g = rs.AddGroup()
	rs.AddObjectsToGroup(edges,g)

#	if s.num-1 in [0,2,5,7]:
	if 1:
		p = [s.section,0,0]
		plane = rs.PlaneFromNormal(p,[1,0,0])
		holes = [rs.MoveObject(rs.AddCircle(plane,diam/2),[0,1.5*deck_str.thickness,s.keel_hab+deck_str.width])]
		holes.extend(rs.MirrorObjects(holes,p,ss(p,[1,0,0]),copy=True))
	else:
		holes = []

	rs.MoveObjects(rs.RotateObjects(ins+edges+holes,[s.section,0,s.keel_hab],r,[0,1,0]),t)


def draw_keel(b):
	objs = []
	for i in range(len(b.tof)-1):
		p1 = [b.tof[i].section,0,b.tof[i].keel_hab]
		p2 = [b.tof[i+1].section,0,b.tof[i+1].keel_hab]
		objs.append(rs.AddLine(p1,p2))
	h = (b.tof[0].chine_hab - b.tof[1].chine_hab)*(b.tof[0].section-b.chine)/(b.tof[1].section - b.tof[0].section ) + b.tof[0].chine_hab 
	p1 = [b.chine,0,h]
	objs.append(rs.AddLine(p1,[b.tof[0].section,0,b.tof[0].keel_hab]))
	objs.append(rs.AddLine([0,0,b.bow],p1))
	h = (b.tof[-1].chine_hab - b.tof[-2].chine_hab)*(b.loa-b.aft-b.tof[-1].section)/(b.tof[-1].section - b.tof[-2].section ) + b.tof[-1].chine_hab 
	p2 = [b.loa-b.aft,0, h]
	objs.append(rs.AddLine(p2,[b.tof[-1].section,0,b.tof[-1].keel_hab]))
	objs.append(rs.AddLine([b.loa,0,b.stern], p2))
	return lengths(objs)


def draw_chine(b):
	objs=[]
	for i in range(len(b.tof)-1):
		p1 = [b.tof[i].section,b.tof[i].chine_hb,b.tof[i].chine_hab]
		p2 = [b.tof[i+1].section,b.tof[i+1].chine_hb,b.tof[i+1].chine_hab]
		objs.append(rs.AddLine(p1,p2))
	h = (b.tof[0].chine_hab - b.tof[1].chine_hab)*(b.tof[0].section-b.chine)/(b.tof[1].section - b.tof[0].section ) + b.tof[0].chine_hab 
	p1 = [b.chine,0,h]
	objs.append(rs.AddLine(p1,[b.tof[0].section,b.tof[0].chine_hb,b.tof[0].chine_hab]))
	objs.append(rs.AddLine([0,0,b.bow],p1))
	h = (b.tof[-1].chine_hab - b.tof[-2].chine_hab)* (b.loa-b.aft - b.tof[-1].section) / (b.tof[-1].section-b.tof[-2].section ) + b.tof[-1].chine_hab
	p2 = [b.loa-b.aft,0,h]
	objs.append(rs.AddLine(p2,[b.tof[-1].section,b.tof[-1].chine_hb,b.tof[-1].chine_hab]))
	objs.append(rs.AddLine([b.loa,0,b.stern], p2))
	rs.MirrorObjects(objs,[0,0,0],[1,0,0],copy=True)
	return lengths(objs)

def draw_gunwale(b):
	objs=[]
	bf = 0
	for i in range(len(b.tof)-1):
		p1 = [b.tof[i].section,b.tof[i].gunwale_hb,b.tof[i].gunwale_hab]
		p2 = [b.tof[i+1].section,b.tof[i+1].gunwale_hb,b.tof[i+1].gunwale_hab]
		objs.append(rs.AddLine(p1,p2))
	objs.append(rs.AddLine([0,0,b.bow], [b.tof[0].section,b.tof[0].gunwale_hb,b.tof[0].gunwale_hab]))
	objs.append(rs.AddLine([b.loa,0,b.stern], [b.tof[-1].section,b.tof[-1].gunwale_hb,b.tof[-1].gunwale_hab]))
	rs.MirrorObjects(objs,[0,0,0],[1,0,0],copy=True)
	return lengths(objs)

def draw_coaming(c):
	pts = [[0,0,0]]
	half = [[(i+1)*c.spacing,c.points[i],0] for i in range(len(c.points))]
	pts.extend(half)
	pts.append([c.length,0,0])
	half = [[(i+1)*c.spacing,-c.points[i],0] for i in range(len(c.points))]
	half.reverse()
	pts.extend( half )
	pts.append([0,0,0])
	crv = rs.AddInterpCurve(pts,degree=3,knotstyle=0,start_tangent=[0,1,0],end_tangent=[0,1,0])
	strip = [crv,rs.OffsetCurve(crv,[-1,0,0],c.width1)]
	rs.CopyObjects(strip,[0,c.beam+2*c.width1,0])
	strip2 = [rs.CopyObjects(crv),rs.OffsetCurve(crv,[-1,0,0],c.width2)]
	rs.MoveObjects(strip2,[0,-c.beam-c.width1-c.width2,0])


class stringer(object):
	def __init__(self,width,thickness):
		self.width = width
		self.thickness = thickness

class station(object):
	def __init__(self,num,keel_hab, chine_hb, chine_hab, gunwale_hb, gunwale_hab, deckridge_hb, deckridge_hab,section,width,deck_string_place=None):
		self.num = num
		self.keel_hab = keel_hab
		self.chine_hb = chine_hb
		self.chine_hab = chine_hab
		self.gunwale_hb = gunwale_hb
		self.gunwale_hab = gunwale_hab
		self.deckridge_hb = deckridge_hb
		self.deckridge_hab = deckridge_hab
		self.section = section
		self.width = width
		self.deck_string_place = deck_string_place

class coaming(object):
	def __init__(self,length,beam,spacing,points,width1,width2):
		self.length = length
		self.beam = beam
		self.spacing = spacing
		self.points = points
		self.width1 = width1
		self.width2 = width2

class boat(object):
	def __init__(self,name,loa,chine,bow,peak,aft,stern,tof,coaming,keelString,chineString,gunwaleString,deckString,stem_width):
		self.name = name
		self.loa = loa
		self.chine = chine
		self.bow = bow
		self.peak = peak
		self.aft = aft
		self.stern = stern
		self.tof = tof
		self.coaming = coaming
		self.keelString = keelString
		self.chineString = chineString
		self.gunwaleString = gunwaleString
		self.deckString = deckString
		self.stem_width = stem_width

#sea_rider
#http://www.yostwerks.com/SeaRider1.html
tof =  [station(1,.124,.212,.251,.408,.718,0.,.718,2.5, 1.5/12),
	  	station(2,.060,.440,.183,.610,.637,0,.637,4.25, 1.5/12),
 		station(3,.019,.589,.138,.743,.578,0,.710,6.0, 1.5/12,.3),
 		station(4,.000,.665,.115,.811,.538,.2,.833,8.160, 1.5/12,.3),
 		station(5,.011,.639,.123,.788,.535,0,.535,10., 1.5/12,.4),
 		station(6,.041,.577,.147,.712,.549,0,.549,11.5, 1.5/12,.4),
 		station(7,.078,.421,.187,.585,.581,0,.581,13., 1.5/12),
 		station(8,.134,.233,.243,.408,.630,0,.630,14.5, 1.5/12)]

#inside dimensions at 35 mm intervals, forward to aft
pts = [77,108,131,147,160,172,184,191,198,201,203,200,192,180,145]
coam = coaming(56/2.54/12, 40.6/2.54/12, 3.5/2.54/12, [i/25.4/12 for i in pts],1./12,1.5/12)

if __name__ == '__main__':
	SetupLayers()
	keelString = stringer(1./12,.75/12)
	chineString = stringer(1./12,.75/12)
	gunwaleString = stringer(1.5/12,.75/12)
	deckString = stringer(1./12,.75/12)
	b = boat('Sea Rider',17.3, 16./12, 10.5/12, 10./12, 6.5/12, 9./12,tof,coam,keelString,chineString,gunwaleString,deckString,4./12)

	jig_hole_diam = 3./16./12.
	bracket_hole_diam = .328/12

	for i,station in enumerate(b.tof):
		rs.CurrentLayer('frames')
		draw_frame(station)
		rs.CurrentLayer('layout')
		draw_frame_layout(station,b.keelString,b.chineString,b.gunwaleString,b.deckString,jig_hole_diam, bracket_hole_diam)
	draw_coaming(b.coaming)
	make_stem_pieces(b)
	make_floor_board(b)
	make_jigs(b,jig_hole_diam, bracket_hole_diam)
	rs.CurrentLayer('seams')
	kbf = draw_keel(b)
	cbf = draw_chine(b)
	gbf = draw_gunwale(b)
	rs.MessageBox('keel board feet: %f \nchine board feet: %f \ngunwale board feet: %f \n\ntotal:%f'%(kbf,2*cbf,2*gbf, kbf+2*cbf+2*gbf))


