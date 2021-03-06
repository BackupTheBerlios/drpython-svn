#	Programmer:	Daniel Pozmanter
#	E-mail:		drpython@bluebottle.com
#	Note:		You must reply to the verification e-mail to get through.
#
#	Copyright 2003-2005 Daniel Pozmanter
#
#	Distributed under the terms of the GPL (GNU Public License)
#
#    DrPython is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

#drScript Menu

import os.path
import wx
import drFileDialog
import drScrolledMessageDialog
from drPrefsFile import ExtractPreferenceFromText
import drShortcutsFile
import drShortcuts
from drMenu import drMenu

def updatescripts(scriptfile, paths, titles):
	l = len(paths)
	x = 0
	f = open(scriptfile, 'w')
	while (x < l):
		f.write("<path>" + paths[x] + "</path><title>" + titles[x] + "</title>\n")
		x = x + 1
	f.close()

class drNewShellDialog(wx.Dialog):

	def __init__(self, parent, title):
		wx.Dialog.__init__(self, parent, -1, title, wx.Point(50, 50), wx.Size(375, 250), wx.DEFAULT_DIALOG_STYLE | wx.MAXIMIZE_BOX | wx.THICK_FRAME | wx.RESIZE_BORDER)

		self.ID_SAVE = 1005

		self.theSizer = wx.FlexGridSizer(6, 3, 5, 10)

		self.btnSave = wx.Button(self, self.ID_SAVE, "&Save")

		self.parent = parent

		self.txtTitle = wx.TextCtrl(self, -1, "",  wx.Point(15, 325), wx.Size(250, -1))
		self.txtCommand = wx.TextCtrl(self, -1, "",  wx.Point(15, 325), wx.Size(250, -1))
		self.txtArguments = wx.TextCtrl(self, -1, "",  wx.Point(15, 325), wx.Size(250, -1))
		self.txtDirectory = wx.TextCtrl(self, -1, "",  wx.Point(15, 325), wx.Size(250, -1))
		self.chkRunInPrompt = wx.CheckBox(self, -1, "")
		self.chkRunInPrompt.SetValue(True)

		self.theSizer.Add(wx.StaticText(self, -1, " "), 0, wx.ALIGN_CENTER | wx.SHAPED)
		self.theSizer.Add(wx.StaticText(self, -1, " "), 0, wx.ALIGN_CENTER | wx.SHAPED)
		self.theSizer.Add(wx.StaticText(self, -1, " "), 0, wx.ALIGN_CENTER | wx.SHAPED)

		self.theSizer.Add(wx.StaticText(self, -1, " "), 0, wx.ALIGN_CENTER | wx.SHAPED)
		self.theSizer.Add(wx.StaticText(self, -1, "Title:"), 0, wx.ALIGN_CENTER | wx.SHAPED)
		self.theSizer.Add(self.txtTitle, 0, wx.SHAPED)

		self.theSizer.Add(wx.StaticText(self, -1, " "), 0, wx.ALIGN_CENTER | wx.SHAPED)
		self.theSizer.Add(wx.StaticText(self, -1, "Command:"), 0, wx.ALIGN_CENTER | wx.SHAPED)
		self.theSizer.Add(self.txtCommand, 0, wx.SHAPED)

		self.theSizer.Add(wx.StaticText(self, -1, " "), 0, wx.ALIGN_CENTER | wx.SHAPED)
		self.theSizer.Add(wx.StaticText(self, -1, "Arguments:"), 0, wx.ALIGN_CENTER | wx.SHAPED)
		self.theSizer.Add(self.txtArguments, 0, wx.SHAPED)

		self.theSizer.Add(wx.StaticText(self, -1, " "), 0, wx.ALIGN_CENTER | wx.SHAPED)
		self.theSizer.Add(wx.StaticText(self, -1, "Directory:"), 0, wx.ALIGN_CENTER | wx.SHAPED)
		self.theSizer.Add(self.txtDirectory, 0, wx.SHAPED)

		self.theSizer.Add(wx.StaticText(self, -1, " "), 0, wx.ALIGN_CENTER | wx.SHAPED)
		self.theSizer.Add(wx.StaticText(self, -1, "Run In Prompt:"), 0, wx.ALIGN_CENTER | wx.SHAPED)
		self.theSizer.Add(self.chkRunInPrompt, 0, wx.SHAPED)

		self.btnClose = wx.Button(self, 101, "&Close")
		self.theSizer.Add(wx.StaticText(self, -1, " "), 0, wx.ALIGN_CENTER | wx.SHAPED)
		self.theSizer.Add(wx.StaticText(self, -1, " "), 0, wx.ALIGN_CENTER | wx.SHAPED)
		self.theSizer.Add(wx.StaticText(self, -1, " "), 0, wx.ALIGN_CENTER | wx.SHAPED)
		self.theSizer.Add(wx.StaticText(self, -1, " "), 0, wx.ALIGN_CENTER | wx.SHAPED)
		self.theSizer.Add(self.btnClose, 0, wx.SHAPED | wx.ALIGN_CENTER)
		self.theSizer.Add(self.btnSave, 0, wx.SHAPED | wx.ALIGN_RIGHT)
		self.txtTitle.SetFocus()
		self.btnSave.SetDefault()

		self.SetAutoLayout(True)
		self.SetSizer(self.theSizer)

		self.exitstatus = 0

		self.Bind(wx.EVT_BUTTON,  self.OnbtnSave, id=self.ID_SAVE)
		self.Bind(wx.EVT_BUTTON,  self.OnbtnClose, id=101)

	def GetExitStatus(self):
		return self.exitstatus

	def GetShellTuple(self):
		return self.txtTitle.GetValue(), self.txtCommand.GetValue(), self.txtArguments.GetValue(), self.txtDirectory.GetValue(), int(self.chkRunInPrompt.GetValue())

	def OnbtnClose(self, event):
		self.exitstatus = 0
		self.Close(1)

	def OnbtnSave(self, event):
		self.exitstatus = 1
		self.Close(1)

	def SetShellTuple(self, title, command, args, dir, inprompt):
		self.txtTitle.SetValue(title)
		self.txtCommand.SetValue(command)
		self.txtArguments.SetValue(args)
		self.txtDirectory.SetValue(dir)
		self.chkRunInPrompt.SetValue(inprompt)

