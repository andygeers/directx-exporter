#!BPY

""" Registration info for Blender menus:
Name: 'DirectX Exporter [with error handling] (.x)...'
Blender: 245
Group: 'Export'
Tip: 'Export to DirectX text file format format.'
"""
__author__ = "Arben (Ben) Omari"
__url__ = ("blender", "elysiun", "Author's site, http://www.omariben.too.it")
__version__ = "3.0"

__bpydoc__ = """\
This script exports a Blender mesh with armature to DirectX 9's text file
format.

Notes:<br>
    Check author's site or the elYsiun forum for a new beta version of the
DX exporter.
"""
# DirectXExporter.py version 3.0
# Copyright (C) 2006  Arben OMARI -- omariarben@everyday.com 
# Modified 2007 by Andy Geers -- andy.geers@googlemail.com
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# This script export meshes created with Blender in DirectX9 file format
# it exports meshes,armatures,materials,normals,texturecoords and animations

# Grab the latest official version here :www.omariben.too.it
# Grab Geero's latest version from www.geero.net

###########################################
#                                         #
#      Default Configuration Settings     #
#                                         #
###########################################

DEF_EXPORT_ANIMATIONS = 1
DEF_EXPORT_SHAPES     = 0
DEF_EXPORT_LIMITS     = 0
DEF_DEDUPLICATE       = 0
DEF_FLIP_NORMALS      = 0
DEF_SWAP_YZ           = 0
DEF_FLIP_Z            = 0
DEF_EXPORT_SPEED      = 1
DEF_TICKS_PER_SEC     = 25
DEF_FACE_NORMALS      = 0
DEF_RECALC_NORMALS    = 0
DEF_BLENDER_NORMALS   = 1

###########################################
#                                         #
#  End of Default Configuration Settings  #
#                                         #
###########################################

import Blender
from Blender import Types, Object, NMesh, Material,Armature,Mesh
from Blender.Mathutils import *
from Blender import Draw, BGL
from Blender.BGL import *
import math
import re

global INDEX_LIST,SPACE,BONE_LIST, RESERVED_WORDS
global EXPORT_ANIMATIONS,EXPORT_SHAPES,EXPORT_LIMITS,DEDUPLICATE,FLIP_NORMALS,SWAP_YZ,FLIP_Z,EXPORT_SPEED,TICKS_PER_SEC,FACE_FORMALS,RECALC_NORMALS,BLENDER_NORMALS

FLIP_Z = DEF_FLIP_Z;EXPORT_ANIMATIONS=DEF_EXPORT_ANIMATIONS;EXPORT_SHAPES=DEF_EXPORT_SHAPES;EXPORT_LIMITS=DEF_EXPORT_LIMITS
DEDUPLICATE=DEF_DEDUPLICATE;SWAP_YZ=DEF_SWAP_YZ;FLIP_NORMALS=DEF_FLIP_NORMALS;EXPORT_SPEED=DEF_EXPORT_SPEED;TICKS_PER_SEC= DEF_TICKS_PER_SEC
BLENDER_NORMALS = DEF_BLENDER_NORMALS;RECALC_NORMALS = DEF_RECALC_NORMALS;FACE_NORMALS = DEF_FACE_NORMALS

# Build a list of reserved words so that we can give a warning if any objects use these as names
RESERVED_WORDS = [	'Animation', 'AnimationKey', 'AnimationOptions', 'AnimationSet', 'AnimTicksPerSecond', 'array',
					'Boolean', 'Boolean2d', 'ColorRGB', 'ColorRGBA', 'CompressedAnimationSet', 'Coords2d', 'DeclData', 'DWORD',
					'EffectDWord', 'EffectFloats', 'EffectInstance', 'EffectParamDWord', 'EffectParamFloats', 'EffectParamString', 'EffectString',
					'FaceAdjacency', 'float', 'FloatKeys', 'Frame', 'FrameTransformMatrix', 'FVFData', 'Guid', 'IndexedColor',
					'Material', 'MaterialWrap', 'Matrix4x4', 'Mesh', 'MeshFace', 'MeshFaceWraps', 'MeshMaterialList', 'MeshNormals',
					'MeshTextureCoords', 'MeshVertexColors', 'Patch', 'PatchMesh', 'PatchMesh9', 'PMAttributeRange', 'PMInfo', 'PMVSplitRecord',
					'SkinWeights', 'string', 'template', 'TextureFilename', 'TimedFloatKeys', 'Vector', 'VertexDuplicationIndices',
					'VertexElement', 'XSkinMeshHeader']

anim_tick = Draw.Create(25)


#***********************************************
# MAIN
#***********************************************

# Export ALL
def my_callback(filename):
	if filename.find('.x', -2) <= 0: filename += '.x' 
	xexport = xExport(filename)
	xexport.SelectObjs()

# Export Selected
def my_callback_sel(filename):
	if filename.find('.x', -2) <= 0: filename += '.x' 
	xexport = xExport(filename)
	xexport.exportSelMesh()
def event(evt, val):	
		if evt == Draw.ESCKEY:
			Draw.Exit()                
			return

def button_event(evt): 
	global FLIP_Z,SWAP_YZ,DEDUPLICATE,FLIP_NORMALS,EXPORT_ANIMATIONS,EXPORT_SHAPES,EXPORT_LIMITS,TICKS_PER_SEC,EXPORT_SPEED,FACE_NORMALS,BLENDER_NORMALS,RECALC_NORMALS
	arg = __script__['arg']
  	if evt == 1:
		EXPORT_ANIMATIONS = 1 - EXPORT_ANIMATIONS
		Draw.Redraw(1)
	if evt == 13:
		EXPORT_SHAPES = 1 - EXPORT_SHAPES
		Draw.Redraw(1)
	if evt == 15:
		EXPORT_LIMITS = 1 - EXPORT_LIMITS
		Draw.Redraw(1)
	if evt == 14:
		DEDUPLICATE = 1 - DEDUPLICATE
		Draw.Redraw(1)
	if evt == 2:
		FLIP_NORMALS = 1 - FLIP_NORMALS
		Draw.Redraw(1)
	if evt == 3:
		SWAP_YZ = 1 - SWAP_YZ
		Draw.Redraw(1)
	if evt == 4:
		FLIP_Z = 1 - FLIP_Z
		Draw.Redraw(1)
	if evt == 5:
		EXPORT_SPEED = 1 - EXPORT_SPEED
		Draw.Redraw(1)
	if evt == 10:
		if BLENDER_NORMALS==0:
			BLENDER_NORMALS = 1
			RECALC_NORMALS = 0
			FACE_NORMALS = 0
		Draw.Redraw(1)
	if evt == 11:
		if RECALC_NORMALS==0:
			RECALC_NORMALS = 1
			BLENDER_NORMALS = 0
			FACE_NORMALS = 0
		Draw.Redraw(1)
	if evt == 12:
		if FACE_NORMALS==0:
			FACE_NORMALS = 1
			RECALC_NORMALS = 0
			BLENDER_NORMALS = 0
		Draw.Redraw(1)
	if evt == 6:
		TICKS_PER_SEC = anim_tick.val
	if evt == 7:
		fname = Blender.sys.makename(ext = ".x")
		Blender.Window.FileSelector(my_callback, "Export DirectX", fname)
	if evt == 8:
		fname = Blender.sys.makename(ext = ".x")
		Blender.Window.FileSelector(my_callback_sel, "Export DirectX", fname)
	if evt == 9:
		Draw.Exit()
		
	
