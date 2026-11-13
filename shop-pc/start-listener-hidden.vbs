' SONA XEROX — start the print listener INVISIBLY in the background
' Double-click this file to start. No window will appear.
' To check it's running: open Task Manager -> look for "pythonw.exe",
' or open listener.log in this folder to see live activity.
' To stop it: double-click stop-listener.bat

Set fso = CreateObject("Scripting.FileSystemObject")
folder = fso.GetParentFolderName(WScript.ScriptFullName)

Set shell = CreateObject("WScript.Shell")
shell.CurrentDirectory = folder
' pythonw = python without a console window
shell.Run "pythonw listener.py", 0, False
