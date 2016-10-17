import maya.cmds as cmds
import maya.mel as mel

windowID = 'PlayView'
helpID = 'PlayViewHelp'
custom_viewport = ""  # Saves modelEditor name for future playback

"""
cmds.lsUI(windows=True)
Primary window: "MayaWindow"

cmds.panel(panelname, q=True, control=True)

cmds.paneLayout(controlname, q=True, configuration=True)
    "single",
    "horizontal2", "vertical2",
    "horizontal3", "vertical3",
    "top3", "left3", "bottom3", "right3",
    "horizontal4", "vertical4", "top4", "left4", "bottom4", "right4",
    "quad"

cmds.layout(layoutname, q=True, configuration=True) == "single"

cmds.window(windowname, q=True, tlc=True, wh=True)

cmds.setFocus(panelname)

scale elements by 0.15 (1920/1080 -> 288/162)

"""
