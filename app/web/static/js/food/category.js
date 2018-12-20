;
var food_category_ops = {
    init:function(){
        this.eventBind();
    },
    eventBind:function(){
        var that = this;
        // 选择改变就刷新数据
        $(".wrap_search select[name=status]").change(function(){
            $(".wrap_search").submit();
        });

        $(".remove").click( function(){
            that.ops( "remove",$(this).attr("data") );
        } );

        $(".recover").click( function(){
            that.ops( "recover",$(this).attr("data") );
        } );
    },
    ops:function( act,id ){
        var callback = {
            'ok':function(){
                $.ajax({
                    url:common_ops.buildUrl( "/food/category-ops" ),
                    type:'POST',
                    data:{
                        act:act,
                        id:id
                    },
                    dataType:'json',
                    success:function( res ){
                        var callback = null;
                        if( res.error_code == 0 ){
                            callback = function(){
                                window.location.href = window.location.href;
                            }
                        }
                        common_ops.alert( res.msg,callback );
                    }
                });
            },
            'cancel':null
        };
        common_ops.confirm( ( act == "remove" ? "确定删除？":"确定恢复？" ), callback );
    }

};

$(document).ready( function(){
    food_category_ops.init();
} );