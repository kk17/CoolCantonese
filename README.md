# 粤讲粤酷微信公众号工程
[![Build Status](https://travis-ci.org/kk17/CoolCantonese.svg)](https://travis-ci.org/kk17/CoolCantonese)

[En](./README_en.md)

为了方便身边的朋友学习粤语，开发了这个微信公众号，提供在线多种语言到粤语的文字和语音翻译。微信扫描下面的二维码即可关注公众号。

![粤讲粤酷](./docs/qrcode.jpg)

支持输入语言列表:
![支持输入语言列表](./docs/support_input_languages.png)

## 配置
参考coolcantonese/conf目录下的`config.json.example`
如果使用Docker部署，参考`.env.example`

## 部署
推荐使用docker部署
需要安装docker，然后在工程目录下运行`sudo docker-compose up`即可

## 测试
推荐使用[ushuz/weixin-simulator](https://github.com/ushuz/weixin-simulator)进行测试

## 本项目使用到的一些资源和依赖
1. [Ekho(余音) - 中文语音合成软件(支持粤语、普通话)](http://www.eguidedog.net/cn/ekho_cn.php)
2. [whtsky/WeRoBot](https://github.com/whtsky/WeRoBot) 微信机器人框架

## 寻找前端开发者帮助

希望开发一个对应的微信小程序或官方网站，本人前端技术和时间精力有限，如有对本项目感兴趣的前端开发者欢迎联系。