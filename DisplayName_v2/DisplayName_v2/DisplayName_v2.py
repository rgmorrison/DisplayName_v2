import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging

#
# DisplayName_v2
#

class DisplayName_v2(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "DisplayName_v2" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Examples"]
    self.parent.dependencies = []
    self.parent.contributors = ["John Doe (AnyWare Corp.)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
This is an example of scripted loadable module bundled in an extension.
It performs a simple thresholding on the input volume and optionally captures a screenshot.
"""
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """
This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.

#
# DisplayName_v2Widget
#

class DisplayName_v2Widget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)
    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Update"
    self.layout.addWidget(parametersCollapsibleButton)
    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)
    
    #
    # Start Button
    #
    self.startButton = qt.QPushButton("Start")
    self.startButton.toolTip = "Run the algorithm."
    self.startButton.enabled = True
    parametersFormLayout.addRow(self.startButton)
    # connections
    self.startButton.connect('clicked(bool)', self.onstartButton)

    #
    # Stop Button
    #
    self.stopButton = qt.QPushButton("Stop")
    self.stopButton.toolTip = "Stop the algorithm."
    self.stopButton.enabled = True
    parametersFormLayout.addRow(self.stopButton)
    # connections
    self.stopButton.connect('clicked(bool)', self.onstopButton)
    
    # Add vertical spacer
    self.layout.addStretch(1)

    self.logic = DisplayName_v2Logic()

  def cleanup(self):
    pass

  def onstartButton(self):
    self.logic.setupCrossHairTracker()

  def onstopButton(self):
    self.logic.stopCrossHairTracker()


#
# DisplayName_v2Logic
#

class DisplayName_v2Logic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """
  def setupCrossHairTracker(self):
    self.crosshairNode = slicer.util.getNode('Crosshair') 
    self.observationId = self.crosshairNode.AddObserver(slicer.vtkMRMLCrosshairNode.CursorPositionModifiedEvent, self.printModelName())
    print("Set up crosshair tracker")

  def stopCrossHairTracker(self):
    self.crosshairNode.RemoveObserver(self.observationId)
    print("Stopped crosshair tracker")

  def printModelName(self):
    modelDisplayableManager = None
    threeDViewWidget = slicer.app.layoutManager().threeDWidget(0)
    managers = vtk.vtkCollection()
    threeDViewWidget.getDisplayableManagers(managers)
    for i in range(managers.GetNumberOfItems()):
      obj = managers.GetItemAsObject(i)
      if obj.IsA('vtkMRMLModelDisplayableManager'):
        modelDisplayableManager = obj
        break
    if modelDisplayableManager is None:
      logging.error('Failed to find the model displayable manager')

    crosshairNode = slicer.mrmlScene.GetNodeByID("vtkMRMLCrosshairNodedefault")
    modelDisplayableManager.Pick3D(crosshairNode.GetCrosshairRAS())
    if(slicer.mrmlScene.GetNodeByID(modelDisplayableManager.GetPickedNodeID())):
      modelNode = slicer.mrmlScene.GetNodeByID(modelDisplayableManager.GetPickedNodeID()).GetDisplayableNode()
      print(modelNode.GetName())
    else:
      print("Nothing Selected")


class DisplayName_v2Test(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_DisplayName_v21()

  def test_DisplayName_v21(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")
    #
    # first, get some data
    #
    import SampleData
    SampleData.downloadFromURL(
      nodeNames='FA',
      fileNames='FA.nrrd',
      uris='http://slicer.kitware.com/midas3/download?items=5767')
    self.delayDisplay('Finished with download and loading')

    volumeNode = slicer.util.getNode(pattern="FA")
    logic = DisplayName_v2Logic()
    self.assertIsNotNone( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')
