// 注入页面执行

var url = window.location.href;// 获取页面url
// url = decodeURI(url);    // 解码显示中文
var time = new Date().getTime();    // 获取页面时间
chrome.extension.sendMessage([url, time]);// 传参给后台