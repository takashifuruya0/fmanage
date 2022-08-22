// 設定
var move_from = document.getElementById("id_move_from")
var move_to = document.getElementById("id_move_to")
var way = document.getElementById("id_way")
var usage = document.getElementById("id_usage")
var kouho = move_from.getElementsByTagName("option")
var kouho_usage = usage.getElementsByTagName("option")
for(var i=0; i<kouho.length; i++){
    if(kouho[i].text=="財布"){
        var saifu = kouho[i].value
    }else if(kouho[i].text=="ゆうちょ"){
        var yucho = kouho[i].value
    }
}
for (var i=0; i<kouho_usage.length; i++){
    if(kouho_usage[i].text=="その他"){
        var sonota = kouho_usage[i].value;
    }else if(kouho_usage[i].text=="その他収入"){
        var sonota_income = kouho_usage[i].value;
    }
}

// メソッド
var fill_resource = function(){
    // 場合分け
    var wayval = way.value
    if(wayval=="支出（現金）") {
        move_from.value = saifu;
        move_to.value = null;
        usage.value = sonota;
    }else if(wayval=="引き落とし"){
        move_from.value = yucho
        move_to.value = null
        usage.value = sonota;
    }else if(wayval=="収入"){
        move_from.value = null
        move_to.value = yucho
        usage.value = sonota_income;
    }else if(wayval=="支出（クレジット）" || wayval=="支出（Suica）") {
        move_from.value = null
        move_to.value = null
        usage.value = sonota;
    }else{
        move_from.value = null
        move_to.value = null
        usage.value = null;
    }
};
way.on("change", fill_resource())
