var script = document.createElement('script');
script.src = 'https://code.jquery.com/jquery-1.10.2.js';
script.type = 'text/javascript';
document.getElementsByTagName('head')[0].appendChild(script);

function ChangeTable(value) {
    url_current = new URL(document.URL)
    url_show_table = url_current.origin + '/show_table/';
    $.post(url_show_table, {index: value}).done(function (data) {
        $("#result").empty().append(data);
        Load_selector();
    });

}

function Load_selector() {
    for (let key = 0; key < 20; key++) {
        const el = document.getElementById("fk_table_" + key);
        if (el != null) {
            ChangeFKTable(key, el.value, el.name);
        }
    }
}

async function save_excel(url_save) {
    let reponse = await fetch(url_save, {
        method: 'POST',
        body: new FormData(form_file)
    });
    let rep = await reponse.text();
    if (rep === 'Успешно'){
        location.replace('/')
    }else{
        location.replace('/set_db/')
    }
}

async function create_download_delete(url_create) {
    let response = await fetch(url_create, {
        method: 'POST',
        body: new FormData(form_file)
    });
    let file_name = await response.text();

    // ответ в виде file_name
    let url_download = window.origin + '/download/' + file_name;
    await download(url_download)
    await delete_by_name(file_name)

}

async function delete_by_name(file_name){
    let url_delete = window.origin + '/delete_tmp_file/' + file_name;
    await fetch(url_delete)

}


async function download(str_url){
    // создание ссылки на скачаивание
    let link = document.createElement('a');
    link.setAttribute('href', str_url);
    link.setAttribute('download', 'download');
    link.click();
}

function sleep(miliseconds) {
   var currentTime = new Date().getTime();

   while (currentTime + miliseconds >= new Date().getTime()) {
   }
}