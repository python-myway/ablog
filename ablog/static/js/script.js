$(function () {
    function render_time() {
        return moment($(this).data('timestamp')).format('L')
    }
    $('[data-toggle="tooltip"]').tooltip(
        {title: render_time}
    );
});


function update_notices_count() {
    var $el = $('#notice-badge');
    $.ajax({
        type: 'GET',
        url: $el.data('href'),
        success: function (data) {
            if (data.count === 0) {
                $('#notice-badge').hide();
            } else {
                $el.show();
                $el.text(data.count)
            }
        }
    });
};

setInterval(update_notices_count, 30000);