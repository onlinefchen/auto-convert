#!/usr/bin/env python3
"""
Upload configuration files to private GitHub Gist and generate QR codes
"""

import json
import os
import sys
import qrcode
from github import Github
from datetime import datetime
import argparse

class GistUploader:
    def __init__(self, token=None):
        """Initialize with GitHub token"""
        self.token = token or os.getenv('GITHUB_TOKEN')
        if not self.token:
            print("❌ GitHub token not found!")
            print("请设置环境变量 GITHUB_TOKEN 或使用 --token 参数")
            print("获取token: https://github.com/settings/tokens")
            print("需要的权限: gist")
            sys.exit(1)
        
        try:
            self.github = Github(self.token)
            # Test authentication
            self.github.get_user().login
            print("✅ GitHub 认证成功")
        except Exception as e:
            print(f"❌ GitHub 认证失败: {e}")
            sys.exit(1)
    
    def upload_files(self, files, description=None, public=False):
        """Upload files to GitHub Gist"""
        if not files:
            print("❌ 没有找到要上传的文件")
            return None
        
        # Prepare gist files
        gist_files = {}
        for file_path in files:
            if not os.path.exists(file_path):
                print(f"⚠️  文件不存在: {file_path}")
                continue
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            filename = os.path.basename(file_path)
            gist_files[filename] = {
                'content': content
            }
        
        if not gist_files:
            print("❌ 没有有效的文件可上传")
            return None
        
        # Create description
        if not description:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            description = f"Proxy Config - Generated at {timestamp}"
        
        try:
            print(f"📤 上传 {len(gist_files)} 个文件到 GitHub Gist...")
            gist = self.github.get_user().create_gist(
                public=public,
                files=gist_files,
                description=description
            )
            
            print(f"✅ 上传成功!")
            print(f"🔗 Gist URL: {gist.html_url}")
            
            return gist
            
        except Exception as e:
            print(f"❌ 上传失败: {e}")
            return None
    
    def get_raw_urls(self, gist):
        """Get raw URLs for gist files"""
        raw_urls = {}
        for filename, file_obj in gist.files.items():
            raw_urls[filename] = file_obj.raw_url
        return raw_urls
    
    def generate_qr_codes(self, urls, output_dir="qr_codes"):
        """Generate QR codes for URLs"""
        os.makedirs(output_dir, exist_ok=True)
        
        for filename, url in urls.items():
            print(f"📱 生成二维码: {filename}")
            
            # Create QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(url)
            qr.make(fit=True)
            
            # Create image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Save QR code
            qr_filename = f"{os.path.splitext(filename)[0]}_qr.png"
            qr_path = os.path.join(output_dir, qr_filename)
            img.save(qr_path)
            
            print(f"✅ 二维码已保存: {qr_path}")
            print(f"📱 扫描此二维码导入 {filename}")
            print(f"🔗 直链: {url}")
            print()

def main():
    parser = argparse.ArgumentParser(description='Upload config files to private GitHub Gist')
    parser.add_argument('files', nargs='+', help='Config files to upload')
    parser.add_argument('--token', help='GitHub personal access token')
    parser.add_argument('--public', action='store_true', help='Make gist public (NOT recommended)')
    parser.add_argument('--description', help='Gist description')
    parser.add_argument('--qr-dir', default='qr_codes', help='QR codes output directory')
    
    args = parser.parse_args()
    
    # Initialize uploader
    uploader = GistUploader(args.token)
    
    # Upload files
    gist = uploader.upload_files(
        files=args.files,
        description=args.description,
        public=args.public
    )
    
    if not gist:
        sys.exit(1)
    
    # Get raw URLs
    raw_urls = uploader.get_raw_urls(gist)
    
    # Generate QR codes
    uploader.generate_qr_codes(raw_urls, args.qr_dir)
    
    print("🎉 完成!")
    print(f"📱 二维码保存在: {args.qr_dir}/")
    print(f"🔗 Gist地址: {gist.html_url}")
    
    if not args.public:
        print("🔒 这是私有Gist，只有知道链接的人才能访问")

if __name__ == '__main__':
    main()