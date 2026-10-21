<#
.SYNOPSIS
Deploys the VoiceGuard India full stack to AWS using the AWS CLI.
It deploys the static frontend to an S3 Website and the FastAPI Backend to an EC2 Instance.
#>

$ErrorActionPreference = "Stop"

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host " VoiceGuard India - AWS Cloud Deployment " -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# 0. Get Current AWS Region
$awsRegion = (aws configure get region)
if (-not $awsRegion) { $awsRegion = "us-east-1" }
Write-Host "Detected AWS Region: $awsRegion" -ForegroundColor Cyan

# 1. Generate Unique Names
$rand = Get-Random -Minimum 1000 -Maximum 99999
$bucketName = "voiceguard-frontend-$rand"
$sgName = "voiceguard-sg-$rand"

# 2. S3 Bucket Deployment (Frontend + Asset Hosting)
Write-Host "`n[1/4] Creating S3 Bucket ($bucketName) for Frontend Hosting..." -ForegroundColor Yellow
aws s3 mb s3://$bucketName --region $awsRegion

Write-Host "Configuring S3 Bucket for Static Website Hosting..." -ForegroundColor Yellow
aws s3 website s3://$bucketName/ --index-document index.html

Write-Host "Applying Public Read Bucket Policy..." -ForegroundColor Yellow
aws s3api put-public-access-block --bucket $bucketName --public-access-block-configuration "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false" --region $awsRegion

$policy = @"
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::$bucketName/*"
        }
    ]
}
"@
$policy | Out-File policy.json -Encoding ascii
aws s3api put-bucket-policy --bucket $bucketName --policy file://policy.json --region $awsRegion
Remove-Item policy.json

Write-Host "Syncing Frontend Files to S3..." -ForegroundColor Yellow
aws s3 sync . s3://$bucketName --exclude ".git/*" --exclude "Agentic GIT/*" --exclude "voiceguard-india/*" --exclude "venv/*" --exclude "*.zip" --exclude "*.ps1"

$s3Url = "http://$bucketName.s3-website.$awsRegion.amazonaws.com"
Write-Host "Frontend successfully deployed! URL: $s3Url" -ForegroundColor Green

# 3. Package Backend 
Write-Host "`n[2/4] Packaging Backend ML Pipeline for EC2..." -ForegroundColor Yellow
if (Test-Path "backend.zip") { Remove-Item "backend.zip" -Force }
Compress-Archive -Path "Agentic GIT/GIFT_IFIH_2026/voiceguard_backend", "Agentic GIT/GIFT_IFIH_2026/ml_engine" -DestinationPath backend.zip -Force
aws s3 cp backend.zip s3://$bucketName/backend.zip

# 4. EC2 Security Group
Write-Host "`n[3/4] Provisioning EC2 Security Group..." -ForegroundColor Yellow
$sgId = aws ec2 create-security-group --group-name $sgName --description "VoiceGuard Backend Security Group" --query "GroupId" --output text --region $awsRegion
aws ec2 authorize-security-group-ingress --group-id $sgId --protocol tcp --port 80 --cidr 0.0.0.0/0 --region $awsRegion | Out-Null
aws ec2 authorize-security-group-ingress --group-id $sgId --protocol tcp --port 22 --cidr 0.0.0.0/0 --region $awsRegion | Out-Null

# 5. EC2 Instance Deployment
Write-Host "`n[4/4] Launching EC2 Backend Server..." -ForegroundColor Yellow
$amiId = aws ssm get-parameters --names /aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2 --query "Parameters[0].Value" --output text --region $awsRegion

$userData = @"
#!/bin/bash
# System Updates & Dependencies
yum update -y
yum install -y python3 unzip gcc gcc-c++ python3-devel mesa-libGL
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
./aws/install

# Setup Application
mkdir /app
cd /app
# Download backend source code from our public S3 bucket
curl -O $s3Url/backend.zip
unzip backend.zip

# Install ML Dependencies
pip3 install --upgrade pip
pip3 install fastapi uvicorn python-multipart librosa scikit-learn numpy pydantic

# Redirect Port 80 to FastAPI's 8000
iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8000

# Start Backend Daemon
export PYTHONPATH=/app
nohup python3 -m uvicorn voiceguard_backend.api:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
"@

$userDataBase64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($userData))

$instanceId = aws ec2 run-instances --image-id $amiId --instance-type t3.medium --security-group-ids $sgId --user-data $userDataBase64 --query "Instances[0].InstanceId" --output text --region $awsRegion

Write-Host "EC2 Instance ($instanceId) provisioning..." -ForegroundColor Cyan
aws ec2 wait instance-running --instance-ids $instanceId --region $awsRegion
$publicIp = aws ec2 describe-instances --instance-ids $instanceId --query "Reservations[0].Instances[0].PublicIpAddress" --output text --region $awsRegion

Write-Host "`n=============================================" -ForegroundColor Green
Write-Host " DEPLOYMENT COMPLETED SUCCESSFULLY! " -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host "FRONTEND URL: $s3Url"
Write-Host "BACKEND API:  http://$publicIp/api/detect"
Write-Host "`nNote: The backend ML dependencies (librosa/scikit-learn) take roughly 3-4 minutes to install upon boot." -ForegroundColor Yellow
Write-Host "Please wait 4 minutes, then update admin.html's fetch URL from localhost to http://$publicIp/api/detect to go fully live!" -ForegroundColor Yellow
