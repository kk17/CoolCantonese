# 粤讲粤酷微信公众号工程
[![Build Status](https://travis-ci.org/kk17/CoolCantonese.svg)](https://travis-ci.org/kk17/CoolCantonese)

[En](./README_en.md)

为了方便身边的朋友学习粤语，开发了这个微信公众号，提供在线多种语言到粤语的文字和语音翻译。微信扫描下面的二维码即可关注公众号。

![粤讲粤酷](./docs/qrcode.jpg)

支持输入语言列表:
![支持输入语言列表](./docs/support_input_languages.png)

## 系统要求
- Python 3.12 或更高版本
- Docker 24.0 或更高版本 (推荐使用Docker部署)
- 支持 OCI 格式的容器运行时

## 主要依赖
- werobot>=1.13.1 - 微信机器人框架
- beautifulsoup4>=4.12.3 - HTML解析
- lxml>=5.1.0 - XML处理
- redis>=5.0.1 - 会话存储
- gunicorn>=21.2.0 - WSGI HTTP服务器

## 开发依赖
- pytest>=8.0.0 - 测试框架
- black>=24.1.0 - 代码格式化
- flake8>=7.0.0 - 代码检查

## 配置
参考coolcantonese/conf目录下的`config.json.example`
如果使用Docker部署，参考`.env.example`

## 部署
推荐使用docker部署，支持最新的OCI格式和多平台部署：

1. 安装Docker 24.0或更高版本
2. 克隆项目：
   ```bash
   git clone https://github.com/kk17/CoolCantonese.git
   cd CoolCantonese
   ```
3. 配置环境：
   ```bash
   cp .env.example .env
   # 编辑.env文件配置必要的参数
   ```
4. 启动服务：
   ```bash
   docker compose up -d
   ```

## 本地开发
1. 创建虚拟环境：
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或
   .\venv\Scripts\activate  # Windows
   ```
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   pip install -r dev-requirements.txt
   ```
3. 运行测试：
   ```bash
   pytest
   ```

## 测试
- 单元测试：使用pytest运行测试套件
- 集成测试：推荐使用[ushuz/weixin-simulator](https://github.com/ushuz/weixin-simulator)进行微信接口测试
- 代码质量：
  ```bash
  black .  # 格式化代码
  flake8  # 代码检查
  ```

## 本项目使用到的一些资源和依赖
1. [Ekho(余音) - 中文语音合成软件(支持粤语、普通话)](http://www.eguidedog.net/cn/ekho_cn.php)
2. [whtsky/WeRoBot](https://github.com/whtsky/WeRoBot) 微信机器人框架

## 寻找前端开发者帮助
希望开发一个对应的微信小程序或官方网站，本人前端技术和时间精力有限，如有对本项目感兴趣的前端开发者欢迎联系。

## 贡献
欢迎提交Pull Request或Issue。本项目使用Python 3.12和现代Python开发实践，包括：
- 类型提示 (Type Hints)
- 现代异常处理
- 代码质量工具
- 全面的测试覆盖