#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Inspired by code of Sam Calisch (http://www.mit.edu/~calisch/)

# kayak OpenSCAD model generation from table of offsets.

import argparse

parser = argparse.ArgumentParser(description="kayak OpenSCAD model generation from a table of offsets.")
parser.add_argument('--file', help='File containing offsets, Tab seperated, comment lines begin with `#`', required=True)
args = parser.parse_args()

def extrude(obj):
    return '{0}.extrude()'.format(obj)

def rotateX(obj,deg):
    return '{0}.rotateX({1})'.format(obj,deg)

def translateY(obj,offset):
    return '{0}.translate([0,{1},0])'.format(obj,260-offset)
def union(obj1,obj2):
    return 'union({0},{1})'.format(obj1,obj2)

class Section(object):

    def __init__(self, num, keel_hab, chine_hb, chine_hab, gunwale_hb, gunwale_hab, deckridge_hb, deckridge_hab, width=None):
        self.num = num

        self.keel_hb = 0.0
        self.keel_hab = float(keel_hab)

        self.chine_hb = float(chine_hb)
        self.chine_hab = float(chine_hab)

        self.gunwale_hb = float(gunwale_hb)
        self.gunwale_hab = float(gunwale_hab)

        self.deckridge_hb = float(deckridge_hb)
        self.deckridge_hab = float(deckridge_hab)

        if width:
            self.width = float(width)
        else:
            self.width = 1.0

    def __str__(self):
        return "Section({0},({1},{2}),({3},{4}),({5},{6}),({7},{8}),{9})".format(self.num,
                self.keel_hb,self.keel_hab,
                self.chine_hb,self.chine_hab,
                self.gunwale_hb,self.gunwale_hab,
                self.deckridge_hb,self.deckridge_hab,
                self.width)

    def jscad(self):
        """polygon(points=[
    [{0},{1}], // Keel
    [{2},{3}], // Positive Chine
    [{4},{5}], // Positive GunWale
    [{6},{7}], // Positive deck
    [-{6},{7}], // Negative deck
    [-{4},{5}], // Negative GunWale
    [-{2},{3}] // Negative Chine
    // And back to the keel ])"""
        # Is the deck a ridge or a flat surface?
        if self.deckridge_hab:
            # There is a deckridge
            if self.deckridge_hb:
                # there is a HalfBreadth for the deckridge, so it's 2 points, not 1 point.
                tmpl="""CAG.fromPoints(\n[ [{0},{1}], [{2},{3}], [{4},{5}], [{6},{7}], [-{6},{7}], [-{4},{5}], [-{2},{3}] ]\n)"""
            else:
                # no deckridge HalfBreadth, so it's 1 point.
                tmpl="""CAG.fromPoints(\n[ [{0},{1}], [{2},{3}], [{4},{5}], [{6},{7}], [-{4},{5}], [-{2},{3}] ]\n)"""
        else:
            # No deckridge
            tmpl="""CAG.fromPoints(\n[ [{0},{1}], [{2},{3}], [{4},{5}], [-{4},{5}], [-{2},{3}] ]\n)"""

        return tmpl.format(
                self.keel_hb,self.keel_hab,
                self.chine_hb,self.chine_hab,
                self.gunwale_hb,self.gunwale_hab,
                self.deckridge_hb,self.deckridge_hab,
                )


class Coaming(object):
	def __init__(self,length,beam,spacing,points,width1,width2):
		self.length = length
		self.beam = beam
		self.spacing = spacing
		self.points = points
		self.width1 = width1
		self.width2 = width2


class Kayak(object):
    def __init__(self,name,sections,spacing,coaming=None):
        self.name = name
        self.sections = sections
        self.spacing = spacing
        self.coaming = coaming

    def jscad(self):
        render=None
        for sec,offset in zip(self.sections,self.spacing[1:-1]):
            if render:
                render=union(render,translateY(rotateX(extrude(sec.jscad()),90),offset))
            else:
                render=translateY(rotateX(extrude(sec.jscad()),90),offset)

        return render



if __name__ == '__main__':
    print "start"
    sections=[];
    with open(args.file) as table:
        for line in table:
            if line.startswith('#'):
                continue
            elif line.startswith('Spacing:'):
                spacers=map(float,line.split(':',2)[1].strip().split(','))
            elif line.startswith('Name:'):
                name=line.split(':',2)[1].strip()
            else:
                sections.append(Section(*line.rstrip().split("\t")))
    kayak = Kayak(name,sections,spacers)
    print kayak.jscad()
    print "end"

# vim: set filetype=python ts=4 sw=4 et si tw=100
