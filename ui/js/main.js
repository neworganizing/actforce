Object.size = function(obj) {
    var size = 0, key;
    for (key in obj) {
        if (obj.hasOwnProperty(key)) size++;
    }
    return size;
};

function orgquery(orgname, orgid) {
    $('.fulllist').empty();
    $('.noresults').hide();
    $('.moreresults').hide();
    $('.loadingbar').show();
    $.getJSON('',{orgid:orgid, orgname:orgname}).done(function(data){
console.log(data);
$('.loadingbar').hide();
var total = Object.size(data);
if (total == 7) {
    $('.moreresults').show();
} else if (total == 0) {
    $('.noresults').show();
}
console.log(total);
$.each( data, function( id, orgname ) {
var html = "<li class=\"orgoption\" data-orgname=\"" + orgname + "\" data-orgid=\"" + id + "\"><a class=href=\"#\">" + orgname + "</a></li>";
console.log(html)
$('.fulllist').append(html);
    $('.fulllist li').click(function() {
        console.log("Click!");
        $('#recordform #id_orgname').attr('value',$(this).attr('data-orgname'));
        $('#recordform #id_hiddenorgname').attr('value',$(this).attr('data-orgname'));
        $('#recordform #id_orgid').attr('value',$(this).attr('data-orgid'));
        $('.orglist a').removeClass('active');
        $('.neworg').hide();
        $('#orgModal').modal('hide');
        return false;
    });
});
})
}

$(document).ready(function() {
    $('.changepage-toggle').click(function(){
        $('.changepage').toggleClass('hide');
    });
    // Org Box

    $('.createorg a').click(function() {
        $('.neworg').toggle();
        $('.createorg a').toggleClass('active');
        return false;
    });

    $('.orgsearch').submit(function () {
        orgquery($('.orgsearchbox').val(),'')
        return false;
    });

    function mover(type,origin) {
        $('#recordform input[type="text"],#recordform input[type="email"]').val('');
        $(origin).find('span').each(function() {
            console.log($(this).attr('data-target'))
            $('#recordform #' + $(this).attr('data-target')).val($(this).text())
        })
    }
    $('.createnewrecord').click(function() {
        $('.editform').show();
        $(this).hide();
        return false;
    });
    $('.neworg').submit(function() {
        $('#recordform #id_orgname').attr('value',$('#neworgname').val());
        $('#recordform #id_hiddenorgname').attr('value',$('#neworgname').val());
        $('#recordform #id_orgid').attr('value','neworg');
        $('#orgModal').modal('hide');
        return false;     

    });
    
    if (window.location.hash == "#addnew") {
        $('.editform').show();
        $('.createnewrecord').hide();
    }
});