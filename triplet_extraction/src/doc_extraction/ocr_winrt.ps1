param(
    [Parameter(Mandatory = $true)]
    [string]$FilePath,

    [Parameter(Mandatory = $true)]
    [string]$Language
)

# Set UTF-8 encoding for output
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

Add-Type -AssemblyName System.Runtime.WindowsRuntime

[void][Windows.Media.Ocr.OcrEngine,Windows.Media.Ocr,ContentType=WindowsRuntime]
[void][Windows.Storage.StorageFile,Windows.Storage,ContentType=WindowsRuntime]
[void][Windows.Graphics.Imaging.BitmapDecoder,Windows.Graphics.Imaging,ContentType=WindowsRuntime]

$asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() |
    Where-Object {
        $_.Name -eq 'AsTask' -and
        $_.GetParameters().Count -eq 1 -and
        $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1'
    }
)[0]

try {
    $StorageFileAsync = [Windows.Storage.StorageFile]::GetFileFromPathAsync($FilePath)
    $StorageFile = $asTaskGeneric.MakeGenericMethod(
        [Windows.Storage.StorageFile]
    ).Invoke($null, $StorageFileAsync).Result

    $StreamAsync = $StorageFile.OpenReadAsync()
    $Stream = $asTaskGeneric.MakeGenericMethod(
        [Windows.Storage.Streams.IRandomAccessStreamWithContentType]
    ).Invoke($null, $StreamAsync).Result

    $BitmapDecoderAsync = [Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($Stream)
    $BitmapDecoder = $asTaskGeneric.MakeGenericMethod(
        [Windows.Graphics.Imaging.BitmapDecoder]
    ).Invoke($null, $BitmapDecoderAsync).Result

    $SoftwareBitmapAsync = $BitmapDecoder.GetSoftwareBitmapAsync()
    $SoftwareBitmap = $asTaskGeneric.MakeGenericMethod(
        [Windows.Graphics.Imaging.SoftwareBitmap]
    ).Invoke($null, $SoftwareBitmapAsync).Result

    $OCR = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage($Language)
    if (-not $OCR) {
        throw "OCR language not installed: $Language"
    }

    $OCRResultAsync = $OCR.RecognizeAsync($SoftwareBitmap)
    $OCRResult = $asTaskGeneric.MakeGenericMethod(
        [Windows.Media.Ocr.OcrResult]
    ).Invoke($null, $OCRResultAsync).Result

    Write-Output $OCRResult.Text
}
catch {
    Write-Error $_.Exception.Message
    exit 1
}