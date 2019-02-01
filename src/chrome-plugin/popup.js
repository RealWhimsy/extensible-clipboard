function onSyncButtonClick(){
    console.log('blub')
    clipboardApi.getAllClips()
}

let syncButton = $('#syncButton')
console.log(syncButton)
syncButton.click(onSyncButtonClick)
