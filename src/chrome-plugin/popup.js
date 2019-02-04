var app = (function(){
    var that = {};
    var syncButton = null;
    var clipTemplate = null;
    var $table = null;

    function onSyncButtonClick(){
        $("#clipTable tbody").empty()
        clipboardApi.getAllClips(app, onClipsGet)
    }

    function mimetypeSupported(mimetype){
        if (mimetype.indexOf('text/') !== -1 || mimetype.indexOf('application/') !== -1){
            return true
        }
        else{
            return false
        }
    }

    function onClipsGet(data, textStatus, jqXHR){
        if (jqXHR.status === 200 ){
            var clips = [];
            var clipList = document.getElementById('clipList');
            for (var i = 0; i < data.length; i++){
                if (mimetypeSupported(data[i].mimetype) === false){
                    continue;
                }
                clip = {};
                clip.clipText = data[i].data.toString()
                clip.clipType = data[i].mimetype
                if (data[i].mimetype === 'text/html'){
                    a = $(clip.clipText).attr('href')
                    clip.clipText = clip.clipText.replace('<a ', '<a target="_blank" ')
                    clip.clipText = clip.clipText.replace('</a>', a + '</a>')
                }
                clips.push(clip);
            }
            var _new = this.clipTemplate({clips: clips})
            this.$table.append(_new)
        }
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