def draw():
		global animsg,shapesmsg,flipmsg,swapmsg,anim_tick
		global FLIP_Z,SWAP_YZ,FLIP_NORMALS,EXPORT_ANIMATIONS,EXPORT_SHAPES,EXPORT_LIMITS,DEDUPLICATE,TICKS_PER_SEC,EXPORT_SPEED,RECALC_NORMALS,BLENDER_NORMALS,FACE_NORMALS
		glClearColor(0.55,0.6,0.6,1)
		glClear(BGL.GL_COLOR_BUFFER_BIT)
		#external box
		glColor3f(0.2,0.3,0.3)
		rect(10,492,300,472)
		#--
		#glColor3f(0.3,0.4,0.4)
		#rect(11,429,298,428)
		#--
		glColor3f(0.5,0.75,0.65)
		rect(14,488,292,30)
		#-- Blue box around toggle buttons
		glColor3f(0.5,0.75,0.65)
		rect(14,456,292,250)
		#--
		glColor3f(0.5,0.75,0.65)
		rect(14,202,292,60)
		#--
		glColor3f(0.5,0.75,0.65)
		rect(14,138,292,40)
		#--
		glColor3f(0.5,0.75,0.65)
		rect(14,94,292,70)
		
		glColor3f(0.8,.8,0.6)
		glRasterPos2i(20, 470)
		Draw.Text("DirectX Exporter ",'large')
		Draw.Text("(for Blender 2.45)", 'small')
		#-------Animation toggle---------------------------------------------
		Draw.Toggle("Anim", 1, 20, 420, 55, 20, EXPORT_ANIMATIONS,"export animations")
		if EXPORT_ANIMATIONS :
			animsg = "animation will be exported"
		else:
			animsg = "animation will not be exported"
		glRasterPos2i(100,425)
		Draw.Text(animsg)
		#-------Shape Keys toggle---------------------------------------------
		Draw.Toggle("Shapes", 13, 20, 390, 55, 20, EXPORT_SHAPES, "export shape keys")
		if EXPORT_SHAPES:
			shapesmsg = "shape keys will be exported"
		else:
			shapesmsg = "shape keys will not be exported"
		glRasterPos2i(100, 395)
		Draw.Text(shapesmsg)
		#-------Bone Constraints toggle---------------------------------------
		Draw.Toggle("Limits", 15, 20, 360, 55, 20, EXPORT_LIMITS, "export bone constraints")
		if EXPORT_LIMITS:
			limitsmsg = "bone constraints will be exported"
		else:
			limitsmsg = "constraints will not be exported"
		glRasterPos2i(100, 365)
		Draw.Text(limitsmsg)		
		#-------Vertex Duplication toggle-------------------------------------
		Draw.Toggle("Dedup", 14, 20, 330, 55, 20, DEDUPLICATE, "export vertex duplication data")
		if DEDUPLICATE:
			dedupmsg = "export vertex duplication data"
		else:
			dedupmsg = "no vertex duplication data"
		glRasterPos2i(100, 335)
		Draw.Text(dedupmsg)
		#---Flip normals toggle-----------------------------------------------
		Draw.Toggle("Flip norm", 2, 20, 300, 55, 20, FLIP_NORMALS,"invert normals")
		if FLIP_NORMALS :
			flipmsg = "flipped normals"
		else:
			flipmsg = "not flipped normals"
		glRasterPos2i(100,305)
		Draw.Text(flipmsg)
		#------Swap yz toggle----------------------------------------------------------------
		Draw.Toggle("Swap zy", 3, 20, 270, 55, 20, SWAP_YZ,"swap z,y axis(y up)")
		if SWAP_YZ :
			swapmsg = "Y-axis up"
		else:
			swapmsg = "Z-axis up"
		glRasterPos2i(100,275)
		Draw.Text(swapmsg)
		#------Flip z toggle----------------------------------------------------------------
		Draw.Toggle("Flip z", 4, 20, 240, 55, 20, FLIP_Z,"flip z axis")
		if FLIP_Z :
			zmsg = "left handed system"
		else:
			zmsg = "right handed system"
		glRasterPos2i(100,245)
		Draw.Text(zmsg)
		#------Speed toggle----------------------------------------------------------------
		Draw.Toggle("Speed", 5, 20, 210, 55, 20, EXPORT_SPEED,"Animation speed")
		if EXPORT_SPEED:
			spedmsg = "set speed"
			anim_tick = Draw.Number("", 6,200, 210, 85, 20, anim_tick.val,1,100000,"ticks per second")
		else:
			spedmsg = ""
		glRasterPos2i(100,215)
		Draw.Text(spedmsg)
		#------Blender Normals toggle----------------------------------------------------------------
		Draw.Toggle("Bl.normals", 10, 20, 105, 75, 25, BLENDER_NORMALS,"export normals as in Blender")
		#------Recalculute Normals toggle----------------------------------------------------------------
		Draw.Toggle("recalc.no", 11, 120, 105, 75, 25, RECALC_NORMALS,"export recalculated normals")
		#------Recalculute Normals toggle----------------------------------------------------------------
		Draw.Toggle("no smooth", 12, 220, 105, 75, 25, FACE_NORMALS,"every vertex has the face normal,no smoothing")
		#------Draw Button export----------------------------------------------------------------
		exp_butt = Draw.Button("Export All",7,20, 155, 75, 30, "export all the scene objects")
		sel_butt = Draw.Button("Export Sel",8,120, 155, 75, 30, "export the selected object(only meshes)")
		exit_butt = Draw.Button("Exit",9,220, 155, 75, 30, "exit")
		glRasterPos2i(20,75)
		Draw.Text("(C) 2006  Arben OMARI ")
		glRasterPos2i(20,55)
		Draw.Text("http://www.omariben.too.it")
		glRasterPos2i(20,35)
		Draw.Text("aromar@tin.it")
			
def rect(x,y,width,height):
		glBegin(GL_LINE_LOOP)
		glVertex2i(x,y)
		glVertex2i(x+width,y)
		glVertex2i(x+width,y-height)
		glVertex2i(x,y-height)
		glEnd()
		
def rectFill(x,y,width,height):
		glBegin(GL_POLYGON)
		glVertex2i(x,y)
		glVertex2i(x+width,y)
		glVertex2i(x+width,y-height)
		glVertex2i(x,y-height)
		glEnd()
		
		
		
Draw.Register(draw, event, button_event)


		

#***********************************************
#***********************************************
#                EXPORTER
#***********************************************
#***********************************************

class xExport:
	def __init__(self, filename):
		self.file = open(filename, "w")

