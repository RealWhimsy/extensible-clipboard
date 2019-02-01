var requestBuilder = (function(){
    that = {}
    
    function buildRequest(method, url, callback){
        let xhr = new XMLHttpRequest();
        xhr.open(method, url, true);
        xhr.setRequestHeader("Content-Type", "application/json", "charset=utf-8");
        xhr.responseType = 'json';
        xhr.onreadystatechange = callback
        return xhr
    }

    function sendRequest(xhr, data=null){
        if (data !== null) {
            data = JSON.stringify(data)
        }
        console.log(xhr)
        xhr.send(data)        
    }

    that.buildRequest = buildRequest
    that.sendRequest = sendRequest

    return that

})();
