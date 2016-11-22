import maya.OpenMaya as om
import maya.cmds as cmds
import maya.mel as mel


__author__ = 'Jamie Telford'


class IKFKswitch():

    def __init__(self):
        """init settings"""
        self.mel_command = (
            'ikFK(0, `ls -sl`);',
            '',
            'SetIKFKKeyframe;',
            'NextFrame;',
            'ikFK(0, `ls -sl`);',
            '',
            'SetIKFKKeyframe;'
        )

        self.ShowUI()

    def ShowUI(self):
        """Show window."""
        self.source = 'polar_helper'
        self.polar = 'r_Polar_CTRL'

    def get_polar_position(self, handle):
        """Get pole position."""
        joints = cmds.ikHandle(handle, jl=True, q=True)
        joints.append(cmds.listRelatives(joints[-1], c=1)[0])

        j1 = cmds.xform(joints[0], q=1, ws=1, t=1)
        j2 = cmds.xform(joints[1], q=1, ws=1, t=1)
        j3 = cmds.xform(joints[2], q=1, ws=1, t=1)

        vec1 = om.MVector(j1)
        vec2 = om.MVector(j2)
        vec3 = om.MVector(j3)

        first_last = vec3 - vec1
        first_second = vec2 - vec1

        dot = first_second * first_last
        cast = float(dot) / float(first_last.length())
        first_last_normal = first_last.normal()
        cast_vec = first_last_normal * cast

        point = (first_second - cast_vec) * 3
        pole_pos = point + vec2
        pole_offset = om.MVector(cmds.xform(self.polar, q=1, rp=1))
        return(pole_pos - pole_offset)

    def switch_ikfk(self):
        """Main switch call from button."""
        # testing for multiple IK handles.. eventually to test against connected
        selected = cmds.ls(sl=True)
        ik_handles = cmds.ls(et='ikHandle')
        for handle in ik_handles:
            if cmds.getAttr('{}.ikBlend'.format(handle)):
                cmds.setKeyframe(self.polar)
                self.mel_command[1] = 'setAttr "{}.ikBlend" 1;'.format(handle)
                self.mel_command[5] = 'setAttr "{}.ikBlend" 0;'.format(handle)
                mel.eval(''.join(self.mel_command))
                cmds.setKeyframe(self.polar)
            else:
                cmds.select(self.polar)
                cmds.setKeyframe(self.polar)
                cmds.xform(self.polar, t=self.get_polar_position(handle))
                self.mel_command[1] = 'setAttr "{}.ikBlend" 0;'.format(handle)
                self.mel_command[5] = 'setAttr "{}.ikBlend" 1;'.format(handle)
                mel.eval(''.join(self.mel_command))
                cmds.setKeyframe(self.polar)
                cmds.select(selected)