#*********************************************************************************************************************************************
	#***********************************************
	#Select Scene objects
	#***********************************************
	def analyzeScene(self):
		''' Analyse a scene to see what top-level objects it contains
		'''
		parent_list = []
		for obj in Object.Get():
			mesh = obj.getData()
			#If object is an Armature, simply check that it has no parent
			if type(mesh) == Types.ArmatureType or obj.getType() == "Empty":
				pare = obj.getParent()
				if pare == None :
					parent_list.append(obj)
				elif pare.getType() == 'Mesh':
					print "Armature '%s' has a mesh as parent - should that be the other way around?" % (obj.getName(),)
						
			# If obj is a mesh, it's a little harder to work out if it's standalone - 
			# need to check for associated armature as well as parents
			if type(mesh) == Types.NMeshType:
				hasArmature = 0
				for mod in obj.modifiers:
					if mod.type == Blender.Modifier.Type['ARMATURE'] and mod[Blender.Modifier.Settings.OBJECT] != None:
						hasArmature = 1
						break
						
				if not hasArmature and obj.getParent() == None:
					parent_list.append(obj)							
						
		return parent_list
	
	def reset(self):
		''' Reset state in advance of an export
		'''
		global BONE_LIST, INDEX_LIST, SPACE
		
		BONE_LIST = []
		INDEX_LIST = []
		SPACE = 0
	
	def getChildren(self,obj):
		children_list = []	
		for object in Object.Get():
			pare = object.parent
			if pare == obj :
				children_list.append(object)
		return children_list
	
	def getArmChildren(self,obj):		
		for object in Object.Get():
			pare = object.parent
			if pare == obj :	
				return object
		
	def getLocMat(self, obj):
		pare = obj.getParent()
		mat = obj.matrixWorld		
		if pare:
			mat_c = Matrix(pare.matrixWorld)			
			mat_c.invert()
			mat_f = mat * mat_c
		else :			
			mat_f = mat
			
		return mat_f
	
	def getArmMesh(self,arm_obj):
		# Look for an Armature modifier
		for obj in Object.Get():
			mesh = obj.getData()
			if type(mesh) == Types.NMeshType:
				for mod in obj.modifiers:
					if mod.type == Blender.Modifier.Type['ARMATURE']:
						if mod[Blender.Modifier.Settings.OBJECT] == arm_obj:
							return obj
		
		# See if there is a child mesh
		Child_objs = self.getChildren(arm_obj)
		for obj in Child_objs:
			mesh = obj.getData()
			if type(mesh) == Types.NMeshType:
				return obj
			
		# No associated mesh found
		raise Exception('Armature has no mesh associated with it.')
	
	def writeObjFrames(self,obj):
		global SPACE,CHILD_OBJ,ch_list
		mesh = obj.getData()
		
		indent_level = 0		
		
		# If selected object is ???, export ???
		if obj.getType() == "Empty" :
			mat = self.getLocMat(obj)
			mat_c = Matrix(mat)
			name = obj.name
			name_f = self.getXCompatibleName(name)			
			self.writeArmFrames(mat_c, name_f)
			# N.B. writeArmFrames opens a template that it does not close
			indent_level += 1
			
		# If selected object is an Armature, export it and any meshes that it is parent to 
		if type(mesh) == Types.ArmatureType :
			# Find associated mesh
			mesh_obj = self.getArmMesh(obj)
			CHILD_OBJ = obj
			
			# Add child mesh to list so that we know not to export it separately
			ch_list.append(mesh_obj)
			
			# Export armature and mesh details			
			self.writeRootBone(obj, mesh_obj)	
			
		# If selected object is a Mesh that hasn't been exported already, export it now
		elif type(mesh) == Types.NMeshType and obj not in ch_list:
			self.writeMeshcoordArm(obj, None, None)
			
		# Let the calling function know if we modified the indentation level at all
		return indent_level
			
			
	def writeChildObj(self,obj):
		global SPACE,ch_list		
		if obj :
			for ob in obj:
				if ob not in ch_list:					
					indent_level = self.writeObjFrames(ob)
					ch_list.append(ob)
					ch_ob = self.getChildren(ob)
					self.writeChildObj(ch_ob)
					
					# Close any brackets opened by writeObjFrames
					for i in range(indent_level):
						self.closeBrackets()
						self.indent_write("  // End of the Object %s \n" % (ob.name,))
	
	def getRootMatrix(self):
		global FLIP_Z, SWAP_YZ
		
		if FLIP_Z:
			mat_flip = Matrix([1, 0, 0, 0], [0, 1, 0, 0], [0, 0, -1, 0], [0, 0, 0, 1])
		else :
			mat_flip = Matrix([1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1])
		if SWAP_YZ :
			mat_rot = RotationMatrix(-90, 4, 'x')
			mat_flip = mat_rot * mat_flip					
		
		return mat_flip
					
	def writeRootFrame(self):
		'''Note that this calls writeArmFrames which opens a template it does not close
		'''
		global EXPORT_SPEED
		if EXPORT_SPEED:
			self.writeAnimTicks()
			
		mat_flip = self.getRootMatrix()						
		self.writeArmFrames(mat_flip, "RootFrame")
		
	def getXCompatibleName(self, name):
		'''GET DirectX Compatible Name
			Arguments:
			* name : Blender name
		'''
		global RESERVED_WORDS
		for word in RESERVED_WORDS:
			if name.lower() == word.lower():
				name = "_" + name
				print "Warning: object named with reserved word '", word, "'. Replacing with '", name, "'"
				break
					
		return re.sub('[^a-zA-Z0-9_]', '', name.replace(" ", "_"))
			
	##################################################################
	# For some completely unfathomable reason, this is the method
	# that doesn't just export selected objects, but ALL objects
	def SelectObjs(self):
		"""Export all objects
		"""
		global SPACE,CHILD_OBJ,ch_list,FLIP_Z,EXPORT_SPEED, EXPORT_ANIMATIONS
		print "exporting..."
		self.reset()
		self.writeHeader()
		self.writeRootFrame() # N.B. This opens a template it does not close
		obj_list = self.analyzeScene()
		ch_list = []
		if len(obj_list) == 0:
			print "Warning: No root-level armature or unmodified mesh objects found"
			
		for obj in obj_list:			
			indent_level = self.writeObjFrames(obj)
			ch_l = self.getChildren(obj)
			for ch in ch_l:
				if ch and ch.getType() == "Armature":
					ch_list.append(ch)
					self.writeObjFrames(ch) # Should always return zero, since it's an armature
				else:
					self.writeChildObj(ch_l)
					
			# Close any templates opened by writeObjFrames
			for i in range(indent_level):
				#print "Surprising!"
				self.closeBrackets()
		
		# Close template opened by writeRootFrame
		SPACE -= 1
		self.indent_write("}  // End of the Root Frame\n")		
		
		if EXPORT_ANIMATIONS and len(obj_list):
		
			action_list = Blender.Armature.NLA.GetActions()
			for action in action_list:
				
				self.indent_write("AnimationSet %s {\n" % (self.getXCompatibleName(action_list[action].getName())))
				SPACE += 1
				for obj in Object.Get():
					
						mesh = obj.getData()
						#if type(mesh) == Types.NMeshType or obj.getType() == "Empty":						
						#	# I don't think the writeAnimationObj method works
						#	ip_list = obj.getIpo()
						#	if ip_list != None :
						#		self.writeAnimationObj(obj)
													
						if type(mesh) == Types.ArmatureType:
							# Write out animations for this armature and this action				
							self.writeAnimation(obj, action_list[action])														

				SPACE -= 1
				self.indent_write("} // End of Animation Set\n")				
		self.writeEnd()
		
		if SPACE:
			print "Oops - something went wrong! Indentation level does not finish at zero"
		#######################################################
		
				
	def writeAnimTicks(self):
		global TICKS_PER_SEC
		self.indent_write("AnimTicksPerSecond {\n")
		self.indent_write("  %d; \n" % (TICKS_PER_SEC))
		self.indent_write("}\n")
						
	def exportSelMesh(self):
		'''Export the Selected Mesh
		'''
		global SPACE
		print "exporting ..."
		self.reset()
		self.writeHeader()
		self.writeRootFrame()	# N.B. This opens a template it does not close	
		obj = Object.GetSelected()[0]
		mesh = obj.getData()
		if type(mesh) == Types.NMeshType :			
			self.writeMeshcoordArm(obj)
			# Close template opened by writeRootFrame
			self.indent_write("}\n")
			ip_list = obj.getIpo()
			if ip_list != None :
				self.indent_write("AnimationSet {\n")
				SPACE += 1
				self.writeAnimationObj(obj)
				SPACE -= 1
				self.indent_write("}\n")							
			print "exporting ..."
		else :
			print "The selected object is not a mesh"
			# Close template opened by writeRootFrame
			self.closeBrackets()
		self.writeEnd()	

	def writeMeshMorphTargets(self, mesh_obj, arm_obj):
		'''Export Morph Targets (shape keys)
	       Arguments:
	       * arm_obj  : Armature object
	       * mesh_obj : Mesh to export
	    '''
		global EXPORT_SHAPES, SPACE
		if EXPORT_SHAPES:
			mesh = mesh_obj.getData()
			# See if this mesh has any keyframes associated with it
			if mesh.key != None:				
				#VERTICES NUMBER
				numvert = 0
				for face in mesh.faces:
					numvert = numvert + len(face.v)									
			
				# Each Shape Key will be a separate block
				for block in mesh.key.getBlocks():
					if block.name != "Basis":
						self.indent_write("MeshMorphTarget %s {\n" % (self.getXCompatibleName(block.name)))
						SPACE += 1
						vertices = block.getData()

						self.indent_write("%d;\n" % (numvert))

						n = 0
						for face in mesh.faces:
							for vert in face.v:
								n += 1
								
								f_vec_vert = vertices[vert.index]
									
								self.indent_write("%f; %f; %f;" % (round(f_vec_vert[0],4), round(f_vec_vert[1],4), round(f_vec_vert[2],4)))
								if n == numvert:
									self.file.write(";\n")
								else :
									self.file.write(",\n")					
							
						SPACE -= 1
						self.indent_write("}\n")					
							
	def writeRootBone(self, arm_obj,  mesh_obj):
		'''Export Root Bone
	       Arguments:
	       * arm_obj  : The armature	      
	       * mesh_obj : Associated mesh
	    '''			    
		global SPACE,root_bon
		arms = arm_obj.getData()
		mat_arm = self.getLocMat(arm_obj)
		
		# Look through the bones in this armature until we find the one with no parent
		parentlessCount = 0
		for bon in arms.bones.values():
			if bon.hasParent():
				pass
			else:
				parentlessCount = parentlessCount + 1
				root_bon = bon						
		
		if parentlessCount > 1:
			print "Warning: %d bones detected without parents. %s selected as root bone" % (parentlessCount, root_bon.name)
		
		# Write out root bone and its matrix
		self.writeBon(arm_obj, root_bon) # N.B. This opens a template it does not close
				
		# Export child bones
		bon_c = root_bon.children
		self.writeChildren(arm_obj, bon_c)
		
		# Close the template opened by writeBon
		SPACE -= 1
		self.indent_write("}  // End of the Bone %s \n" % (root_bon.name))		
		
		# Export the mesh data that goes with this armature		
		self.writeMeshcoordArm(mesh_obj, arms, arm_obj)				
			
	def writeBon(self,arm_obj,bon):
		''' Write out bone details
		
		    Note that this calls writeArmFrames which opens a template it does not close
		'''
		global SPACE, EXPORT_LIMITS
		mat_r = self.getCombineMatrix(arm_obj, bon)
		name_r = bon.name
		name_f = self.getXCompatibleName(name_r)
		self.writeArmFrames(mat_r, name_f)
		
		if EXPORT_LIMITS:
			self.writeBoneLimits(arm_obj, bon)
		
	
	def writeChildren(self,arm_obj,bon_c):
		''' Recursively write out the children of a bone
		'''
		global SPACE,BONE_LIST		
		if bon_c:
			for bo in bon_c:
				if bo.name not in BONE_LIST:					
					self.writeBon(arm_obj,bo) # N.B. This opens a template it does not close
					BONE_LIST.append(bo.name)					 
					self.writeChildren(arm_obj, bo.children)					
					self.closeBrackets() # Close the template opened by writeBon
				
	def indent_write(self, text):
		global SPACE
		if SPACE >= 0:
			s = SPACE
		else:			
			s = 0
		tab = "  "
		self.file.write("%s%s" % (tab * SPACE, text))		
					
	def closeBrackets(self):
		'''Reduce indentation by one level
		'''
		global SPACE
		SPACE -= 1
		tab = "  "
		self.file.write(tab * SPACE)
		self.file.write("}\n")
		
		if SPACE < 0:
			print "Oops - something's gone wrong! Indentation level is now %d" % (SPACE,)
		
	def writeBoneLimits(self, arm_obj, bone):
		'''Write Bone rotation constraints
		'''
		bone_dict = arm_obj.getPose().bones.items()
		for pose_key in bone_dict:
			if pose_key[0] == bone.name:
				p_bone = pose_key[1]
				# Loop over each constraint on this bone looking for rotation Limits
				for cons in p_bone.constraints:
					if cons.type == Blender.Constraint.Type.LIMITROT:
						self.writeBoneConstraint(cons)
				
	def writeBoneConstraint(self, cons):
		global SPACE		
		self.indent_write("BoneConstraintRot {\n");
		self.indent_write("  %d;\n" % (cons[Blender.Constraint.Settings.LIMIT],));
		self.indent_write("  %f; %f;\n" % (		cons[Blender.Constraint.Settings.XMIN],
												cons[Blender.Constraint.Settings.XMAX]));
		self.indent_write("  %f; %f;\n" % (		cons[Blender.Constraint.Settings.YMIN],
												cons[Blender.Constraint.Settings.YMAX]));
		self.indent_write("  %f; %f;\n" % (		cons[Blender.Constraint.Settings.ZMIN],
												cons[Blender.Constraint.Settings.ZMAX]));		
		self.indent_write("}\n");
			
	def getMatrixOffset(self, arm_obj, mesh_obj, bone):
		''' Get matrix that transforms from bone space to object (bind) space
			(or possibly the other way around? It would be good to be certain!)
		'''		
		# Combine armature-relative bind pose matrix with the armature's world matrix
		bone_to_world = (bone.matrix['ARMATURESPACE'] * arm_obj.matrixWorld).invert()
		world_to_obj = mesh_obj.getMatrix('worldspace')
		
		return world_to_obj * bone_to_world
	
	def getCombineMatrix(self, arm_obj, bon):
		''' Find transformation matrix for bone relative to parent, in bind pose
		'''		
		mat_b = bon.matrix['ARMATURESPACE']
		
		# Need to turn Armature-relative pose matrix into one that's relative to the parent Frame.		
		if bon.hasParent():
			mat_p = bon.parent.matrix['ARMATURESPACE'].copy()
			mat_p.invert()
			
		else:
			# No parent, so use the armature's matrix
			mat_p = arm_obj.matrixWorld
					
		return mat_b * mat_p
		
	def getCombineMatrixForFrame(self, arm_obj, bon, frame):
		''' Find transformation matrix for bone relative to parent, at the given time frame
		'''
		global  CHILD_OBJ
		
		# Get the pose at the given frame		
		Blender.Set('curframe', frame)
		pose = CHILD_OBJ.getPose()
		mat_b = pose.bones[bon.name].poseMatrix
		
		# Need to turn Armature-relative pose matrix into one that's relative to the parent Frame.		
		if bon.hasParent():
			mat_p = pose.bones[bon.parent.name].poseMatrix.copy()	
			mat_p.invert()
			
		else:
			# No parent, so use the armature's matrix
			mat_p = arm_obj.matrixWorld # self.getIdentityMatrix() # 
				
		return mat_b * mat_p

