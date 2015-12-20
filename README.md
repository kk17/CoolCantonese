#粤讲粤酷微信公众号工程
为了方便身边的朋友学习粤语，开发了这个微信公众号，提供在线国语到粤语的文字和语音翻译。微信扫描下面的二维码即可关注公众号。

![粤讲粤酷](http://7sbpek.com1.z0.glb.clouddn.com/img/qrcode.jpg)

##配置
参考configs目录下的`env.cfg.example`和`redis.cfg.example`文件生成`env.cfg`和`redis.cfg`

##部署
推荐使用docker部署
需要安装docker和fig，然后在工程目录下运行`sudo fig up`即可

##测试
推荐使用[ushuz/weixin-simulator](https://github.com/ushuz/weixin-simulator)进行测试

##本项目使用到的一些资源和依赖
1. [Ekho(余音) - 中文语音合成软件(支持粤语、普通话)](http://www.eguidedog.net/cn/ekho_cn.php)
2. [kk17/ekho_dockerfile](https://github.com/kk17/ekho_dockerfile) 生成ekho docker镜像的Dockerfile
3. [whtsky/WeRoBot](https://github.com/whtsky/WeRoBot) 微信机器人框架
4. [kk17/coolcantonese_dockerfile](https://github.com/kk17/coolcantonese_dockerfile) 生成本项目docker运行镜像的Dockerfile
5. 本项目使用了七牛云存储现在免费部署在Daocloud上，在此表示感谢。



