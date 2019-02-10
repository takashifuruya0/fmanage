// 設定
var move_from = document.getElementById("id_move_from")
var move_to = document.getElementById("id_move_to")
var way = document.getElementById("id_way")
var kouho = move_from.getElementsByTagName("option")
for(var i=0; i<kouho.length; i++){
    if(kouho[i].text=="財布"){
        var saifu = kouho[i].value
    }else if(kouho[i].text=="ゆうちょ"){
        var yucho = kouho[i].value
    }
};
// メソッド
var fill_resource = function(){
    // 場合分け
    var wayval = way.value
    if(wayval=="支出（現金）") {
        move_from.value = saifu
        move_to.value = null
    }else if(wayval=="引き落とし"){
        move_from.value = yucho
        move_to.value = null
    }else if(wayval=="収入"){
        move_from.value = null
        move_to.value = yucho
    }else{
        move_from.value = null
        move_to.value = null
    }
};
way.on("change", fill_resource())