#*********************************************************************************************************************************************
	def writeSkinWeights(self, arm, arm_obj, mesh, mesh_obj):
		'''Write SkinWeights
		'''
		global INDEX_LIST, SPACE				
		
		v_dict = {}
		Blender.Set('curframe',1)
		self.indent_write("XSkinMeshHeader {\n")
		SPACE += 1
		max_infl = 0
		found_verts = 0
		bone_count = 0
		for bo in arm.bones.values() :
			name = bo.name
			try :
				vertx_list = mesh.getVertsFromGroup(name,1)
				bone_count = bone_count + 1
				if len(vertx_list):
					found_verts = 1
				for inde in vertx_list :
					vert_infl = [(bone, weight) for (bone, weight) in mesh.getVertexInfluences(inde[0]) if bone in arm.bones.keys()]
					ln_infl = len(vert_infl)
					if ln_infl > max_infl :
						max_infl = ln_infl
				
			except:
				# Will get an exception if there's no vertex group for this bone				
				pass		
			
		if not found_verts:
			print "No vertices were found which are affected by bones. Make sure your animation is based on Vertex Groups and not Envelopes"
			
		# Add one bone for the vertices that are left over
		bone_count += 1
		
		self.indent_write("%d; \n" % (max_infl))
		self.indent_write("%d; \n" % (max_infl * 3))
		self.indent_write("%d; \n" % (bone_count))
		SPACE -= 1
		self.indent_write("} // End of XSkinMeshHeader\n")		
		
		# Keep track of any vertices which aren't attached to a bone
		# since we'll need to assign any leftovers to the RootFrame
		vertex_bone = {}
		
		for bo in arm.bones.values() :
			bo_list = []
			weight_list = []
			name = bo.name						
			
			try :			
				# Return a list of vertices in this group
				vert_list = mesh.getVertsFromGroup(name)
			except:
				# Will get an exception if there's no vertex group for this bone
				continue
					
			for indx in vert_list:
				# Get a list of vertex influences that actually correspond to bones				
				ver_infl = [(bone, weight) for (bone, weight) in mesh.getVertexInfluences(indx) if bone in arm.bones.keys()]
						
				infl = 0.0
				if len(ver_infl) != 0:
					# Tick off the vertices that have a bone
					vertex_bone[indx] = 1
					
					# Do a quick check to make sure the vertex group isn't matched with the armature object itself
					if name == mesh.name:
						print "This will probably fail because you have a vertex group named the same as the root mesh,", name
					
					sum = 0.0
					
					# Sum the weights of all bones that exert influence
					# on this vertex, so we can find the ratio for the
					# current bone (bo)						
					for bone_n, weight in ver_infl:
						if bone_n == name:
							infl = weight
						sum += weight
						
					infl /= sum
					
				
				# The global INDEX_LIST maps vertices in our X file to Blender vertex indices
				# Find all the X file vertices which correspond to this Blender vertex				
				indx_indices = [i for i in range(len(INDEX_LIST)) if INDEX_LIST[i] == indx]		
				bo_list.extend(indx_indices)
				weight_list.extend([infl] * len(indx_indices))				
						
			# Get the rest pose matrix for this bone
			matx = self.getMatrixOffset(arm_obj, mesh_obj, bo)
			
			# Write out the list of vertices for this bone and corresponding weights
			self.writeBoneSkinWeights(name, bo_list, weight_list, matx)
			
		# Now look for vertices that weren't attached to a bone
		v = -1
		root_vertices = []
		weight_list = []
		for face in mesh.faces:
			for vertex in face.v:
				v += 1
				if not vertex_bone.has_key(vertex.index):
					# Find all the X file vertices which correspond to this Blender vertex
					root_vertices.append(v)
					weight_list.append(1.0)	
		
		if len(weight_list):
			print "%d vertices absent from vertex groups" % (len(weight_list),)
		# Now we need to output all remaining vertices and attach them to the RootFrame		
		# Find it's matrix relative to the armature
		matx = mesh_obj.matrixLocal.copy()
		matx.invert()
		self.writeBoneSkinWeights(mesh.name, root_vertices, weight_list, matx)
		
	def getIdentityMatrix(self):
		return Matrix([1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1])
	
	def writeBoneSkinWeights(self, name, vertices, weights, matx):
		''' Write SkinWeights for a given bone
			 name - The name of the bone
			 vertices - A list of vertices influenced by this bone
			 weights - A list of weights, one for each entry in vertices
			 matx - The bone offset matrix
		'''
		global SPACE
		f_name = self.getXCompatibleName(name)
		
		self.indent_write("SkinWeights {\n")
		SPACE += 1
		self.indent_write('"%s"; \n' % (f_name))
		self.indent_write('%d; \n' % (len(vertices)))
		
		# Write out the list of vertices attached to this bone
		count = 0
		for ind in vertices :
			count += 1
			if count == len(vertices):
				delimeter = ";"
			else:
				delimeter = ","
				
			self.indent_write("%d%s \n" % (ind, delimeter))

		# For each vertex, write out the weight
		count = 0
		for wegh in weights :
			count += 1
			
			if count == len(weights):
				delimeter = ";"
			else:
				delimeter = ","
				
			self.indent_write("%f%s \n" % (round(wegh,6), delimeter))
		
		# Write out rest pose matrix		
		self.writeMatrix(matx)
		SPACE -= 1
		self.indent_write("}\n")		
		

	def writeArmFrames(self, matx, name):
		''' Write out a frame within the armature
			matx - The local transform relative to parent frame
			
			Note this does not close the structure that it opens - that's for the caller to do
		'''
		global SPACE		
		self.indent_write("Frame %s {\n\n" % (name,))		
		self.indent_write("  FrameTransformMatrix {\n")
		SPACE += 2
		self.writeMatrix(matx)
		SPACE -= 1
		self.indent_write("}\n")				
	
	def writeMatrix(self, matx):
		'''Write out a Matrix
		'''
		global SPACE
						
		self.indent_write("%f,%f,%f,%f,\n" %
							(round(matx[0][0],4),round(matx[0][1],4),round(matx[0][2],4),round(matx[0][3],4)))		
		self.indent_write("%f,%f,%f,%f,\n" %
							(round(matx[1][0],4),round(matx[1][1],4),round(matx[1][2],4),round(matx[1][3],4)))		
		self.indent_write("%f,%f,%f,%f,\n" %
							(round(matx[2][0],4),round(matx[2][1],4),round(matx[2][2],4),round(matx[2][3],4)))		
		self.indent_write("%f,%f,%f,%f;;\n" %
							(round(matx[3][0],4),round(matx[3][1],4),round(matx[3][2],4),round(matx[3][3],4)))
							
	def writeMatrixAsList(self, matx):
		'''Write out a Matrix as an unformatted list
		'''
		self.indent_write("%f,%f,%f,%f," %
							(round(matx[0][0],4),round(matx[0][1],4),round(matx[0][2],4),round(matx[0][3],4)))
		self.indent_write("%f,%f,%f,%f," %
							(round(matx[1][0],4),round(matx[1][1],4),round(matx[1][2],4),round(matx[1][3],4)))
		self.indent_write("%f,%f,%f,%f," %
							(round(matx[2][0],4),round(matx[2][1],4),round(matx[2][2],4),round(matx[2][3],4)))
		self.indent_write("%f,%f,%f,%f;;" %
							(round(matx[3][0],4),round(matx[3][1],4),round(matx[3][2],4),round(matx[3][3],4)))	
		
