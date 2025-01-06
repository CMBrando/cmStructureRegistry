export default {
    template: '#timer-delete-component',
    data: function () {
        return {
        };
    },
    props: ['timerid'],
    mounted: function () {
        this.$emit('created');
    },
    methods: {
        cancelDelete: function () {
            this.$emit('canceled');
        },
        deleteTimer: function () {

            var self = this;

            var token = this.$root.$data.token;
            var header = this.$root.$data.header;
            var ajaxHeaders = {};
            ajaxHeaders[header] = token;

            $.ajax({
                cache: false,
                type: 'POST',
                url: "DeleteTimer",
                data: {
                    timerID: this.timerid
                },
                dataType: "json",
                headers: ajaxHeaders
            }).done(function (data) {

                if (data.success) {

                    self.$emit('deleted');
                }

            });
        }
    }
}
