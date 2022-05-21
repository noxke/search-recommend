// 后台脚本，接收前台的url和time, 使用http请求发送到服务器处理

const id = Math.random().toString(36).slice(-10);    // 浏览器打开时创建随机id
var opt = true;

chrome.extension.onMessage.addListener(
    function(message) {
        if (opt) {
            // alert(id)
            url = message[0];
            time = message[1];
            const Http = new XMLHttpRequest();
            var req = `http://$host$:$port$/?id=${id} &time=${time} &url=${url}`;
            Http.open("GET", req);
            // Http.setRequestHeader("ID", id)
            // Http.setRequestHeader("TIME", time)
            Http.send();
        }
    }
);