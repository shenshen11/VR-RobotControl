"""
生成自签名 SSL 证书
用于 WebSocket Secure (WSS) 连接
"""
import os
import sys


def generate_certificate():
    """生成自签名证书"""
    
    print("🔐 生成自签名 SSL 证书...")
    print("=" * 60)
    
    # 检查是否已存在证书
    if os.path.exists('cert.pem') and os.path.exists('key.pem'):
        print("⚠️  证书文件已存在:")
        print("   - cert.pem")
        print("   - key.pem")
        
        response = input("\n是否覆盖现有证书？(y/N): ").strip().lower()
        if response != 'y':
            print("❌ 已取消")
            return False
    
    # 使用 OpenSSL 生成证书
    try:
        import subprocess
        
        print("\n📝 生成证书...")
        
        # 生成私钥和证书
        cmd = [
            'openssl', 'req', '-x509', '-newkey', 'rsa:4096',
            '-keyout', 'key.pem', '-out', 'cert.pem',
            '-days', '365', '-nodes',
            '-subj', '/CN=localhost'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 证书生成成功！")
            print("\n生成的文件:")
            print("   - cert.pem (证书)")
            print("   - key.pem (私钥)")
            print("\n⚠️  注意:")
            print("   - 这是自签名证书，浏览器会显示安全警告")
            print("   - 在浏览器中点击 '高级' → '继续访问' 即可")
            print("   - 证书有效期: 365 天")
            return True
        else:
            print(f"❌ 生成失败: {result.stderr}")
            print("\n尝试使用 Python 生成证书...")
            return generate_with_python()
            
    except FileNotFoundError:
        print("❌ 未找到 OpenSSL")
        print("尝试使用 Python 生成证书...")
        return generate_with_python()


def generate_with_python():
    """使用 Python cryptography 库生成证书"""
    
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
        import datetime
        
        print("\n📝 使用 Python cryptography 生成证书...")
        
        # 生成私钥
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # 生成证书
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=365)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName(u"localhost"),
                x509.DNSName(u"*.local"),
                x509.IPAddress(ipaddress.IPv4Address(u"127.0.0.1")),
            ]),
            critical=False,
        ).sign(private_key, hashes.SHA256())
        
        # 保存私钥
        with open("key.pem", "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        # 保存证书
        with open("cert.pem", "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        print("✅ 证书生成成功！")
        print("\n生成的文件:")
        print("   - cert.pem (证书)")
        print("   - key.pem (私钥)")
        return True
        
    except ImportError:
        print("\n❌ 未安装 cryptography 库")
        print("\n请安装:")
        print("   pip install cryptography")
        print("\n或使用 OpenSSL:")
        print("   openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj '/CN=localhost'")
        return False
    except Exception as e:
        print(f"\n❌ 生成失败: {e}")
        return False


if __name__ == "__main__":
    try:
        import ipaddress
        success = generate_certificate()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ 已取消")
        sys.exit(1)

