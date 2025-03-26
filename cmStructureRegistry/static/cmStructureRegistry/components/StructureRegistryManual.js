const fit_groups = ['High Power Slots', 'Medium Power Slots', 'Low Power Slots', 'Rig Slots', 'Service Slots', 'Charges',
    'High Power', 'Medium Power', 'Low Power', 'Rig Slot', 'Service Slot', 'Fighters'
];

export default {
    template: '#structure-add-registry',
    props: ['structure_id'],
    data: function () {
        return {
            structureName: '',
            structureType: '',
            structureTypes: [],
            systemId: null, // for merc den
            planet: null, // for merc den
            planets: [], // for merc den    
            corporationName: null,
            fitText: null,
            vulnList: null,
            structVuln: null,
            structVulnText: null,
            nextVuln: null,
            nextVulnDate: null,
            fit: null,
            showError: false,
            errors: []
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
    created: function () {
        this.loadTypes();

        var arr = _.range(24);
        this.vulnList = _.map(arr, function (a) { return ('' + a).padStart(2, '0') + '00'; });
        this.vulnList.unshift('');

        if (this.structure_id)
            this.loadStructure();
    },
    mounted: function () {
        this.$emit('created');

        this.$refs.structureName.focus();

        var questions = $(this.$el).find('.fa-circle-question');

        var tt = new bootstrap.Tooltip(questions[0], {
            trigger: 'hover',
            placement: 'top',
            title: function() {
                return $(questions[0]).attr('title');
            }
        });

        if(questions.length > 1) {
            var tt2 = new bootstrap.Tooltip(questions[1], {
                trigger: 'hover',
                placement: 'top',
                title: function() {
                    return $(questions[1]).attr('title');
                }
            });
        }
    },
    methods: {
        loadTypes: function () {
            var self = this;

            $.get('GetStructureTypes?', function (data) {
                self.structureTypes = data;
            });
        },
        systemChanged: function (system) {
            this.systemId = system.id;
        },
        loadPlanets: function () {
            var me = this;
            $.get('GetPlanets?solarSystemID=' + this.systemId, function (data) {
                me.planets = data;
            });
        },               
        onStructureNameInput: function () {
            var name = _.trim(this.structureName).replace(/\s+/g, ' ');
            if (name.slice(-1) === ')') {
                this.structureName = name.substring(0, name.lastIndexOf(' ('));
                this.corporationName = name.substring(name.lastIndexOf('(') + 1, name.length - 1);
            }
            else {            
                var regex = /\[([^\]]+)\]/;
                var match = this.structureName.match(regex);

                if(match) {
                    this.corporationName = match[1];

                    if(this.structureName.includes("Skyhook"))
                        this.structureType = 19;
                    else
                        this.structureType = 18;  // POCO
                }

                if(this.structureName.includes("Mercenary Den")) {
                    this.structureType = 21;
                }
            }
        },
        loadStructure: function () {
            var self = this;
            $.get('GetStructure?structureID=' + this.structure_id, function (data) {
                self.structureName = data.structure_name;
                self.structureType = data.structure_type_id;
                self.corporationName = data.corporation;
                self.structVuln = data.vulnerability;
            });
        },
        parseVulnerability: function() {
            if(this.structVulnText) {
                var lines = this.structVulnText.split('\n');            
                if(lines.length == 4) {
                    this.structVuln = _.trim(lines[1].substring(_.indexOf(lines[1], ':') + 1)).replace(":", "")
                    this.nextVuln = _.trim(lines[2].substring(_.indexOf(lines[2], ':') + 1)).replace(":", "")
                    this.nextVulnDate = _.trim(lines[3].substring(_.indexOf(lines[3], ':') + 1))
                }
            }
            else {
                this.structVuln = null;
                this.nextVuln = null;
                this.nextVulnDate = null;
            }
        },
        parseFits: function () {

            var raw = _.trim(this.fitText);
            var names = raw.split('\n');

            var fitItems = {};
            var currGroup = null;

            var $that = this;
            _.each(names, function (name) {

                // trim leading and trailing whitespace on the line and multiple spaces to one space
                name = _.trim(name).replace(/\s+/g, ' ');
                var num = 1;

                if (name === '')
                    return;

                // match pre-number
                var res = name.match(/^\d?[,]?\d+x /);

                // if no number don't find and add
                if (res != null && res.length == 1) {
                    name = name.replace(res[0], '');
                    num = res[0].replace(/,/g, '').replace('x ', ''); // this is to get the multiplier
                }

                // check if grouping first, otherwise a fit item
                if (_.findIndex(fit_groups, function (item) { return item.toLowerCase() === name.toLowerCase(); }) > -1) {
                    currGroup = name;
                    fitItems[currGroup] = [];
                }
                else {
                    // if already in list increment
                    var fItem2 = _.find(fitItems[currGroup], function (item) { return item.name == name });

                    // if exists increment
                    if (fItem2 != null)
                        fItem2.multiplier = fItem2.multiplier + num;
                    else
                        fitItems[currGroup].push({ name: name, id: null, multiplier: num });
                }

            });

            //console.log(fitItems);
            this.fit = fitItems;

        },       
        saveStructure: function () {

            var self = this;
            this.showError = false;

            var token = this.$root.$data.token;
            var header = this.$root.$data.header;
            var ajaxHeaders = {};
            ajaxHeaders[header] = token;

            var fitEncoded = null;
            if(this.fit && JSON.stringify(this.fit) !== '{}') {
                var encoder = new TextEncoder()
                var uint8Array = encoder.encode(JSON.stringify(this.fit));
                fitEncoded = btoa(String.fromCodePoint(...uint8Array));
            }

            var nextVulnISODate = ''
            if(this.nextVulnDate)
                nextVulnISODate = moment.utc(this.nextVulnDate, 'YYYY.MM.DD HH:mm').toISOString()

            $.ajax({
                cache: false,
                type: 'POST',
                url: "SaveStructure",
                data: {
                    structure_id: this.structure_id,
                    structure_name: this.structureName,
                    structure_type_id: this.structureType === '' ? null : this.structureType,
                    corporation_name: this.corporationName,
                    vulnerability: this.structVuln,
                    next_vulnerability: this.nextVuln,
                    next_vulnerability_date: nextVulnISODate,
                    fit: fitEncoded,
                    system_id: this.systemId,
                    planet: this.planet
                },
                dataType: "json",
                headers: ajaxHeaders
            }).done(function (data) {

                if (data.success) {

                    if (toastr != null) {
                        var msg = 'Structure ' + (self.structure_id ? 'Updated' : 'Added') + ' Successfully!'
                        toastr.success(msg);
                    }

                    self.$emit('structure-added');
                }
                else {
                    self.showError = true;
                    self.errors = data.messages;
                }

            });
        },
        closeWindow: function() {
            this.$emit('registryadd-closed');
        },
    }
}
