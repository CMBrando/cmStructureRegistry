export default {
    data: function () {
        return {
            durationDate: '',
            durationText: ''
        };
    },
    template: '<input type="text" style="width:200px" placeholder="eg. 1d 2h 3m 4s" v-model="durationText" />',
    watch: {
        durationText: function(val) {
            this.durationDate = reltime.parse(new Date(), val);
        }
    }
}
