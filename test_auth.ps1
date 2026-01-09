# API test script
$timestamp = Get-Random -Minimum 1000 -Maximum 9999
$email = "test_$timestamp@example.com"

$body = @{
    firstName = "TestUser"
    lastName = "Test"
    email = $email
    password = "Test123456"
    phone = "5551234567"
} | ConvertTo-Json

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Testing Signup API" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Email: $email" -ForegroundColor Yellow
Write-Host ""

try {
    $response = Invoke-WebRequest -Uri 'http://localhost:5000/api/auth/signup' `
        -Method POST `
        -ContentType 'application/json' `
        -Body $body `
        -ErrorAction Stop
    
    Write-Host "✓ Success (Status $($response.StatusCode))" -ForegroundColor Green
    $result = $response.Content | ConvertFrom-Json
    Write-Host "Response:" -ForegroundColor Yellow
    Write-Host ($result | ConvertTo-Json | Out-String) -ForegroundColor White
    
    # Test login
    Write-Host ""
    Write-Host "=========================================" -ForegroundColor Cyan
    Write-Host "Testing Login API" -ForegroundColor Cyan
    Write-Host "=========================================" -ForegroundColor Cyan
    
    $loginBody = @{
        email = $email
        password = "Test123456"
    } | ConvertTo-Json
    
    $loginResponse = Invoke-WebRequest -Uri 'http://localhost:5000/api/auth/login' `
        -Method POST `
        -ContentType 'application/json' `
        -Body $loginBody `
        -ErrorAction Stop
    
    Write-Host "✓ Success (Status $($loginResponse.StatusCode))" -ForegroundColor Green
    $loginResult = $loginResponse.Content | ConvertFrom-Json
    Write-Host "Response:" -ForegroundColor Yellow
    Write-Host ($loginResult | ConvertTo-Json | Out-String) -ForegroundColor White
    
} catch {
    Write-Host "✗ Error" -ForegroundColor Red
    Write-Host "Status: $($_.Exception.Response.StatusCode.Value)" -ForegroundColor Red
    
    try {
        $errorBody = $_.ErrorDetails.Message
        $errorContent = $_ | ConvertFrom-Json
        Write-Host "Error: $($errorContent.error)" -ForegroundColor Red
    } catch {
        Write-Host "Response: $($_)" -ForegroundColor Red
    }
}
