1 修改config.ini文件中的路径信息folder_prefix，也可以更改cpu核心线程占用率
2 运行SearchLink.py，输入解析网址，程序会自动下载所有链接并保存到linksTemp.txt
3 将linksTemp.txt中的链接复制到links.txt中，并删除linksTemp.txt
4 运行PhotoFromWebsite.py，程序会自动下载所有链接并保存到folder中的folder_prefix的值的文件夹
