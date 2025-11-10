"""
重新生成 SSL 证书
删除旧证书并生成包含所有 IP 地址的新证书
"""
import os
import sys


def main():
    print("=" * 60)
    print("🔐 重新生成 SSL 证书")
    print("=" * 60)
    print()
    
    # 删除旧证书
    if os.path.exists('cert.pem'):
        os.remove('cert.pem')
        print("🗑️  已删除旧证书: cert.pem")
    
    if os.path.exists('key.pem'):
        os.remove('key.pem')
        print("🗑️  已删除旧密钥: key.pem")
    
    print()
    
    # 调用 start_with_ssl.py 生成新证书
    import start_with_ssl
    
    if start_with_ssl.generate_certificates():
        print()
        print("=" * 60)
        print("✅ 证书重新生成成功！")
        print("=" * 60)
        print()
        print("📋 下一步:")
        print("  1. 重启虚拟机器人服务器:")
        print("     python main.py")
        print()
        print("  2. 在浏览器中刷新页面")
        print()
        print("  3. 接受新的证书警告:")
        print("     - 点击 '高级' → '继续访问'")
        print()
        return 0
    else:
        print()
        print("❌ 证书生成失败")
        return 1


if __name__ == '__main__':
    sys.exit(main())

