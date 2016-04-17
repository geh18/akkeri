;(function($){
    $(function(){
        var h2 = $('<button>', {'class': 'btn h2'}).text('Title');
        var image = $('<button>', {'class': 'btn image',
                                   'data-toggle': 'modal',                 
                                   'data-target': '#admin-modal',
                                   'data-url': '/modal_upload_image'}).text('Image');
        var $cedit = $('div.cedit');

        $cedit.before(h2);
        $cedit.before(image);
       
       h2.click(function(e) {
            e.preventDefault();
            var html = $cedit.html();
            document.execCommand('formatBlock', false, 'h1');
            if(html == $cedit.html()) {
                document.execCommand('formatBlock', false, 'div');
            }
        });

        function placeCaretAtEnd(el) {
            el.focus();
            if (typeof window.getSelection != "undefined"
                    && typeof document.createRange != "undefined") {
                var range = document.createRange();
                range.selectNodeContents(el);
                range.collapse(false);
                var sel = window.getSelection();
                sel.removeAllRanges();
                sel.addRange(range);
            } else if (typeof document.body.createTextRange != "undefined") {
                var textRange = document.body.createTextRange();
                textRange.moveToElementText(el);
                textRange.collapse(false);
                textRange.select();
            }
        }

        function insertImage(imgSrc, id, editor) {
            var doc = (editor.tagName.toLowerCase() == "iframe") ?
                (editor.contentDocument || editor.contentWindow.document) : document;
            var imgHtml = "<img src='" + imgSrc + "' id=" + id + ">";
            var sel;
            
            if (doc.queryCommandSupported("InsertHTML")) {
                doc.execCommand("insertHTML", false, imgHtml);
            } else if ( (sel = doc.selection) && sel.type != "Control") {
                var range = sel.createRange();
                range.pasteHTML(imgHtml);
                range.collapse(false);
                range.select();
            }
            
            return doc.getElementById(id);
        };
        
        image.click(function(e){
            e.preventDefault();

            var focusNode = window.getSelection().focusNode,
                anchor = window.getSelection().anchorNode,
                in_editor = $(anchor).closest($cedit).length > 0;

            var focused =  in_editor || (
                focusNode && (focusNode.parentElement || focusNode.parentNode)) == $cedit[0];

            if(!focused){
                placeCaretAtEnd($cedit[0]);
            }
        });

        $cedit[0].addEventListener("paste", function(e) {
            // cancel paste
            e.preventDefault();

            // get text representation of clipboard
            var text = e.clipboardData.getData("text/plain");

            // insert text manually
            document.execCommand("insertHTML", false, text);
        });

        $('#admin-modal').on('change', '#select-image', function(){
            readFile(this);
        });

        $('#admin-modal').on('click', '.confirm-btn', function(e){
            e.preventDefault();
            if(true) {
                var base64 = $('div.image-with-upload .preview img').attr('src');
                var postid = getUrlParameter('id');
                $.ajax({
                    url: '/modal_upload_image',
                    type: 'POST',
                    dataType: 'json',
                    data: {'image_path': base64, 'postid': postid}
                })
                .success(function(resp){
                    if(resp.new) {
                        $('#instanceid').val(resp.postid);
                    }
                    if(resp.img_path) {
                        $('#admin-modal').modal('hide');
                        //document.execCommand('insertImage', false, resp.img_path);
                        insertImage(resp.img_path, resp.img_id, $cedit[0]);
                    }
                });
            }
        });

        function readFile(input) {
            if(input.files && input.files[0]) {
                var reader = new FileReader(); 

                reader.onload = function (e) {
                    $('div.image-with-upload .preview img').attr('src', e.target.result);
                }

                reader.readAsDataURL(input.files[0]); 
            }
        }

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
       
        $('form').submit(function(){
            var text = $cedit[0].innerHTML;
            var textarea = $cedit.val(text);
        });
    });
})(jQuery);