#*********************************************************************************************************************************************
	
	def writeHeader(self):
		'''HEADER
		'''
		global EXPORT_SHAPES, EXPORT_SPEED, EXPORT_LIMITS
		self.indent_write("xof 0303txt 0032\n\n\n")
		self.indent_write("template VertexDuplicationIndices { \n\
 <b8d65549-d7c9-4995-89cf-53a9a8b031e3>\n\
 DWORD nIndices;\n\
 DWORD nOriginalVertices;\n\
 array DWORD indices[nIndices];\n\
}\n\
template XSkinMeshHeader {\n\
 <3cf169ce-ff7c-44ab-93c0-f78f62d172e2>\n\
 WORD nMaxSkinWeightsPerVertex;\n\
 WORD nMaxSkinWeightsPerFace;\n\
 WORD nBones;\n\
}\n\
template SkinWeights {\n\
 <6f0d123b-bad2-4167-a0d0-80224f25fabb>\n\
 STRING transformNodeName;\n\
 DWORD nWeights;\n\
 array DWORD vertexIndices[nWeights];\n\
 array float weights[nWeights];\n\
 Matrix4x4 matrixOffset;\n\
}\n")
		if EXPORT_SPEED:
			self.indent_write("template AnimTicksPerSecond {\n\
 <9e415a43-7ba6-4a73-8743-b73d47e88476>\n\
 DWORD AnimTicksPerSecond;\n\
}\n")
		if EXPORT_LIMITS:
			self.indent_write("template BoneConstraintRot {\n\
 <5850992a-a18e-11dc-8314-0800200c9a66>\n\
 BYTE ConstrainedAxes;\n\
 float xMin; float xMax;\n\
 float yMin; float yMax;\n\
 float zMin; float zMax;\n\
}\n")
		if EXPORT_SHAPES:
			self.indent_write("template MeshMorphTarget {\n\
 <537fe4be-732b-11dc-8314-0800200c9a66>\n\
 DWORD nVertices;\n\
 array Vector vertices[nVertices];\n\
}\n\
template MorphedAnimationKey {\n\
 <2a2ea9e0-7330-11dc-8314-0800200c9a66>\n\
 DWORD nKeys;\n\
 array TimedFloatKeys keys[nKeys];\n\
}\n")
		self.indent_write("\n");
		
	def writeEnd(self):
		'''CLOSE FILE
		'''
		self.file.close()
		print "... finished"


	def writeTextures(self,name, tex):
		'''EXPORT TEXTURES
		'''
		mesh = name.data
		for face in mesh.faces:
			if face.image and face.image.name not in tex:
				tex.append(face.image.name)
	
	def getMeshFlipFlag(self, obj):
		''' See if a mesh needs to have its winding order reversed
		'''			
		global FLIP_Z
		
		# Check if there is a negative scale factor on this mesh,
		# and combine that with the global flag for flipping Z
 		axisSize = obj.getSize('localspace')
		negScale = FLIP_Z
		for size in axisSize:
			if size < 0:
				negScale = not negScale
		return negScale
	
	def getWindingOrder(self, negScale):
		''' Return a tuple of lists, (index3, index4), where index3 an ordered list of the indices to use for a triangle,
		    and index4 is for a quad
		'''		
		index3 = range(3)
		index4 = range(4)
		if negScale:
			index3.reverse()
			index4.reverse()
		return index3, index4

	def writeMeshcoordArm(self, obj, arm = None, arm_ob = None):
		''' Write out co-ordinates of a mesh object
			 obj - The mesh object
			 arm_ob - Associated armature object, or None
		'''
		global INDEX_LIST,FLIP_Z,SPACE
		
		# Start off by building a list of textures
		tex = []
		self.writeTextures(obj, tex)
			
		#TransformMatrix
		mat = self.getLocMat(obj)
		name_f = self.getXCompatibleName(obj.name)
		self.writeArmFrames(mat, name_f)
		mesh = obj.getData()		
		self.indent_write("Mesh { //%s\n" % (obj.name,))
		SPACE += 1
		numface = len(mesh.faces)
		
		# Check if there is a negative scale factor on this mesh 		
		negScale = self.getMeshFlipFlag(obj)
		if negScale == (not FLIP_Z):
			print "Negative scale detected, reversing winding order"
		
		#VERTICES NUMBER
		numvert = 0
		for face in mesh.faces:
			numvert = numvert + len(face.v)
		self.indent_write("%d;\n" % (numvert))		
		if numvert == 0:
			print "Mesh named",mesh.name,"has no vertices.Problems may occur using the .x file"					
		
		#VERTICES COORDINATES
		counter = 0
		for face in mesh.faces:
			counter += 1
			for n in range(len(face.v)):
				INDEX_LIST.append(face.v[n].index)
				vec_vert = Vector([(face.v[n].co[0]), face.v[n].co[1], face.v[n].co[2], 1])
				f_vec_vert = vec_vert
				self.indent_write("%f; %f; %f;" % (round(f_vec_vert[0],4), round(f_vec_vert[1],4), round(f_vec_vert[2],4)))
			
				if counter == numface :
					if n == len(face.v)-1 :
						self.file.write(";\n")
					else :
						self.file.write(",\n")
				else :
					self.file.write(",\n")
				
		# If Z is flipped, need to reorder the vertices to keep the winding order consistent
		# Same applies if the object has a negative scale factor in one axis
		index3, index4 = self.getWindingOrder(negScale)		

		#FACES NUMBER 
		self.indent_write("%s;\n" % (numface))  
		coun,counter = 0, 0
		for face in mesh.faces :
			coun += 1
			if coun == numface:
				delimeter = ";"
			else:
				delimeter = ","
				
			if len(face.v) == 3:
				self.indent_write("3; %d, %d, %d;%s\n" % (tuple([counter + ind for ind in index3]) + (delimeter,)))
				counter += 3
			elif len(face.v) == 4:
				self.indent_write("4; %d, %d, %d, %d;%s\n" % (tuple([counter + ind for ind in index4]) + (delimeter,)))
				counter += 4
			elif len(face.v) < 3:
				print "WARNING:the mesh has faces with less then 3 vertices"
				print "        It my be not exported correctly."				
		
		# Write out all of the other mesh properties
		mesh = obj.getData()
		self.writeMeshMorphTargets(obj, arm_ob)
		self.writeMeshMaterialList(obj, mesh, tex)
		self.writeMeshNormals(obj, mesh)
		self.writeMeshVertexDuplicates(arm_ob, obj, mesh)
		self.writeMeshTextureCoords(obj, mesh)
		if arm != None:
			self.writeSkinWeights(arm,arm_ob,mesh,obj)
		
		# Close the data structures we opened at the top of the function
		SPACE -= 2
		self.indent_write("  } // End of Mesh\n")		
		self.indent_write("}  // End of the Object %s \n" % (obj.name,))		

	
	def writeMeshMaterialList(self, obj, mesh, tex):
		'''MESH MATERIAL LIST
		'''
		global SPACE
		
		self.indent_write("MeshMaterialList {\n")
		SPACE += 1
		#HOW MANY MATERIALS ARE USED
		count = len(mesh.getMaterials())
		if count == 0:
			print "WARNING: No materials found. The mesh probably will not be rendered."	
		
		self.indent_write("%d;\n" % (len(tex) + count))
		#HOW MANY FACES IT HAS
		numfaces=len(mesh.faces)
		self.indent_write("%d;\n" % (numfaces))
		##MATERIALS INDEX FOR EVERY FACE
		counter = 0
		for face in mesh.faces :
			counter += 1
			mater = face.materialIndex
			if counter == numfaces:
				delimeter = ";"
			else:
				delimeter = ","
				
			if face.image and face.image.name in tex :
				self.indent_write("%d%s\n" % (tex.index(face.image.name) + count, delimeter))
			else :
				self.indent_write("%d%s\n" % (mater, delimeter))
			
		##MATERIAL NAME
		for mat in mesh.getMaterials():
			self.indent_write("Material")
			name_m = mat.name
			name_f = self.getXCompatibleName(name_m)
			self.file.write(" %s "% (name_f))
			self.file.write("{\n")
			self.indent_write("    %f; %f; %f;" % (mat.R, mat.G, mat.B))
			self.indent_write("%s;;\n" % (mat.alpha))
			self.indent_write("    %f;\n" % (mat.spec))
			self.indent_write("    %f; %f; %f;;\n" % (mat.specR, mat.specG, mat.specB))
			self.indent_write("    0.0; 0.0; 0.0;;\n")
			self.indent_write("}  //End of Material\n") 
		
		for mat in tex:
			self.indent_write("Material Mat")
			self.file.write("%s "% (len(tex)))
			self.file.write("{\n")
			self.indent_write("    1.0; 1.0; 1.0; 1.0;;\n")
			self.indent_write("    1.0;\n")
			self.indent_write("    1.0; 1.0; 1.0;;\n")
			self.indent_write("    0.0; 0.0; 0.0;;\n")
			self.indent_write("  TextureFilename {")
			self.indent_write('    "%s";'% (mat))
			self.indent_write("  }\n")
			self.indent_write("}  // End of Material\n")
			
		SPACE -= 1
		self.indent_write("}  //End of MeshMaterialList\n")		

	def writeMeshNormals(self,obj,mesh):
		'''MESH NORMALS
		'''
		global FLIP_NORMALS,FLIP_Z,FACE_NORMALS,RECALC_NORMALS,BLENDER_NORMALS,SPACE
		
		self.indent_write("MeshNormals {\n")
		SPACE += 1
		
		#VERTICES NUMBER
		numvert = 0
		for face in mesh.faces:
			numvert = numvert + len(face.v)
		self.indent_write("%d;\n" % (numvert))
		numfaces=len(mesh.faces)
		if FLIP_NORMALS :
			fl = -1
		else :
			fl = 1
			
		#VERTICES NORMAL
		if BLENDER_NORMALS:
			self.writeBlenderNormals(mesh,fl)
		if RECALC_NORMALS:
			self.writeRecalcNormals(mesh,fl)	
		if FACE_NORMALS:
			self.writeNoSmothing(mesh,fl)								
		
		# Check if there is a negative scale factor on this mesh 		
		negScale = self.getMeshFlipFlag(obj)
		
		# If Z is flipped, need to reorder the vertices to keep the winding order consistent
		# Same applies if the object has a negative scale factor in one axis
		index3, index4 = self.getWindingOrder(negScale)

		#FACES NUMBER 
		self.indent_write("%s;\n" % (numfaces))  
		coun,counter = 0, 0
		for face in mesh.faces :
			coun += 1
			if coun == numfaces:
				delimeter = ";"
			else:
				delimeter = ","
				
			if len(face.v) == 3:
				self.indent_write("3; %d, %d, %d;%s\n" % (tuple([counter + ind for ind in index3]) + (delimeter,)))
				counter += 3
			else:
				self.indent_write("4; %d, %d, %d, %d;%s\n" % (tuple([counter + ind for ind in index4]) + (delimeter,)))
				counter += 4

		SPACE -= 1
		self.indent_write("}  //End of MeshNormals\n")		
		
	def writeBlenderNormals(self,mesh,fl):
		numfaces=len(mesh.faces)
		#VERTICES NORMAL
		counter = 0
		for face in mesh.faces:
			counter += 1  			
			for n in range(len(face.v)):
				self.indent_write("%f; %f; %f;" % (
									(round(face.v[n].no[0],6)*fl),(round(face.v[n].no[1],6)*fl),(round(face.v[n].no[2],6)*fl)))
				if counter == numfaces :
					if n == len(face.v)-1 :
						self.file.write(";\n")
					else :
						self.file.write(",\n")
				else :
					self.file.write(",\n")
						
	def writeRecalcNormals(self,mesh,fl):
		numfaces=len(mesh.faces)
		normal_list = {}
		
		# For each vertex, average the normals of all neighbouring faces
		idx = 0
		for vertex in mesh.verts:
			v_norm = Vector([0, 0, 0])
			normal_list[idx] = v_norm
			idx += 1
			for face in mesh.faces:
				for verts in face.v:
					if verts.index == vertex.index :
						v_norm[0] += face.no[0]
						v_norm[1] += face.no[1]
						v_norm[2] += face.no[2]
			
			v_norm.normalize()
						
		counter = 0
		for face in mesh.faces:
			counter += 1 
			n = 0 
			for vert in face.v:
				n += 1			
				norm = normal_list[vert.index]
				
				self.indent_write("%f; %f; %f;" % (
							(round(norm[0],6)*fl),(round(norm[1],6)*fl),(round(norm[2],6)*fl)))		
				if counter == numfaces :
					if n == len(face.v) :
						self.file.write(";\n")
					else :
						self.file.write(",\n")
				else :
					self.file.write(",\n")
						
	def writeNoSmothing(self,mesh,fl):
		numfaces=len(mesh.faces)
		counter = 0
		for face in mesh.faces:
				counter += 1 
				n = 0 
				for n in range(len(face.v)):
					n += 1
					self.indent_write("%f; %f; %f;" % (
									(round(face.no[0],6)*fl),(round(face.no[1],6)*fl),(round(face.no[2],6)*fl)))
					
							
					if counter == numfaces :
						if n == len(face.v) :
							self.file.write(";\n")
						else :
							self.file.write(",\n")
					else :
						self.file.write(",\n")
	
	def writeMeshVertexDuplicates(self, arm_ob, obj, mesh):
		'''MESH VERTEX DUPLICATION INDICES
		'''
		global DEDUPLICATE
		if DEDUPLICATE:
			numvert = 0
			numunique = 0
			vert_index = {}
			unique_index_list = []
			
			mat = self.getLocMat(obj)
			
			# Find all of the unique vertices and map them to an index
			for face in mesh.faces:
				for vert in face.v:
					numvert += 1
					
					vec_vert = Vector([vert.co[0], vert.co[1], vert.co[2], 1])
					f_vec_vert = vec_vert
					
					key = (str(round(f_vec_vert[0], 4)), str(round(f_vec_vert[1], 4)), str(round(f_vec_vert[2], 4)))
					if not vert_index.has_key(key):
						vert_index[key] = numunique
						numunique += 1
						
					unique_index_list.append(vert_index[key])
			
			self.indent_write("VertexDuplicationIndices {\n")
			self.indent_write("  %d;\n" % (numvert))
			self.indent_write("  %d;\n" % (numunique))
			
			n = 0
			for ind in unique_index_list:
				n += 1
				if n == numvert:
					delimeter = ";"
				else:
					delimeter = ","
					
				self.indent_write("  %d%s\n" % (ind, delimeter))
			
			self.indent_write("}	//End of VertexDuplicationIndices\n")
	
	def writeMeshTextureCoords(self, name, mesh):
		'''MESH TEXTURE COORDS
		'''
		global SPACE
		
		if mesh.hasFaceUV():
			self.indent_write("MeshTextureCoords {\n")
			SPACE += 1
			#VERTICES NUMBER
			numvert = 0
			for face in mesh.faces:
				numvert += len(face.v)
			self.indent_write("%d;\n" % (numvert))
			#UV COORDS
			numfaces = len(mesh.faces)
			counter = -1
			co = 0
			for face in mesh.faces:
				counter += 1
				co += 1
				for n in range(len(face.v)):
					self.indent_write("%f;%f;" % (mesh.faces[counter].uv[n][0], -mesh.faces[counter].uv[n][1]))
					if co == numfaces :
						if n == len(face.v) - 1 :
							self.file.write(";\n")
						else :
							self.file.write(",\n")
					else :
						self.file.write(",\n")

			SPACE -= 1
			self.indent_write("}  //End of MeshTextureCoords\n")			
