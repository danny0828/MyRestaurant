;
var account_index_ops = {
    init:function(){
        this.eventBind();
    },
    eventBind:function(){
        var that = this;
        $(".wrap_search .search").click(function(){
            $(".wrap_search").submit();
        });

        $(".remove").click( function(){
             //jquery获取元素属性attr
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
                    url:common_ops.buildUrl( "/account/ops" ),
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
    account_index_ops.init();
} );