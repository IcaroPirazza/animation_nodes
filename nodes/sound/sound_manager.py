import bpy
import os
from bpy.props import *
from bpy.types import Node
from ... mn_utils import getNode
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

# https://developer.blender.org/diffusion/B/browse/master/source/blender/imbuf/intern/util.c;23c7d14afdb0e5b6d56d4776b487bff6ab5d232c$165
soundFileTypes = ["wav", "ogg", "oga", "mp3", "mp2", "ac3", "aac", "flac", "wma", "eac3", "aif", "aiff", "m4a", "mka"]

class SoundStripData(bpy.types.PropertyGroup):
    filepath = StringProperty()

class mn_SoundManager(Node, AnimationNode):
    bl_idname = "mn_SoundManager"
    bl_label = "Sound Manager"
    
    loadedSounds = CollectionProperty(type = SoundStripData)
    
    def init(self, context):
        self.use_custom_color = True
        self.color = (0.4, 0.9, 0.4)
        self.width = 400
        
    def getInputSocketNames(self):
        return {}
    def getOutputSocketNames(self):
        return {}
        
    def draw_buttons(self, context, layout):
        self.callFunctionFromUI(layout, "loadNewSound", text = "Load New", description = "Choose a sound file with the file browser and load it", icon = "PLUS")
        
        editor = context.scene.sequence_editor
        if not editor: return
        soundSequences = [sequence for sequence in editor.sequences if sequence.type == "SOUND"]
        
        col = layout.column(align = False)
        for i, sequence in enumerate(soundSequences):
            box = col.box()
            box.prop(sequence, "name")
            box.prop(sequence, "frame_start")
            props = box.operator("mn.remove_sound_sequence")
            props.index = i
        
    def loadNewSound(self):
        bpy.ops.mn.load_sound_file("INVOKE_DEFAULT", nodeTreeName = self.id_data.name, nodeName = self.name)
        
    def loadSoundFile(self, filepath):
        editor = self.getSequenceEditor()
        channel = self.getEmptyChannel(editor)
        sound = editor.sequences.new_sound(os.path.basename(filepath), filepath, channel, 1)
        print(sound)
        
    def getSequenceEditor(self):
        scene = bpy.context.scene
        if not scene.sequence_editor:
            scene.sequence_editor_create()
        return scene.sequence_editor
        
    def getEmptyChannel(self, editor):
        channels = [True] * 32
        for sequence in editor.sequences:
            channels[sequence.channel - 1] = False
        for i, channel in enumerate(channels):
            if channel:
                return i + 1
        raise Exception("No free sequencer channel")
               
            
        
class LoadSoundFile(bpy.types.Operator):
    bl_idname = "mn.load_sound_file"
    bl_label = "Load Sound File"
    
    nodeTreeName = bpy.props.StringProperty()
    nodeName = bpy.props.StringProperty()
    filepath = bpy.props.StringProperty(subtype = "FILE_PATH")
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return { 'RUNNING_MODAL' }
        
    def execute(self, context):
        node = getNode(self.nodeTreeName, self.nodeName)
        path = self.filepath
        if any([path.endswith(extension) for extension in soundFileTypes]):
            node.loadSoundFile(self.filepath)
        else:
            raise Exception("No valid file name extension")
        return {'FINISHED'}

class RemoveSoundSequence(bpy.types.Operator):
    bl_idname = "mn.remove_sound_sequence"
    bl_label = "Remove Sound Sequence"
    
    index = bpy.props.IntProperty()
        
    def execute(self, context):
        editor = getSequenceEditor()
        sequence = getSoundSequences()[self.index]
        sound = sequence.sound
        editor.sequences.remove(sequence)
        if sound.users == 0:
            bpy.data.sounds.remove(sound)
        return {'FINISHED'}      





def getSoundSequences():
    editor = bpy.context.scene.sequence_editor
    if not editor: return []
    return [sequence for sequence in editor.sequences if sequence.type == "SOUND"]
        
def getSequenceEditor():
    scene = bpy.context.scene
    if not scene.sequence_editor:
        scene.sequence_editor_create()
    return scene.sequence_editor         