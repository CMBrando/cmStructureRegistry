export default {
    template: '#timer-fc-component',
    data: function () {
        return {
            value: this.fc
        };
    },
    props: ['timerid', 'fc'],
    mounted: function () {
        this.$emit('created');
        this.$refs.fcValue.focus();
    },
    methods: {
        cancelSet: function () {
            this.$emit('canceled');
        },
        setFC: function () {

            var self = this;

            var token = this.$root.$data.token;
            var header = this.$root.$data.header;
            var ajaxHeaders = {};
            ajaxHeaders[header] = token;

            $.ajax({
                cache: false,
                type: 'POST',
                url: "SetFleetCommander",
                data: {
                    id: this.timerid,
                    fleet_commander: this.value
                },
                dataType: "json",
                headers: ajaxHeaders
            }).done(function (data) {

                if (data.success) {

                    self.$emit('modified');
                }

            });
        }
    }
}

