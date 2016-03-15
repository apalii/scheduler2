$(function() {
    var noTasks = $('.alert.alert-success');
    if (noTasks.length) noTasks.delay(5000).fadeOut();
    var statusClass = {
        _classList: [
            { value: 'Scheduled',  _class: 'default' },
            { value: 'Done',     _class: 'success' },
            { value: 'In progress', _class: 'info'   },
            { value: 'Postponed',  _class: 'info'   },
            { value: 'Partially',  _class: 'info'   },
            { value: 'Cancelled',  _class: 'danger'  },
            { value: 'Failed',    _class: 'danger'  }
        ],
        get: function(status) {
            return this._classList.reduce(function(memo, item) {
                if (item.value == status) memo = item._class;
                return memo;
            }, null);
        },
        get fullList() {
            return this._classList
                .map(function(item) { return item._class; })
                .join(' ');
        }
    };
    $('.editable-field.status').editable({
        type: 'select',
        title: 'Select status',
        source: [
            {value: 'Scheduled', text: 'Scheduled'},
            {value: 'Done', text: 'Done'},
            {value: 'In progress', text: 'In progress'},
            {value: 'Postponed', text: 'Postponed'},
            {value: 'Partially', text: 'Partially'},
            {value: 'Cancelled', text: 'Cancelled'},
            {value: 'Failed', text: 'Failed'},
        ],
        success: function(response, newValue) {
            if(response.status == 'error') return response.msg;
            if (newValue) $(this).parent()
                .removeClass(statusClass.fullList)
                .addClass(statusClass.get(newValue));
        },
        params: function(params) {
            return {
                status: params.value,
                csrfmiddlewaretoken: $('#csrf').val()
            };
        }
    });
});