let app = (function(){
    let that = {};
    let syncButton = null;
    let clipTemplate = null;
    let $table = null;

    function onSyncButtonClick(){
        $("#clipTable tbody").empty()
        clipboardApi.getAllClips(app, onClipsGet)
    }

    function isBinary(data){
        // https://gist.github.com/RyanNutt/fe1836843a4257a4a362b2f551213835
        try {
            atob(data);
            return true
        }
        catch (err) {
            return false
        }
    }

    function saveToStorage(data) {
        let i = new Object();
        i[data._id] = data;
        chrome.storage.local.set(i) 
    }

    function onClipsGet(data, textStatus, jqXHR){
        if (jqXHR.status === 200 ){
            let clips = [];
            let clipList = document.getElementById('clipList');
            for (let i = 0; i < data.length; i++){
                clip = {};
                clip._id = data[i]._id
                if (isBinary(data[i].data) === true){
                    clip.clipText = data[i].filename.toString()
                }
                else {
                    clip.clipText = data[i].data.toString()
                }
                clip.clipType = data[i].mimetype
                if (data[i].mimetype === 'text/html'){
                    a = $(clip.clipText).attr('href')
                    clip.clipText = clip.clipText.replace('<a ', '<a target="_blank" ')
                    clip.clipText = clip.clipText.replace('</a>', a + '</a>')
                }
                clips.push(clip);
                saveToStorage(data[i])
            }
            let _new = this.clipTemplate({clips: clips})
            this.$table.append(_new)
            $('.clipDelete').click(onDeleteClick)
        }
    }

    function onClipDeleted(data, textStatus, jqXHR) {
        chrome.storage.local.remove(data)
        $("[data-id=" + data + "]").remove()
    }

    function onDeleteClick(e){
        _id = $(e.currentTarget).parent().data('id');
        clipboardApi.deleteClip(_id, onClipDeleted)
    }

    function init(){
        this.clipTemplate = Handlebars.compile(
            $("#clipTemplate").html()
        )
        this.$table = $('#clipTable tbody')

        this.syncButton = $('#syncButton')
        this.syncButton.click(onSyncButtonClick)

        onSyncButtonClick()
    }

    that.init = init;
    that.loadClips = onSyncButtonClick

    return that;
}());
