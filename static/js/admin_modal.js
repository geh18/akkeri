$(window).ready(function(){
    $('#admin-modal').on('show.bs.modal', function (event) {
        var src_btn = $(event.relatedTarget),
            recipient = src_btn.data('modal'),
            url = src_btn.data('url'),
            modal = $(this);

        if (recipient == 'delete-image') {
            modal.find('.modal-title').text('Delete Image');
            modal.find('.modal-body').text('Are you sure you want to delete your photo? Note: this will affect all of your articles');
            var confirm_btn = modal.find('.confirm-btn');
            confirm_btn.text('Delete');
            deleteImage(src_btn, confirm_btn);
        }

        if (url) {
           $.ajax({
                url: url,
                type: 'GET',
                dataType: 'html'
           })
           .success(function(data){
                modal.find('.modal-body').html(data);        
           });
        }
    }); 

    function deleteImage(src_btn, confirm_btn){
        confirm_btn.on('click', function(){
            var form = src_btn.closest('form');
            var checkbox = form.find('input:checkbox');
            checkbox.prop('checked', true);
            console.log('form + ' + form);
            form.submit();
        });
    }

    function uploadImageToArticle(){
        i
    }
});