class drScriptMenu(drMenu):
	def __init__(self, parent):
		drMenu.__init__(self, parent)

		self.dynamicscriptext = ""

		self.ID_ADD_SCRIPT = 3100
		self.ID_NEW_SCRIPT = 3101
		self.ID_EXISTING_SCRIPT = 3102
		self.ID_SHELL_COMMAND = 3103

		self.ID_EDIT_SCRIPT = 3003
		self.ID_REMOVE_SCRIPT = 3005
		self.ID_DYNAMIC_SCRIPT = 3006

		self.ID_EXAMPLE_SCRIPTS = 3010

		self.ID_SCRIPT_BASE = parent.ID_SCRIPT_BASE

		self.ID_SCRIPT_MENU = 3500

		self.parent = parent
		self.userpreferencesdirectory = parent.userpreferencesdirectory
		self.programdirectory = parent.programdirectory

		self.scriptcount = 0
		self.scripts = []
		self.titles = []

		self.setupMenu()

		self.ExampleScriptCount = 0

		self.loadscripts()

	def getdrscriptmenulabel(self, label):
		shortcuttext = ''

		if len(self.parent.DrScriptShortcuts) == 0:
			return label

		if label in self.titles:
			i = self.titles.index(label)
			shortcuttext = drShortcuts.GetShortcutLabel(self.parent.DrScriptShortcuts[i])

		if len(shortcuttext) > 1:
			return label + '\t' + shortcuttext

		return label

	def loadscripts(self, SyncShortcuts = 1):
		self.scriptcount = 0
		if self.parent.prefs.drscriptloadexamples:
			self.examplemenu = wx.Menu()
			self.loadscriptsfromfile(self.programdirectory + "/examples/DrScript/drscript.dat", self.examplemenu, 1)
			self.AppendMenu(self.ID_EXAMPLE_SCRIPTS, "Examples", self.examplemenu)
			self.AppendSeparator()

		self.ExampleScriptCount = self.scriptcount

		self.loadscriptsfromfile(self.userpreferencesdirectory + "/drscript.dat", self)

		#Either there is no shortcuts file, or it is out of sync.
		if SyncShortcuts:
			l = len(self.titles)
			if not (l == len(self.parent.DrScriptShortcuts)):
				self.parent.DrScriptShortcuts = []
				self.parent.DrScriptShortcutNames = []

				x = 0
				while (x < l):
					self.parent.DrScriptShortcuts.append(' #')
					self.parent.DrScriptShortcutNames.append(self.titles[x])
					x = x + 1

	def loadscriptsfromfile(self, scriptfile, target, appendprogpath = 0):
		if (os.path.exists(scriptfile)):
			folders = [target]
			folderindex = 0
			menuTitles = []
			menuTitleindex = -1
			lastCount = 0
			try:
				#Read from the file
				f = open(scriptfile, 'rb')
				#Initialize
				line = f.readline()
				while (len(line) > 0):
					c = line.count('\t')
					line = line[c:].rstrip()

					while (lastCount > c):
						folders[(folderindex - 1)].AppendMenu(self.ID_SCRIPT_MENU, menuTitles.pop(), folders.pop())
						folderindex = folderindex - 1
						menuTitleindex = menuTitleindex - 1
						lastCount = lastCount - 1

					if (line[0] == '>'):
						folders.append(wx.Menu())
						menuTitles.append(line[1:])
						folderindex = folderindex + 1
						menuTitleindex = menuTitleindex + 1
						c = c + 1
					else:
						line_path = ExtractPreferenceFromText(line, "path")
						if appendprogpath:
							line_path = self.programdirectory + "/" + line_path.replace('\\', '/')
						line_title = ExtractPreferenceFromText(line, "title")
						if (os.path.exists(line_path)):
							self.titles.append(line_title)
							folders[folderindex].Append((self.ID_SCRIPT_BASE + self.scriptcount), self.getdrscriptmenulabel(line_title))
							self.parent.Bind(wx.EVT_MENU, self.OnScript, id=(self.ID_SCRIPT_BASE + self.scriptcount))
							self.scripts.append(line_path)
							self.scriptcount = self.scriptcount + 1
					lastCount = c
					line = f.readline()
				f.close()
				#Add any menus not yet added:
				c = 0
				while (lastCount > c):
					folders[(folderindex - 1)].AppendMenu(self.ID_SCRIPT_MENU, menuTitles.pop(), folders.pop())
					folderindex = folderindex - 1
					menuTitleindex = menuTitleindex - 1
					lastCount = lastCount - 1
			except:
				drScrolledMessageDialog.ShowMessage(self.parent, ("Your drscript file is a tad messed up.\n"), "Error")

	def OnAddExistingScript(self, event):
		scriptfile = self.userpreferencesdirectory + "/drscript.dat"
		dlg = drFileDialog.FileDialog(self.parent, "Select Script File", self.parent.prefs.wildcard)
		if (len(self.parent.prefs.drscriptdefaultdirectory) > 0):
			try:
				dlg.SetDirectory(self.parent.prefs.drscriptdefaultdirectory)
			except:
				drScrolledMessageDialog.ShowMessage(self.parent, ("Error Setting Default Directory To: " + self.parent.prefs.drscriptdefaultdirectory), "DrPython Error")
		if (dlg.ShowModal() == wx.ID_OK):
			filen = dlg.GetPath().replace("\\", "/")
			d = wx.TextEntryDialog(self.parent, 'Enter Script Title:', 'Add DrScript: Title', '')
			title = ""
			if (d.ShowModal() == wx.ID_OK):
				title = d.GetValue()
			d.Destroy()
			if (len(title) < 1):
				drScrolledMessageDialog.ShowMessage(self.parent, ("Bad script title.\nDrPython will politely ignore your request to add this script."), "Error")
				return
			self.Append((self.ID_SCRIPT_BASE + self.scriptcount), title, title)
			self.parent.Bind(wx.EVT_MENU, self.OnScript, id=(self.ID_SCRIPT_BASE + self.scriptcount))
			self.scripts.append(filen)
			self.titles.append(title)

			x = len(self.parent.DrScriptShortcuts)
			self.parent.DrScriptShortcuts.append('')
			self.parent.DrScriptShortcutNames.append(title)

			self.scriptcount = self.scriptcount + 1
			try:
				f = open(scriptfile, 'a')
				f.write("<path>" + filen + "</path><title>" + title + "</title>\n")
				f.close()

				#Update the shortcuts Too.
				shortcutsfile = self.userpreferencesdirectory + "/drscript.shortcuts.dat"
				drShortcutsFile.WriteShortcuts(shortcutsfile, self.parent.DrScriptShortcuts, self.parent.DrScriptShortcutNames, "", False)
			except:
				drScrolledMessageDialog.ShowMessage(self.parent, ("Problem saving script.\n"), "Error")
		dlg.Destroy()

	def OnAddNewScript(self, event):
		scriptfile = self.userpreferencesdirectory + "/drscript.dat"
		dlg = drFileDialog.FileDialog(self.parent, "Save New Script File As", self.parent.prefs.wildcard, IsASaveDialog=True)
		if (len(self.parent.prefs.drscriptdefaultdirectory) > 0):
			try:
				dlg.SetDirectory(self.parent.prefs.drscriptdefaultdirectory)
			except:
				drScrolledMessageDialog.ShowMessage(self.parent, ("Error Setting Default Directory To: " + self.parent.prefs.drscriptdefaultdirectory), "DrPython Error")
		if (dlg.ShowModal() == wx.ID_OK):
			filen = dlg.GetPath().replace("\\", "/")
			d = wx.TextEntryDialog(self.parent, "Enter Script Title:", "Add DrScript: Title", "")
			title = ""
			if (d.ShowModal() == wx.ID_OK):
				title = d.GetValue()
			d.Destroy()
			if (len(title) < 1):
				drScrolledMessageDialog.ShowMessage(self.parent, ("Bad script title.\nDrPython will politely ignore your request to add this script."), "Error")
				return

			cfile = file(filen, 'wb')
			cfile.write("#drscript\n\n")
			cfile.close()

			self.Append((self.ID_SCRIPT_BASE + self.scriptcount), title, title)
			self.parent.Bind(wx.EVT_MENU, self.OnScript, id=(self.ID_SCRIPT_BASE + self.scriptcount))
			self.scripts.append(filen)
			self.titles.append(title)

			x = len(self.parent.DrScriptShortcuts)
			self.parent.DrScriptShortcuts.append('')
			self.parent.DrScriptShortcutNames.append(title)

			self.scriptcount = self.scriptcount + 1
			try:
				f = open(scriptfile, 'a')
				f.write("<path>" + filen + "</path><title>" + title + "</title>\n")
				f.close()

				shortcutsfile = self.userpreferencesdirectory + "/drscript.shortcuts.dat"
				drShortcutsFile.WriteShortcuts(shortcutsfile, self.parent.DrScriptShortcuts, self.parent.DrScriptShortcutNames, "", False)
			except:
				drScrolledMessageDialog.ShowMessage(self.parent, ("Problem saving script.\n"), "Error")

			old = self.parent.txtDocument.filename
			filename = filen
			if (len(old) > 0) or (self.parent.txtDocument.GetModify()):
				self.parent.OpenFile(filename, True)
			else:
				self.parent.OpenFile(filename, False)
		dlg.Destroy()

	def OnAddShellCommand(self, event):
		scriptfile = self.userpreferencesdirectory + "/drscript.dat"
		dlg = drFileDialog.FileDialog(self.parent, "Save New Shell Command As", self.parent.prefs.wildcard, IsASaveDialog=True)
		if (len(self.parent.prefs.drscriptdefaultdirectory) > 0):
			try:
				dlg.SetDirectory(self.parent.prefs.drscriptdefaultdirectory)
			except:
				drScrolledMessageDialog.ShowMessage(self.parent, ("Error Setting Default Directory To: " + self.parent.prefs.drscriptdefaultdirectory), "DrPython Error")
		if (dlg.ShowModal() == wx.ID_OK):
			filen = dlg.GetPath().replace("\\", "/")
			d = drNewShellDialog(self.parent, "New Shell Command")
			if self.parent.prefs.platform_is_windows:
				d.SetSize(wx.Size(425, 350))
			d.ShowModal()
			if d.GetExitStatus():
				title, cmd, args, dir, inprompt = d.GetShellTuple()
				d.Destroy()
			else:
				d.Destroy()
				return
			if (len(title) < 1):
				drScrolledMessageDialog.ShowMessage(self.parent, ("Bad shell title.\nDrPython will politely ignore your request to add this shell command."), "Error")
				return

			if args.find("<Current File>") > -1:
				args = args.replace("<Current File>", self.parent.txtDocument.filename)
			if args.find("<Current Directory>") > -1:
				args = args.replace("<Current Directory>", os.path.split(self.parent.txtDocument.filename)[0])
			if dir.find("<Current Directory>") > -1:
				dir = dir.replace("<Current Directory>", os.path.split(self.parent.txtDocument.filename)[0])

			cfile = file(filen, 'wb')
			scripttext = "#drscript shell command\n\n"
			if len(dir) > 0:
				scripttext = scripttext + 'import os\n\nos.chdir("' + dir + '")\n\n'

			if inprompt:
				scripttext = scripttext + 'DrFrame.Execute("' + cmd + ' ' + args + '", "Running Shell Command")\n\n'
			else:
				scripttext = scripttext + 'wx.Shell("' + cmd + ' ' + args + '")\n\n'
			cfile.write(scripttext)
			cfile.close()

			self.Append((self.ID_SCRIPT_BASE + self.scriptcount), title, title)
			self.parent.Bind(wx.EVT_MENU, self.OnScript, id=(self.ID_SCRIPT_BASE + self.scriptcount))
			self.scripts.append(filen)
			self.titles.append(title)

			x = len(self.parent.DrScriptShortcuts)
			self.parent.DrScriptShortcuts.append('')
			self.parent.DrScriptShortcutNames.append(title)

			self.scriptcount = self.scriptcount + 1
			try:
				f = open(scriptfile, 'a')
				f.write("<path>" + filen + "</path><title>" + title + "</title>\n")
				f.close()

				shortcutsfile = self.userpreferencesdirectory + "/drscript.shortcuts.dat"
				drShortcutsFile.WriteShortcuts(shortcutsfile, self.parent.DrScriptShortcuts, self.parent.DrScriptShortcutNames, "", False)
			except:
				drScrolledMessageDialog.ShowMessage(self.parent, ("Problem saving script.\n"), "Error")
		dlg.Destroy()

	def OnDynamicScript(self, event):
		from drDynamicDrScriptDialog import drDynamicDrScriptDialog
		d = drDynamicDrScriptDialog(self.parent, self.dynamicscriptext)
		d.ShowModal()
		self.dynamicscriptext = d.GetText()
		d.Destroy()

	def OnEditScript(self, event):
		if (len(self.scripts) > 0):
			def tuplify(x, y):
				return (x, y)

			def detuplify(x):
				return x[0]

			array = map(tuplify, self.titles, self.scripts)
			array.sort()

			titles = map(detuplify, array)
			d = wx.SingleChoiceDialog(self.parent, "Select the Script to Edit:", "Edit Script", titles, wx.OK|wx.CANCEL)
			d.SetSize(wx.Size(250, 250))
			answer = d.ShowModal()
			d.Destroy()
			if (answer == wx.ID_OK):
				i = d.GetSelection()
				old = self.parent.txtDocument.filename
				filename = array[i][1].replace("\\", "/")
				alreadyopen = map(lambda x: x.filename.replace("\\", "/"), self.parent.txtDocumentArray)
				if filename in alreadyopen:
					self.parent.setDocumentTo(alreadyopen.index(filename))
					return
				if (len(old) > 0) or (self.parent.txtDocument.GetModify()):
					self.parent.OpenFile(filename, True, False)
				else:
					self.parent.OpenFile(filename, False, False)
		else:
			drScrolledMessageDialog.ShowMessage(self.parent, ("There aren't any scripts to edit.\nTry \"New Script\" or \"Add Script\" Instead."), "Error")

	def OnScript(self, event):
		scriptindex = event.GetId() - self.ID_SCRIPT_BASE
		f = open(self.scripts[scriptindex], 'r')
		scripttext = f.read()
		f.close()

		if (scripttext.find("DrFilename") > -1):
			scripttext = scripttext.replace("DrFilename", "self.parent.txtDocument.filename")
		if (scripttext.find("DrScript") > -1):
			scripttext = scripttext.replace("DrScript", "self.parent.DrScript")
		if (scripttext.find("DrDocument") > -1):
			scripttext = scripttext.replace("DrDocument", "self.parent.txtDocument")
		if (scripttext.find("DrPrompt") > -1):
			scripttext = scripttext.replace("DrPrompt", "self.parent.txtPrompt")
		if (scripttext.find("DrFrame") > -1):
			scripttext = scripttext.replace("DrFrame", "self.parent")

		try:
			code = compile((scripttext + '\n'), self.scripts[scriptindex], 'exec')
		except:
			drScrolledMessageDialog.ShowMessage(self.parent, ("Error compiling script."), "Error", wx.DefaultPosition, wx.Size(550,300))
			return

		try:
			exec(code)
		except:
			drScrolledMessageDialog.ShowMessage(self.parent, ("Error running script."), "Error", wx.DefaultPosition, wx.Size(550,300))
			return

	def setupMenu(self):
		addscriptmenu = wx.Menu()
		addscriptmenu.Append(self.ID_NEW_SCRIPT, "&New Script...")
		addscriptmenu.Append(self.ID_EXISTING_SCRIPT, "&Existing Script...")
		addscriptmenu.Append(self.ID_SHELL_COMMAND, "&Shell Command...")

		self.AppendMenu(self.ID_ADD_SCRIPT, "&Add Script", addscriptmenu)
		self.Append(self.ID_EDIT_SCRIPT, "&Edit Script...")
		self.Append(self.ID_DYNAMIC_SCRIPT, "&Dynamic DrScript...")
		self.AppendSeparator()

		self.parent.Bind(wx.EVT_MENU, self.OnAddExistingScript, id=self.ID_EXISTING_SCRIPT)
		self.parent.Bind(wx.EVT_MENU, self.OnAddNewScript, id=self.ID_NEW_SCRIPT)
		self.parent.Bind(wx.EVT_MENU, self.OnAddShellCommand, id=self.ID_SHELL_COMMAND)
		self.parent.Bind(wx.EVT_MENU, self.OnEditScript, id=self.ID_EDIT_SCRIPT)
		self.parent.Bind(wx.EVT_MENU, self.OnDynamicScript, id=self.ID_DYNAMIC_SCRIPT)

	def reloadscripts(self, oldlength = -1, SyncShortcuts = 1):
		if oldlength < 0:
			oldlength = len(self.scripts)
		mnuitems = self.GetMenuItems()
		num = len(mnuitems)
		x = 0
		while (x < num):
			self.Remove(mnuitems[x].GetId())
			#mnuitems[x].Destroy()
			x = x + 1
		self.scripts = []
		self.titles = []
		self.setupMenu()
		self.loadscripts(SyncShortcuts)
