const TimerTypes = {
    ARMOR: 1,
    HULL: 2,
    MINING: 3,
    MOVE: 4,
    FLEET: 5,
    IHUB: 6,
    TCU: 7,
    UNANCHOR: 8,
    ANCHORING: 9
}

const HostilityTypes = {
    HOSTILE: 1,
    FRIENDLY: 2
}

export default {
    template: '#timer-component',
    data: function () {
        return {
            show: false,
            sort: { property: "timer_datetime", direction: "asc" },
            timers: [],
            now: (new Date()).getTime(),
            frequency: 30000,
            staging_system: this.stagingSystemId
        };
    },
    props: ['type', 'admin', 'add', 'edit', 'stagingSystemId'],
    mounted: function () {
        this.loadData();
    },
    watch: {
        sort: {
            deep: true,
            handler: function () {
                var res = _.orderBy(this.timers, [this.sort.property], [this.sort.direction]);
                this.timers = res;
            }
        },
        stagingSystemId: {
            handler: function() {
                this.staging_system = this.stagingSystemId
                this.loadData()
            }
        }
    },
    methods: {
        loadData: function () {

            var me = this;

            var url = '';
            if (this.type === 'recent')
                url = 'GetRecentTimers';
            else
                url = 'GetOpenTimers?system=' + (this.staging_system ? this.staging_system: '');

            $.get(url, function (data) {

                me.timers = [];
                // reset sort cause we're repopulating
                if (me.type === 'recent')
                    me.sort = { property: "timer_datetime", direction: "desc" };
                else
                    me.sort = { property: "timer_datetime", direction: "asc" };

                _.each(data, function (item) {
                    me.timers.push(item);
                });

                me.show = true;

                if (me.type === 'open')
                    me.frequency = 1000;

                me.rerender();
            });
        },
        isSortProp: function (prop) {
            return (this.sort.property == prop);
        },
        showSortIcon: function (prop, dir) {
            return (this.sort.property == prop && this.sort.direction == dir);
        },
        rerender: function () {
            var self = this;

            this.now = (new Date()).getTime()

            setTimeout(function () { self.rerender(); }, this.frequency);
        },
        toggleSort: function (prop) {
            if (this.sort.property == prop) {
                if (this.sort.direction == 'asc')
                    this.sort.direction = 'desc';
                else
                    this.sort.direction = 'asc';
            }
            else // switching properties so set and set to default asc
            {
                this.sort.property = prop;
                this.sort.direction = 'asc';
            }
        },
        formatTimer: function (dateTime) {
            return moment.utc(dateTime).format('MM/DD HH:mm:ss');
        },
        formatFloat: function (number) {
            return numeral(number).format('0.0')
        },        
        fromNow: function (dateTime) {

            if (this.type === 'open')
                return moment().countdown(dateTime).toString();
            else
                return moment(dateTime).fromNow();

        },
        isRed: function (dateTime) {

            if (this.type === 'open')
                return moment().isAfter(moment(dateTime));
            else
                return false;
        },
        copySystemToClipboard: function(system) {
            navigator.clipboard.writeText(system);
            toastr.success('System copied to clipboard')
        },
        timerAdded: function () {
            this.loadData();
        },
        addTimer: function (id) {
            this.$emit('add-timer', id);
        },
        confirmDelete: function (id) {
            this.$emit('delete-timer', id);
        },
        setFleetCommander: function (id) {

            var timer = _.find(this.timers, function (t) { return t.id === id; });

            this.$emit('set-fleetcommander', id, timer.fleet_commander);
        },
        distanceText: function(timer) {
            if(timer.jumps) {
                var distance = this.formatFloat(timer.distance);
                return `${distance} ly (${timer.jumps} jp)`;
            }
            else
                return 'N/A'
        }
    }
}












