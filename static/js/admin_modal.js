$(window).ready(function(){
    $('#admin-modal').on('show.bs.modal', function (event) {
        var src_btn = $(event.relatedTarget);
        var recipient = src_btn.data('modal');
        var modal = $(this);

        if (recipient == 'delete-image') {
            modal.find('.modal-title').text('Delete Image');
            modal.find('.modal-body').text('Are you sure you want to delete your photo? Note: this will affect all of your articles');
            var confirm_btn = modal.find('.confirm-btn');
            confirm_btn.text('Delete');
            deleteImage(src_btn, confirm_btn);
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
 
});
