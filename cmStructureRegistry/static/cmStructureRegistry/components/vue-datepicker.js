export default {
    props: ['format', 'date', 'index'],
    data: function () {
        return {
            dt: this.date == null ? '' : this.date,            
            dtFormat: this.format == null ? 'mm/dd/yyyy' : this.format,
            obj: null
        };
    },
    template: '<input type="text" style="width:85px; padding-left: 5px; padding-right: 5px" v-model="dt" @input="validate" />',
    mounted: function () {
        var self = this;

        this.obj = new Datepicker(this.$el, {
        });

        this.$el.addEventListener('changeDate', function() {
            self.dt = self.obj.getFocusedDate("mm/dd/yyyy");
            self.validate();
        });
    },
    watch: {
        dt: function (e) {
            this.$emit('dateChanged', this.dt, this.index);
        }
    },
    methods: {
        validate: function () {
            // disallow bad characters
            this.dt = this.dt.replace(/[^0-9/]/g, '');
        }
    }
}
