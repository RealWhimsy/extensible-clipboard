var clipboardApi = (function(){

    that = {}
    const BASE_URL = 'http://localhost:5000/'
    const BASE_CLIP_URL = BASE_URL.concat('clip/')

    function onClipSent(){
        if (this.readyState === XMLHttpRequest.DONE && this.status === 201){
            let i = new Object();
            i[this.response._id] = this.response
            chrome.storage.local.set(i) 
        }
    }

    function onClipsGet(){
        if (this.readyState === XMLHttpRequest.DONE && this.status === 200){
            console.log(this.response)
            let clipList = document.getElementById('clipList');
            for (var i = 0; i < this.response.length; i++){
                r = this.response[i].data.toString();
                console.log(r)
                r = r.replace('<a ', '<a target="_blank" ')
                r = r.replace('</a>', 'Item</a>')
                console.log(r)
                $('#clipList').append('<li>'+r+'</li>')
            }
        }
        
    }

    function saveClip(data, mimetype, src_url, src_app){
        console.log(data)
        xhr = requestBuilder.buildRequest('POST', BASE_CLIP_URL, onClipSent);
        send_data = {'data': data,
                     'mimetype': mimetype,
                     'src_url': src_url,
                     'src_app': src_app};
        console.log(send_data)
        requestBuilder.sendRequest(xhr, send_data);
    }

    function getAllClips(){
        console.log('getting clips')
        xhr = requestBuilder.buildRequest('GET', BASE_CLIP_URL, onClipsGet);
        requestBuilder.sendRequest(xhr)
    }

    that.saveClip = saveClip;
    that.getAllClips = getAllClips;


    return that;

})();


