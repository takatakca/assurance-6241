param([string]$JobsPath)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Runtime.WindowsRuntime
[Windows.Storage.StorageFile,Windows.Storage,ContentType=WindowsRuntime] | Out-Null
[Windows.Graphics.Imaging.BitmapDecoder,Windows.Foundation,ContentType=WindowsRuntime] | Out-Null
[Windows.Media.Ocr.OcrEngine,Windows.Foundation,ContentType=WindowsRuntime] | Out-Null
[Windows.Globalization.Language,Windows.Globalization,ContentType=WindowsRuntime] | Out-Null
$asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.IsGenericMethod -and $_.GetGenericArguments().Count -eq 1 })[0]
function Await-WinRt($Operation, [Type]$ResultType) {
    $task = $asTaskGeneric.MakeGenericMethod($ResultType).Invoke($null, @($Operation))
    $task.Wait()
    return $task.Result
}
$language = [Windows.Globalization.Language]::new('en-US')
$engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage($language)
if ($null -eq $engine) { throw 'Windows OCR unavailable' }
$jobs = Get-Content -LiteralPath $JobsPath -Raw -Encoding UTF8 | ConvertFrom-Json
$results = @(); $counter = 0
foreach ($job in $jobs) {
    $row = [ordered]@{id=$job.id;page=$job.page;method='Windows OCR';language='en-US';output=$job.output;status='';characters=0;error=$null}
    try {
        $file = Await-WinRt ([Windows.Storage.StorageFile]::GetFileFromPathAsync($job.image)) ([Windows.Storage.StorageFile])
        $stream = Await-WinRt ($file.OpenReadAsync()) ([Windows.Storage.Streams.IRandomAccessStreamWithContentType])
        $decoder = Await-WinRt ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
        $bitmap = Await-WinRt ($decoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
        $result = Await-WinRt ($engine.RecognizeAsync($bitmap)) ([Windows.Media.Ocr.OcrResult])
        $lines = ($result.Lines | ForEach-Object { $_.Text }) -join "`r`n"
        [System.IO.File]::WriteAllText($job.output,$lines,[System.Text.UTF8Encoding]::new($false))
        $row.status = 'OCR automatique à contrôler visuellement'; $row.characters = $lines.Length
        $bitmap.Dispose(); $stream.Dispose()
    } catch { $row.status='Échec OCR'; $row.error=$_.Exception.Message }
    $results += [pscustomobject]$row
    $counter++
    if ($counter % 20 -eq 0) { Write-Output "$counter / $($jobs.Count) images traitées" }
}
$dest = Join-Path (Split-Path $JobsPath -Parent) 'ocr-resultats.json'
$results | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $dest -Encoding UTF8
Write-Output "Résultats : $dest"
