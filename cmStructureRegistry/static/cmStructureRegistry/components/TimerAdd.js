export default {
    template: '#timer-add-component',
    data: function () {
        return {
            types: [],
            timerRawText: '',
            timerInput: 'countdown',
            timerType: '',
            structureTypes: [],
            structureType: '',
            hostilityTypes: [],
            hostilityType: 1,
            comment: '',
            showError: false,
            errors: [],
            initSystem: '',
            showSystemLookup: true,
            systemName: '',
            systemId: null,
            structureName: null,
            structureID: this.structure_id,
            timerDate: null,
            timerDateString: null,
            planet: null,
            planets: []
        };
    },
    watch: {
        systemId: function () {
            if(this.systemId)
                this.loadPlanets();
            else
                this.planets = [];
        }
    },
    props: ['structure_id'],
    mounted: function () {
        this.loadTypes();

        if (this.structureID != null)
            this.loadStructure();

        this.$emit('created');

        this.$refs.timerPaste.focus();
    },
    methods: {
        loadTypes: function () {
            var self = this;

            $.get('GetStructureTypes', function (data) {
                self.structureTypes = data;
            });

            $.get('GetTimerTypes', function (data) {
                self.types = data;   
            });

            $.get('GetHostilityTypes', function (data) {
                self.hostilityTypes = data;
            });
        },
        loadStructure: function () {

            var me = this;

            if (this.structureID != null) {
                $.get('GetStructure?structureID=' + this.structureID + '&_t=' + (new Date()).getTime(), function (data) {
                    me.initTimer(data);
                });
            }
            else if (this.structureName != null) {
                $.get('GetStructure?structureName=' + encodeURIComponent(this.structureName) + '&_t=' + (new Date()).getTime(), function (data) {

                    if(data != null)
                        me.initTimer(data);
                });
            }
        },
        loadSolarSystem: function (name) {
            var me = this;
            $.get('SearchSolarSystems?query=' + encodeURIComponent(name), function (data) {

                if (data != null && data.length > 0) {
                    me.systemId = data[0].id
                    me.systemName = data[0].name;
                    me.showSystemLookup = false;
                }               
            });
        },
        loadPlanets: function () {
            var me = this;
            $.get('GetPlanets?solarSystemID=' + this.systemId, function (data) {
                me.planets = data;
            });
        },
        initTimer: function (struct) {

            var me = this;

            this.structureType = struct.structure_type_id;
            this.structureName = struct.structure_name;
            this.systemName = struct.solar_system;
            this.systemId = struct.solar_system_id;
            this.structureID = struct.structure_id;
            this.showSystemLookup = false;
        },
        resetForm: function () {

            if(this.$refs.system != null)
                this.$refs.system.system = null;

            this.timerType = '';
            this.timerInput = 'countdown';

            if(this.$refs.date)
                this.$refs.date.dt = '';

            if(this.$refs.time)
                this.$refs.time.time = '';

            this.comment = '';
            this.structureType = '';
            this.hostilityType = 1;
        },
        systemChanged: function (system) {
            this.systemId = system.id;
        },
        structureSelected: function (item) {
            if (item && item.id) {
                this.structureID = item.id;
                this.loadStructure();
            }
            else {
                this.structureID = null;
                this.structureName = '';
                this.systemName = '';
                this.systemID = null;
                this.structureType = null;
                this.showSystemLookup = true;
            }
        },
        timerTypeChange: function () {
            if (this.timerType == '8') { // if UnAnchor
                this.timerInput = 'countdown';

                var that = this;
                this.$nextTick(function () {
                    that.$refs.duration.$data.durationText = '7d 0h 0m 0s'; // set to 7 days by default.
                });
            }
        },
        onTimerRawInput: function () {
            var text = s.clean(this.timerRawText);

            if (text) {

                const regex = /(?:^|[^0-9])([0-9]{1,3}(?:,[0-9]{3})*|0|1,000,000,000) km(?:[^0-9]|$)/;
                const match = text.match(regex);
                if (match) {

                    var number = match[1];
                    var index = text.indexOf(number);

                    var structure = s.clean(text.substring(0, index));
                    this.structureID = null;
                    this.structureName = structure;
                    this.comment = structure;
                    this.loadStructure();

                    var dateTime = text.slice(-19);
                    var dt = moment.utc(dateTime, 'YYYY.MM.DD hh:mm:ss');

                    if (dt != null) {
                        this.timerInput = 'specific';
                        this.timerDate = dt;
                        this.timerDateString = moment.utc(this.timerDate).format("MM/DD/YYYY HH:mm:ss");                        
                    }

                    var solarSystemName = this.structureName.substring(0, this.structureName.indexOf(' - '));
                    var me = this;

                    // wait for to check, if structure populated. if not then search for solar system
                    setTimeout(function () {
                        if (me.structureID == null) {
                            me.loadSolarSystem(solarSystemName);
                        }

                    }, 200);
                }
            }
        },
        addTimer: function () {

            showError: false;
            errors: [];

            var self = this;

            var systemid = this.systemId;

            if(systemid == null)
                systemid = this.$refs.system.system == null ? '' : this.$refs.system.system.id;

            var timerDateStr = '';
            // date was selected instead of countdown
            if (this.$refs.date && this.$refs.date.dt && this.$refs.time.time) {
                timeDt = this.$refs.time.time;
                timerDateStr = moment.utc(this.$refs.date.dt).add(timeDt.getHours(), 'hours').add(timeDt.getMinutes(), 'minutes').toISOString();
            }
            else if (this.$refs.duration && this.$refs.duration.durationDate instanceof Date && !isNaN(this.$refs.duration.durationDate)) {
                timerDateStr = this.$refs.duration.durationDate.toISOString();
            }
            else if (this.timerDate != null) {
                timerDateStr = this.timerDate.toISOString();
            }

            var token = this.$root.$data.token;
            var header = this.$root.$data.header;
            var ajaxHeaders = {};
            ajaxHeaders[header] = token;

            $.ajax({
                cache: false,
                type: 'POST',
                url: "AddTimer",
                data: {
                    system_id: systemid,
                    timer_type_id: this.timerType,
                    timer_datetime: timerDateStr,
                    comment: this.comment,
                    structure_type_id: this.structureType === '' ? null : this.structureType,
                    hostility_type_id: this.hostilityType,
                    structure_id: this.structureID,
                    planet: this.planet
                },
                dataType: "json",
                headers: ajaxHeaders
            }).done(function (data) {

                if (data.success) {

                    self.resetForm();

                    if (self.$toast != null) {

                        self.$toast.success('Timer Added succesfully!', {
                            position: 'bottom'
                        });
                    }

                    self.$emit('timer-added');
                }
                else {
                    self.showError = true;
                    self.errors = data.messages;
                }

            });
        },
        loadTimer: function (id) {

            var me = this;

            $.getJSON('GetTimer?id=' + id, null, function (data) {

                //me.timerType = d.TimerTypeID;
                me.structureType = data.structure_type_id;
                me.hostilityType = data.hostility_type_id;
                me.comment = data.comment;
                me.structureID = data.structure_id;
                me.systemId = data.system_id;
                me.systemName = data.solar_system;

                if(me.structureID != null)
                    me.loadStructure();
                else if(me.systemName != null)
                    me.loadSolarSystem(me.systemName);
                              
            });
        }
    }
}


