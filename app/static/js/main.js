(function(){
    $('.quantity_save').hide();
    $('.item_quantity').on('click', function(){
        $('.quantity_save').hide();
        id = $(this).attr('id');
        btn_id = '#save_'+id
        $(btn_id).show();
    });
   $('#signup_form').on('click', function(){
    $('#myModal').modal('show');
});

})();