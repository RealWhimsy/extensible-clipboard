let app = (function(){
    let that = {};
    let syncButton = null;
    let clipTemplate = null;
    let $table = null;

    function onSyncButtonClick(){
        $('#clipList').empty();
        clipboardApi.getAllClips(app, onClipsGet);
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
    
    function createClip(dataItem) {
        clip = {};
        clip._id = dataItem._id;
        clip.clipType = dataItem.mimetype;
        clip.parent = dataItem.parent;
        clip.children = [];
        date = new Date(dataItem.creation_date)
        options = {year: '2-digit', month: '2-digit', day: 'numeric',
                   timezone: 'UTC+1', hour: 'numeric', minute: 'numeric'};
        clip.date = date.toLocaleString('de-DE', options);
        /*
        if (isBinary(data[i].data) === true){
            console.log(data[i])
            clip.clipText = data[i].filename.toString()
        }
        else {
            clip.clipText = data[i].data.toString()
        }
        if (data[i].mimetype === 'text/html'){
            a = $(clip.clipText).attr('href')
            clip.clipText = clip.clipText.replace('<a ', '<a target="_blank" ')
            clip.clipText = clip.clipText.replace('</a>', a + '</a>')
        }
        */
        return clip
    
    }

    function onClipsGet(data, textStatus, jqXHR){
        if (jqXHR.status === 200 ){
            let clips = [];
            let clipList = document.getElementById('clipList');
            for (let i = 0; i < data.length; i++){
                if (!( 'parent' in data[i] )) {
                    clips.push(createClip(data[i]));
                }
            }
            for (let i = 0; i < data.length; i++) {
                if ( 'parent' in data[i] ) {
                    for (let j = 0; j < clips.length; j++) {
                        if ( data[i].parent === clips[j]._id ) {
                            clips[j].children.push(createClip(data[i]))
                            break;
                        }
                    }
                }
            }
            let flattened = [];
            for (let i = clips.length-1; i >= 0; i--) {
                flattened.push(clips[i]) 
                for ( let j = 0; j < clips[i].children.length; j++ ) {
                    flattened.push(clips[i].children[j])
                }
            }
            let context = {"clips": flattened}
            $('#clipList').append(this.clipTemplate(context))
            $('.clipDelete').click(onDeleteClick)
            $('.clipPaste').click(onPasteClick)
            $('.clipOpen').click(onOpenClick)
            $('.clipType').click(onOpenClick)
        }
        else {
            console.log(data)
        }
    }

    function onClipDeleted(data, textStatus, jqXHR) {
        $("[data-id=" + data._id + "]").remove()
    }

    function onDeleteClick(e){
        _id = $(e.currentTarget).parent().data('id');
        clipboardApi.deleteClip(_id, onClipDeleted)
    }

    function onOpenClick(e) {
        _id = $(e.currentTarget).parent().data('id');
        if ( _id !== undefined ) {
            clipboardApi.openLink(_id)
        }
    }

    function onClipGet(data, textStatus, jqXHR){
        if ( jqXHR.status === 200 ) {
            chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
                chrome.tabs.sendMessage(tabs[0].id, {data: data},);
            });
        }
    }

    function onPasteClick(e){
        _id = $(e.currentTarget).parent().data('id');
        clipboardApi.getClip(_id, onClipGet)
    }

    function init(){
        let source = document.getElementById("clipTemplate2").innerHTML;
        this.clipTemplate = Handlebars.compile(source)
        this.syncButton = $('#syncButton')
        this.syncButton.click(onSyncButtonClick)

        onSyncButtonClick()
    }

    that.init = init;
    that.loadClips = onSyncButtonClick

    return that;
}());
