function validate(){
    var valid = false;
    var list_cust=$('#ui-id-1 li');
    if (list_cust.length==0){$('#cust_id_err').css('display','block');valid=false;}
    var suc=0;
    list_cust.each(function(i){if($(this).text() == $('#cust_id').val()){suc=1;}});
    
    if (suc==1){$('#cust_id_err').css('display','none'); valid=true;}
    else{$('#cust_id_err').css('display','block');valid=false;}
    
    return valid;
}