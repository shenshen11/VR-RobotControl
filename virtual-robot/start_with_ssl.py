"""
启动脚本 - 自动生成证书并启动服务器
"""
import os
import sys
import subprocess


def check_certificates():
    """检查证书是否存在"""
    return os.path.exists('cert.pem') and os.path.exists('key.pem')


def generate_certificates():
    """生成证书"""
    print("🔐 证书文件不存在，正在生成...")

    # 优先使用 Python 生成（支持多 IP）
    return try_python_generation()


def get_local_ips():
    """获取本机所有 IP 地址"""
    import socket
    ips = []

    try:
        # 获取主机名
        hostname = socket.gethostname()

        # 获取所有 IP 地址
        for info in socket.getaddrinfo(hostname, None):
            ip = info[4][0]
            if ip not in ips and not ip.startswith('fe80'):  # 排除 IPv6 链路本地地址
                ips.append(ip)

        # 尝试通过连接外部地址获取主 IP
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            main_ip = s.getsockname()[0]
            s.close()
            if main_ip not in ips:
                ips.insert(0, main_ip)
        except:
            pass

    except:
        pass

    return ips


def try_python_generation():
    """使用 Python 生成证书"""
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
        import datetime
        import ipaddress

        print("📝 使用 Python cryptography 生成证书...")

        # 获取本机 IP
        local_ips = get_local_ips()
        print(f"   检测到本机 IP: {', '.join(local_ips) if local_ips else '无'}")

        # 生成私钥
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )

        # 生成证书
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, u"VR Robot Server"),
        ])

        # 构建 SAN 列表（包含所有 IP 和域名）
        san_list = [
            x509.DNSName(u"localhost"),
            x509.DNSName(u"*.local"),
            x509.IPAddress(ipaddress.IPv4Address(u"127.0.0.1")),
        ]

        # 添加所有本机 IP
        for ip in local_ips:
            try:
                # 尝试解析为 IPv4
                san_list.append(x509.IPAddress(ipaddress.IPv4Address(ip)))
                print(f"   添加 IPv4 到证书: {ip}")
            except:
                try:
                    # 尝试解析为 IPv6
                    san_list.append(x509.IPAddress(ipaddress.IPv6Address(ip)))
                    print(f"   添加 IPv6 到证书: {ip}")
                except:
                    pass

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
            x509.SubjectAlternativeName(san_list),
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
        return True
        
    except ImportError:
        print("\n❌ 未安装 cryptography 库")
        print("\n请选择以下方式之一:")
        print("  1. 安装 cryptography: pip install cryptography")
        print("  2. 使用 OpenSSL 手动生成:")
        print("     openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes -subj '/CN=localhost'")
        print("  3. 使用不安全的 WS (不推荐): python main.py --no-ssl")
        return False
    except Exception as e:
        print(f"\n❌ 生成失败: {e}")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("🤖 VR 虚拟机器人系统 - SSL 启动")
    print("=" * 60)
    print()
    
    # 检查证书
    if not check_certificates():
        if not generate_certificates():
            print("\n❌ 无法生成证书，启动失败")
            print("\n提示: 你可以使用 --no-ssl 参数禁用 SSL:")
            print("  python main.py --no-ssl")
            return 1
    else:
        print("✅ 证书文件已存在")
    
    print()
    print("🚀 启动虚拟机器人服务器...")
    print()
    
    # 启动主程序
    try:
        subprocess.run([sys.executable, 'main.py'] + sys.argv[1:])
    except KeyboardInterrupt:
        print("\n\n⏹️  已停止")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

