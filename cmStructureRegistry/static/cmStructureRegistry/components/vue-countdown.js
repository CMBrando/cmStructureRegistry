export default {
    data: function () {
        return {
            now: new Date()
        };
    },
    props: ['endtime', 'showRelative'],
    template: '<span>[[ countdownText ]]</span>',
    mounted: function () {

        //this.refreshNow();
    },
    computed: {
        countdownText: function () {

            if (this.showRelative)
                return moment(this.endtime).fromNow();
            else 
                return moment().countdown(this.endtime).toString();
        }
    },
    methods: {
    }
}
