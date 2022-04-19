## 前言

**本脚本用于在周六傍晚提醒同学们上传行程卡、安康码、核酸检测报告到USTC健康打卡系统。每周六下午18：00程序会自动检测你是否在本周内上传了这三张图片，如检测到某几张未上传，则会邮件提醒。**

* **20220419暂时停用，学生只能显示当日的两码了，等我这周观察一下系统行为再改代码。改好时再在此告知。**
* 20220414修复了一个bug。

## 使用步骤

* 1、将本仓库fork到你的GitHub（右上角有一个Fork按钮）

* 2、点击Actions选项卡，点击`I understand my workflows, go ahead and enable them`.

* 3、单击github页面上的“Settings-->Secrets-->Actions”，新建五个secret，名称分别是`STUID`, `PASSWORD`, `SERVER`, `MAILPASS`, `RECEIVER`，它们的值分别填你的`学号`, `统一认证密码`, `QQ邮箱`, `QQ邮箱STMP服务的授权码`, `接收提醒的邮箱`。（备注：QQ邮箱STMP服务的授权码在QQ邮箱网页端的 设置--账户 中获得，不懂可以自行百度。）

  <div align=center>
  <img src="https://cdn.jsdelivr.net/gh/cyhcyh/cdn/img/githubsecret.jpg">
  </div>

* 4、点击Actions选项卡，点击左边Workflows下的`Check action`，若有黄色感叹号则需要进一步点击右侧的`Enable workflow`
  <div align=center>
  <img src="https://cdn.jsdelivr.net/gh/cyhcyh/cdn/img/enablewkflow.jpg">
  </div>

* 5、请在 `README.md` 里添加一个空格并提交修改，否则不会触发之后的步骤。



点击Actions选项卡，此时会出现一个名叫“Update README.md”的workflow, 等它运行完前面出现绿色小勾即可，若这个workflow运行失败，单击它并点击右上角的“Re-run all jobs”即可。



本脚本设定的检查时间是每周六晚18：00。

如果您觉得好用，请给我一个star，谢谢！