#***********************************************#***********************************************#***********************************************	
		
	def writeMorphedAnimation(self, arm_obj, mesh_obj, action, ipo):
		'''WRITE MORPHED ANIMATION KEYS
	       Arguments:
	       * arm_obj  : Armature object
	       * mesh_obj : Mesh object
	       * action   : Name of action
	       * ipo      : Shape IPO for current action
	    '''	
		global EXPORT_SHAPES, SPACE
		if EXPORT_SHAPES:
			mesh = mesh_obj.getData()
			
			if len(ipo) != 0 and mesh.key != None:			
				self.indent_write("Animation { \n")
				self.indent_write("  MorphedAnimationKey { \n")
				SPACE += 2
				
				# Check that every shape key (other than the Basis) has an IPO curve
				if len(ipo) != len(mesh.key.getBlocks()) - 1:
					print "Warning: Action '", action, "' doesn't have an IPO curve for every shape key"
			
				# There will be one curve in ipo per Shape Key
				# Make the (slightly naive) assumption that each curve has the same points
				for firstCurve in ipo:
					break
			
				self.indent_write("   %d; \n" % (len(firstCurve.bezierPoints)))
				
				warnedAboutMultipleKeys = 0
				
				# One bezierPoint per key frame
				for n in range(len(firstCurve.bezierPoints)):
					point = firstCurve.bezierPoints[n]
					self.indent_write("   %d;%d;" % ((point.pt[0]), len(ipo)))
					
					foundNonZero = 0
					m = 0
					for curve in ipo:										
						if len(curve.bezierPoints) != len(firstCurve.bezierPoints):
							print "This is going to go wrong because not every Shape Key has the same number of key frames"
							
						# Output weight for each Shape Key in turn
						point = curve.bezierPoints[n]
						self.indent_write("%f" % (point.pt[1]))
						
						if point.pt[1] != 0.0:
							if foundNonZero and not warnedAboutMultipleKeys:
								print "More than one shape key is exerting influence simultaneously - does your application support this?"
								warnedAboutMultipleKeys = 1
							foundNonZero = 1
						
						if m == len(ipo) - 1:
							self.file.write(";;")
						else:
							self.file.write(",")
						
						m = m + 1
				
					if n == len(firstCurve.bezierPoints) - 1:
						self.file.write("; \n")
					else:
						self.file.write(", \n")
								
				SPACE -= 2
				self.indent_write(" } \n")
				self.indent_write("} \n")				
					
	
	
	def writeAnimation(self,arm_ob, action):
		'''WRITE ANIMATION KEYS for an armature
		'''
		global root_bon, SPACE
		arm = arm_ob.getData()				
				
		ip = action.getAllChannelIpos()
		
		# Look for mesh associated with this armature
		# so that we can output any Shape Keys (morph targets)
		# associated with it
		arm_mesh = self.getArmMesh(arm_ob)
		
		# Look for an IPO object for shape keys
		if arm_mesh != None and 'Shape' in ip:
			self.writeMorphedAnimation(arm_ob, arm_mesh, action.getName(), ip['Shape'])
			
		# Make this the active action so that we export the data properly
		action.setActive(arm_ob)				
		
		# Now output animation keys for each bone in the armature
		for bon in arm.bones.values() :
			point_list = []
			name = bon.name
			name_f = self.getXCompatibleName(name)
			try :
				if bon.name in ip:
					ip_bon_channel = ip[bon.name]
					
					if ip_bon_channel is None or len(ip_bon_channel.curves) == 0:
						print "No IPO curves found for bone '%s' in action '%s' - skipping" % (bon.name, action.getName())
					elif ip_bon_channel[Blender.Ipo.PO_LOCZ] is None:
						print "Geero was too lazy to code for this... You have no LocZ IPO Curve for bone '%s' in action '%s'" % (bon.name, action.getName())
					else:
						for po in ip_bon_channel[Blender.Ipo.PO_LOCZ].bezierPoints:
							point_list.append(int(po.pt[0]))
					
						self.indent_write("Animation { \n")
						self.indent_write("  { %s }\n" %(name_f))
						self.indent_write("  AnimationKey { \n")
						self.indent_write("   4;\n")
						self.indent_write("   %d; \n" % (len(point_list)))
						SPACE += 2

						for fr in point_list:
							
							mat = self.getCombineMatrixForFrame(arm_ob, bon, fr)
								
							self.indent_write("   %d;" % (fr))
							self.file.write("16;")
						
							self.writeMatrixAsList(mat)
						
							if fr == point_list[len(point_list)-1]:
								self.file.write(";\n")
							else:
								self.file.write(",\n")
						SPACE -= 2
						self.indent_write("  }\n")
						self.indent_write("}\n")
						self.indent_write("\n")						
			except:
				raise			
				pass
		
		

	def writeAnimationObj(self, obj):
		'''WRITE ANIMATION KEYS
		'''
		global SPACE
		
		print "writeAnimationObj - expect a rubbish .X file!"
		point_list = []
		ip = obj.getIpo()
		poi = ip.getCurves()
		for po in poi[0].getPoints():
			a = po.getPoints()
			point_list.append(int(a[0]))
		
		name = obj.name
		name_f = self.getXCompatibleName(name)
		self.indent_write("Animation {\n")
		self.indent_write(" { %s }\n" % (name_f))
		self.indent_write("   AnimationKey { \n")
		self.indent_write("   4;\n")
		self.indent_write("   %d; \n" % (len(point_list)))
		SPACE += 2
		
		for fr in point_list:
			self.indent_write("   %d;" % (fr))
			self.file.write("16;")
			Blender.Set('curframe',fr)
				
			#mat_new = self.getLocMat(obj) 
			mat_new = obj.matrixLocal
			self.writeMatrixAsList(mat_new)

			if fr == point_list[len(point_list)-1]:
				self.file.write(";\n")
			else:
				self.file.write(",\n")
		SPACE -= 2
		self.indent_write("  }\n")
		self.indent_write("}\n")		

	
		
#***********************************************#***********************************************#***********************************************



	
	
