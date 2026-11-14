'  SONA XEROX - make sure the print listener is running (starts it invisibly if it is not)
'  Safe to run any time: if the listener is already running, it does nothing.
'  install-autostart.bat runs this file every minute, so the listener comes back by itself
'  after a restart, a crash, or if somebody closes it by mistake.

Set fso = CreateObject("Scripting.FileSystemObject")
folder = fso.GetParentFolderName(WScript.ScriptFullName)

running = False
Set wmi = GetObject("winmgmts:\\.\root\cimv2")
Set procs = wmi.ExecQuery("SELECT CommandLine FROM Win32_Process WHERE Name='pythonw.exe' OR Name='python.exe'")
For Each p In procs
  If Not IsNull(p.CommandLine) Then
    If InStr(LCase(p.CommandLine), "listener.py") > 0 Then running = True
  End If
Next

If Not running Then
  Set shell = CreateObject("WScript.Shell")
  shell.CurrentDirectory = folder
  shell.Run "pythonw listener.py", 0, False
End If
