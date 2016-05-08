var has_changed = false;
var saving = false;
var form_saved = false;

var getUrlParameter = function getUrlParameter(sParam) {
    var sPageURL = decodeURIComponent(window.location.search.substring(1)),
        sURLVariables = sPageURL.split('&'),
        sParameterName,
        i;

    for (i = 0; i < sURLVariables.length; i++) {
        sParameterName = sURLVariables[i].split('=');

        if (sParameterName[0] === sParam) {
            return sParameterName[1] === undefined ? true : sParameterName[1];
        }
    }
};

tinymce.init({
    selector: '.tinymce-editor',
    height: 250
});


var getFormData = function(postid, url){
    var url = getUrlParameter('url');

    var text = $('div.cedit')[0].innerHTML;
    $('textarea.cedit').val(text);

    var form_data = $('input[type!=file]', 'form').serialize();

    return form_data;
}

var isNew = function(){
    var path = window.location.pathname,
        url = getUrlParameter('url'),
        action = path.split(url)[1],
        is_new = action.indexOf('new');

    return is_new != -1;
}

var submitForm = function(postid) {
    var $form = $('form');
   
    var url = getUrlParameter('url');
    
    var is_new = isNew();

    if(is_new && !$('#instanceid').val()){
        var form_data = getFormData(postid, url);
        $.post(url+'new/'+'?url='+url, form_data, function(resp) {
            window.location = window.location.href;
            form_saved = true;
            $form.submit();
        });
    }
    else {
        var postid;

        if(is_new && $('#instanceid').val()){
            postid = $('#instanceid').val();
        } else {
            postid = getUrlParameter('id');
        }
        var form_data = getFormData(postid, url);
        $.post(url+'edit/'+'?id='+postid+'&url='+url, form_data, function(resp) {
            window.location = window.location.href;
            form_saved = true;
            $form.submit();
        });
    }

}

$('form').submit(function(e){
    saving = true;
    $form = $(this);

    var image = $('.inline-field.fresh input[type="file"][id^=images-][id$=-upload]');

    if (image.length > 0 && image.get(0).files.length == 0) {
        var empty_image_fields = image.closest('.inline-field');
        empty_image_fields.remove();
    }
    if(!form_saved){
        e.preventDefault();
        submitForm();
        return;
    }
});

// images wrapper
$('.inline-field.well').click(function(e){
    $(this).addClass('edit-image');
    $(this).addClass('col-xs-2');
    $(this).find('.edit').remove();

    var hidden = $(this).find('.hidden');
    var group = hidden.find('.form-group');
    var input = group.find('.col-md-10');
    input.removeClass('col-md-10').addClass('col-md-12');
    var label = hidden.find('label');
    label.css('text-align', 'left');
    hidden.removeClass('hidden');
});


// Minimal effort to prevent people from
// accidentally closing the window without saving
$('#title, #body').one('keyup paste', function(){
    console.log('changed');
    has_changed = true;
});

window.onbeforeunload = function() {
    if (has_changed && !saving) {
    var message = 'You have unsaved changes. Continue?';
    return message;
    }
}

function readURL(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();

        reader.onload = function (e) {
            $('.image-src').attr('src', e.target.result);
        }

        reader.readAsDataURL(input.files[0]);
    }
}

$("#images .inline-field img").change(function(){
    readURL(this);
});


$(function() {
    var observe;
    if (window.attachEvent) {
        observe = function (element, event, handler) {
            element.attachEvent('on'+event, handler);
        };
    }
    else {
        observe = function (element, event, handler) {
            element.addEventListener(event, handler, false);
        };
    }
    function init () {
        var text = document.getElementById('body');
        function resize () {
            text.style.height = 'auto';
            text.style.height = text.scrollHeight+'px';
        }
        /* 0-timeout to get the already changed text */
        function delayedResize () {
            window.setTimeout(resize, 0);
        }
        observe(text, 'change',  resize);
        observe(text, 'cut',     delayedResize);
        observe(text, 'paste',   delayedResize);
        observe(text, 'drop',    delayedResize);
        observe(text, 'keydown', delayedResize);

        text.focus();
        text.select();
        resize();
    }

    init();

    var editor = new MediumEditor('.cedit', {
        placeholder: false,
        anchor: {
            customClassOption: null,
            customClassOptionText: 'Button',
            linkValidation: true,
            placeholderText: 'Type your link',
            targetCheckbox: true,
            targetCheckboxText: 'Opna í nýjum glugga'
        },
        autoLink: true,
        extensions: {
            'imageDragging': {}
        },
        paste: {
            cleanPastedHTML: true,
            cleanAttrs: ['style', 'dir'],
            cleanTags: ['label', 'meta']
        },
        toolbar: {
            buttons: ['h1', 'anchor', 'quote', 'image'],
            diffLeft: 25,
            diffTop: 10,
        },
    });
});


