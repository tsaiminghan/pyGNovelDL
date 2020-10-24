"""# param([string]$deviceName,
   #   [System.IO.FileInfo]$copyFrom,
   #   [string]$copyTo)

Write-Host '+------------------------------'
Write-Host "| DeviceName: $deviceName"
Write-Host "| copyFrom: $copyFrom"
Write-Host "| copyTo: $copyTo"
Write-Host '+------------------------------'

function Check-File-Exist {
  param (
    $DestFolder,
	$FileName
  )
  $Ret = $DestFolder.GetFolder.items() | where { $_.name -eq $FileName }
  return ($Ret -ne $null)
}
function Wait-Copy-Finish {
  param (
     $DestFolder,
	 $FileName
  )
  $i = 0
  DO {
    Sleep -Milliseconds 100
    $i += 1
    if ($i -gt 20) {
      Write-Host Warning! Copy File timeout
      exit -1
    }    
  } While ( -Not (Check-File-Exist $DestFolder $FileName))
}
function Delete-Item {
  param (
     $DestFolder,
	 $FileName
  )
  $Remove = $DestFolder.GetFolder.items() | where { $_.name -eq $FileName }
  $Remove.invokeVerb("delete")
}

$Shell = New-Object -ComObject Shell.Application

$PhoneObject = $shell.NameSpace(17).self.GetFolder.items() | where { $_.name -eq $deviceName }

if ($PhoneObject -eq $null) {
  Write-Host No device $phoneName
  exit -1
}

$Internal = $PhoneObject.GetFolder.items().Item(0) # default, others are extern sdcard

if ($Internal -eq $null) {
  Write-Host Please enable MTP.
  exit -1
}

$DestFolder = $Shell.NameSpace((join-path -path $Internal.Path $copyTo)).self

$FileName = $copyFrom.Name

if (Check-File-Exist $DestFolder $FileName) {
  $DestFolder.GetFolder.CopyHere($copyFrom.FullName)
  Start-Sleep 2
} else {
  $DestFolder.GetFolder.CopyHere($copyFrom.FullName)
  Wait-Copy-Finish $DestFolder $FileName
}"""
