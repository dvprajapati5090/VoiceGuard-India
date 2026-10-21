$ErrorActionPreference = "Stop"

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host " VoiceGuard India - AWS EC2 Hotfix Deployment " -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

$awsRegion = "ap-south-1"
$bucketName = "voiceguard-frontend-90083"
$s3Url = "http://$bucketName.s3-website.$awsRegion.amazonaws.com"
$sgName = "voiceguard-sg-$(Get-Random -Minimum 1000 -Maximum 99999)"

Write-Host "1. Zipping backend and updating S3..." -ForegroundColor Yellow
if (Test-Path "backend.zip") { Remove-Item "backend.zip" -Force }
Compress-Archive -Path "Agentic GIT/GIFT_IFIH_2026/voiceguard_backend", "Agentic GIT/GIFT_IFIH_2026/ml_engine" -DestinationPath backend.zip -Force
aws s3 cp backend.zip s3://$bucketName/backend.zip --region $awsRegion

Write-Host "`n2. Provisioning Ubuntu 24.04 Security Group..." -ForegroundColor Yellow
$sgId = aws ec2 create-security-group --group-name $sgName --description "VoiceGuard Ubuntu SG" --query "GroupId" --output text --region $awsRegion
aws ec2 authorize-security-group-ingress --group-id $sgId --protocol tcp --port 80 --cidr 0.0.0.0/0 --region $awsRegion | Out-Null
aws ec2 authorize-security-group-ingress --group-id $sgId --protocol tcp --port 22 --cidr 0.0.0.0/0 --region $awsRegion | Out-Null

Write-Host "`n3. Launching Ubuntu EC2 Backend Server (Python 3.12)..." -ForegroundColor Yellow
$amiId = aws ec2 describe-images --owners 099720109477 --filters "Name=name,Values=ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*" --query 'sort_by(Images, &CreationDate)[-1].ImageId' --output text --region $awsRegion

$userData = @"
#!/bin/bash
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y python3-pip python3-venv unzip curl build-essential libsndfile1
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
./aws/install

mkdir /app
cd /app
curl -O $s3Url/backend.zip
unzip backend.zip

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install fastapi uvicorn python-multipart librosa scikit-learn numpy pydantic

iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8000

export PYTHONPATH=/app
nohup python -m uvicorn voiceguard_backend.api:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
"@

$userDataBase64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($userData))

$instanceId = aws ec2 run-instances --image-id $amiId --instance-type t3.medium --security-group-ids $sgId --user-data $userDataBase64 --query "Instances[0].InstanceId" --output text --region $awsRegion

Write-Host "EC2 Instance ($instanceId) provisioning..." -ForegroundColor Cyan
aws ec2 wait instance-running --instance-ids $instanceId --region $awsRegion
$publicIp = aws ec2 describe-instances --instance-ids $instanceId --query "Reservations[0].Instances[0].PublicIpAddress" --output text --region $awsRegion

Write-Host "`n4. Patching Frontend HTML with new Ubuntu IP ($publicIp)..." -ForegroundColor Yellow
(Get-Content admin.html) -replace 'http://65.2.79.32/api/detect', "http://$publicIp/api/detect" | Set-Content admin.html
(Get-Content voiceguard_frontend/live_mic.js) -replace 'http://65.2.79.32/api/detect', "http://$publicIp/api/detect" | Set-Content voiceguard_frontend/live_mic.js

aws s3 cp admin.html s3://$bucketName/admin.html --region $awsRegion
aws s3 cp voiceguard_frontend/live_mic.js s3://$bucketName/voiceguard_frontend/live_mic.js --region $awsRegion

Write-Host "`n=============================================" -ForegroundColor Green
Write-Host " HOTFIX DEPLOYMENT COMPLETED! " -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host "FRONTEND URL: $s3Url/admin.html"
Write-Host "Wait 4 minutes for Ubuntu to install the heavy Python packages, then refresh your browser!" -ForegroundColor Yellow
