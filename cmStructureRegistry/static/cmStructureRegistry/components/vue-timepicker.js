export default {
    data: function () {
        return {
            time: '',
            obj: null
        };
    },
    template: '<input type="text" class="time-picker" />',
    mounted: function () {

        var self = this;

        this.obj = new TimeEntry(this.$el, {
            show24Hours: true,
            noSeparatorEntry: true,
            spinnerImage: '',
            beforeSetTime: function (oldTime, newTime) {
                self.time = newTime;
                return newTime;
            }
        });
    }
}
