### 简介
通过一个给定电影名从爬取豆瓣电影抓取评论，生成一个词云图。
由于豆瓣电影搜索数据是动态加载的，这里用到的selenium库，程序运行中会打开Chrome浏览器（如果要使用其他浏览器请下载对应的driver放到drivers目录下，自己修改代码中的对应的驱动路径），中文词云使用jieba库进行分词，matplotlib库展示图片，如果要保存图片，点击词云图片窗口上的保存图标按钮即可。
由于豆瓣对未登录用户有访问权限，最多只能爬取220条评论，如果想抓取更多数据，并制作更个性化的词云图，请自行修改代码实现。
### 搭建开发环境
```
pipenv install
```
如果环境搭建过程中安装wordcloud库出现问题，无法安装 ，原因是win系统下安装wordcloud库需要visual studio build tools 2014，更方便的解决办法是直接安装构建好的.whl库文件，库文件在packages目录下，使用如下命令安装
`pipenv install xxx.whl`
### 使用方法
打开win CMD
```
pipenv shell #激活虚拟环境
cd到src目录下输入
python main.py "机器人瓦力" #通过命令行参数传递电影名
或者
python main.py #代码启动后会提示输入电影名

```
### 图片示例
![image](https://github.com/wangyushun/dbmc/blob/master/image/wali.png)

git@github.com:wangyushun/dbmc.git