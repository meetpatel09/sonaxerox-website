'  SONA XEROX - make sure the print listener is running
'  Starts the listener invisibly. If one is already running, the new copy notices (the listener
'  allows only ONE copy on the PC) and closes by itself, so this is safe to run as often as you like.
'  install-autostart.bat runs this file every minute, so the listener comes back by itself
'  after a restart, a crash, or if somebody closes it by mistake.

Set fso = CreateObject("Scripting.FileSystemObject")
folder = fso.GetParentFolderName(WScript.ScriptFullName)
Set shell = CreateObject("WScript.Shell")
shell.CurrentDirectory = folder
shell.Run "pythonw listener.py", 0, False
