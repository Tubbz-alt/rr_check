# prepare envioronment:

If you want to check task [https://rr.deepin.io/#/review/303](https://rr.deepin.io/#/review/303), just replace `303` in ** rpa.info **: ` id = 303 `

## 准备测试环境，修改/etc/sudoers，使用sudo的时候就可以不用输入密码了
```
bash nopasswd.sh
```
## 安装测试所需要的依赖
```
bash ready_env.sh
```
## 执行脚本
```
python3 check_pkgs.py
```

准备好测试环境和安装完所有依赖后，以后就只需要改动rpa.info的id，然后执行python3 check_pkgs.py 就行了

# check result
在rr_check目录会生成`result.html`文件方便查看版本，安装，打开，删除状态
`pkgs.info`会输出具体的失败信息
