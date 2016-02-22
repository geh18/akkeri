var has_changed = false;
var saving = false;

tinymce.init({
    selector: '.tinymce-editor',
    height: 250
});

$('form').submit(function(e){
    saving = true;
    var image = $('.inline-field.fresh input[type="file"][id^=images-][id$=-upload]');

    if (image.length > 0 && image.get(0).files.length == 0) {
        e.preventDefault();
        var empty_image_fields = image.closest('.inline-field');
        empty_image_fields.remove();
        $(this).submit();
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
    console.log('baaaaaaaaaaaaaaaaaaaaaaaaaaaaaam');
    readURL(this);
});


$(function() {
    console.log('here 1');
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
        console.log(text);
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
});
