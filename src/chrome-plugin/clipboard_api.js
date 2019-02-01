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
        xhr = requestBuilder.buildRequest('GET', BASE_CLIP_URL, onClipsGet);
        requestBuilder.sendRequest(xhr)
    }

    that.saveClip = saveClip;
    that.getAllClips = getAllClips;


    return that;

})();


