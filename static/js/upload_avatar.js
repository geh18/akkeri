$(window).ready(function(){
    var $uploadCrop;

    function readFile(input) {
        if (input.files && input.files[0]) {
            var reader = new FileReader();
            
            reader.onload = function (e) {
                $uploadCrop.croppie('bind', {
                    url: e.target.result
                });

                $('.user-image .image-wrapper').addClass('hidden');
                $('#crop-avatar').removeClass('hidden');
            }
              
            reader.readAsDataURL(input.files[0]);

            reader.onloadend = function(e){
                var min_zoom = $uploadCrop.find('input[type="range"]').attr('min');
                $uploadCrop.croppie('setZoom', parseFloat(min_zoom));
            }

        }
        else {
            swal("Sorry - you're browser doesn't support the FileReader API");
        }
    }

    $uploadCrop = $('#crop-avatar').croppie({
        viewport: {
            width: 175,
            height: 175,
            type: 'circle'
        },
        boundary: {
            width: 225,
            height: 225
        },
        exif: true,
    });

    $('#image').on('change', function () { readFile(this); });
    $('form').submit(function (ev) {
        $uploadCrop.croppie('result', {
            type: 'canvas',
            size: 'viewport',
            quality: 0.8
        }).then(function (resp) {
            $('#base64').val(resp);
        });
    });

    $('.cancel-upload').click(function(){
        $('#base64').val('');
        $('.user-image .image-wrapper').removeClass('hidden');
        $('#crop-avatar').addClass('hidden');
    });
});


