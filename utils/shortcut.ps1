param ($target, $linkname, $workingdir)
#write-host $target
#write-host $linkname
#write-host $workingdir

$s=(New-Object -COM WScript.Shell).CreateShortcut($linkname)
$s.TargetPath="$((Resolve-Path $target).Path)"
$s.WorkingDirectory="$((Resolve-Path $workingdir).Path)"
$s.WindowStyle=7
#$s
$s.Save()