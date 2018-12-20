;
var xxx_xxx_ops = {
    init: function () {
        this.eventBind();
    },
    eventBind:function () {
        $(".xxx_wrap .xxx").click(function(){
            var btn_target = $(this);
            if( btn_target.hasClass("disabled") ){
                common_ops.alert("正在处理!!请不要重复操作~~");
                return;
            }

            //

            btn_target.addClass("disabled");

            //
            const data = {
                xxxxx: '',
                xxxxxx: ''
            };

            $.ajax({
                url:common_ops.buildUrl( "/xxx/xxx" ),
                type:'POST',
                data:data,
                dataType:'json',
                success:function( res ){
                    btn_target.removeClass("disabled");
                    var callback = null;
                    if( res.code == 200 ){
                        callback = function(){
                            window.location.href = window.location.href;
                        }
                    }
                    common_ops.alert( res.msg,callback );
                }
            });

        });
    }
}

$(document).ready(function () {
    xxx_xxx_ops.init();
});