// popup脚本，点击扩展图标后执行

bg = chrome.extension.getBackgroundPage()
bg.opt = confirm("是否同意收集您的数据？\n如涉及敏感信息请退出浏览器选择取消或卸载本插件")