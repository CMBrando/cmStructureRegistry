const FIT_GROUPS = ['High Power Slots', 'Medium Power Slots', 'Low Power Slots', 'Rig Slots', 'Service Slots', 'Charges',
    'High Power', 'Medium Power', 'Low Power', 'Rig Slot', 'Service Slot', 'Fighters'
];

const STRUCTURE_FIT_DEFAULTS = new Map([
    [7, "Service Slots\r\nStandup Conduit Generator I"],
    [8, "Service Slots\r\nStandup Cynosural Field Generator I"],
    [9, "Service Slots\r\nStandup Cynosural System Jammer I"],
    [20, "Service Slots\r\nStandup Metenox Moon Drill"]
])



const POS_TYPE = 12
const MERC_DEN_TYPE = 21
const ANSIBLEX_TYPE = 7
const ONLINE_TYPES = ['Force Field']

const ROMAN_NUMERALS = [
    "I", "II", "III", "IV", "V",
    "VI", "VII", "VIII", "IX", "X",
    "XI", "XII", "XIII", "XIV", "XV",
    "XVI", "XVII", "XVIII", "XIX", "XX",
    "XXI", "XXII", "XXIII", "XXIV", "XXV"
]

export default {
    template: '#structure-add-registry',
    props: ['structure_id'],
    data: function () {
        return {
            structureName: '',
            structureType: '',
            structureTypes: [],
            systemId: null, // for merc den, POS
            planet: null, // for merc den, POS
            planets: [], // for merc den, POS
            moon: null, // for POS
            moons: [], // for POS
            corporationName: null,
            fitText: null,
            vulnList: null,
            structVuln: null,
            structVulnText: null,
            nextVuln: null,
            nextVulnDate: null,
            fit: null,
            posOnline: false,
            showError: false,
            errors: [],
            posTypes: [],
            systemName: null,
            submitting: false
        };
    },
    watch: {
        systemId: function () {
            if(this.systemId)
                this.loadPlanets();
            else
                this.planets = [];
        },
        structureType: function() {
            this.structureTypeChanged()
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

            $.get('GetStructureTypes', function (data) {
                self.structureTypes = data;
            });

            $.get('GetPOSTypes', function (data) {
                self.posTypes = data;
            });

        },
        loadPlanets: function () {
            var me = this;
            $.get('GetPlanets?solarSystemID=' + this.systemId, function (data) {
                me.planets = data;
                me.planetChanged();
            });
        },
        planetChanged: function() {
            var $that = this;
            this.moon = null;
            var item = _.find(this.planets, function(p) { return p.name == $that.planet; });
            if(item && item.moon_count > 0) {
                $that.moons = Array.from({ length: item.moon_count }, (_, i) => `Moon ${i + 1}`);
           }
            else {
                $that.moons = [];
            }
        },
        structureTypeChanged: function() {
                
                // set structure based on default
                var sfd = STRUCTURE_FIT_DEFAULTS;
                if(sfd.has(this.structureType)) {
                    this.fitText = sfd.get(this.structureType);
                    this.parseFits();
                }
        },
        loadStructure: function () {
            var self = this;
            $.get('GetStructure?structureID=' + this.structure_id, function (data) {
                self.structureName = data.structure_name;
                self.structureType = data.structure_type_id;
                self.corporationName = data.corporation;
                self.structVuln = data.vulnerability;
                self.posOnline = data.pos_online;
                self.systemId = data.solar_system_id;
                self.systemName = data.solar_system;

                if(self.structureType == POS_TYPE || self.structureType == MERC_DEN_TYPE) {
                    self.loadPlanets();
                    self.loadDataFromName();
                }
                    
            });
        },        
        systemChanged: function (system) {
            this.systemId = system.id;
        },                       
        onStructureNameInput: function () {
            var name = _.trim(this.structureName).replace(/\s+/g, ' ');
            if (name.slice(-1) === ')') {
                this.structureName = name.substring(0, name.lastIndexOf(' ('));
                this.corporationName = name.substring(name.lastIndexOf('(') + 1, name.length - 1);

                if(this.structureName.indexOf('»') > -1)
                    this.structureType = ANSIBLEX_TYPE;
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
        loadDataFromName: function() {

            var regex = /\(([A-Z0-9\-]+)\s+(I|II|III|IV|V|VI|VII|VIII|IX|X|XI|XII|XIII|XIV|XV|XVI|XVII|XVIII|XIX|XX|XXI|XXII|XXIII|XXIV|XXV)(?:\s+-\s+(Moon\s+(?:[1-9]|1[0-9]|2[0-5])))?\)/;
            var name = this.structureName;

            const match = name.match(regex)
            if(match) {
                var solarSystem = match[1];
                var numeral = match[2];
                var moon = match[3];

                if(solarSystem) {
                    this.structureName = _.trim(name.substring(0, name.indexOf("(")));
                }

                if(numeral) {
                    var index = ROMAN_NUMERALS.indexOf(numeral);
                    this.planet = "Planet " + (index + 1);
                }

                if(moon) {
                    var me = this;
                    setTimeout(function() { me.moon = moon; }, 100);
                }
            }
        },      
        parseVulnerability: function() {
            if(this.structVulnText) {
                var lines = this.structVulnText.split('\n');            
                if(lines.length == 2) {
                    this.structVuln = _.trim(lines[1].substring(_.indexOf(lines[1], ':') + 1)).replace(":", "")                    
                }
                else if(lines.length == 4) {
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

            // reset POS flag
            this.posOnline = false;            

            var $that = this;
            _.each(names, function (name) {

                var num = 1;

                if (name === '')
                    return;

                // check if we're parsing POS
                if(name.includes('\t') && name.split('\t').length == 4)
                {
                    var row = name.split('\t');
                    var id = parseInt(row[0]);
                    var itemName = row[2];
                    var itemGroup = row[1];                    

                    // look up item in POS list
                    var item = _.find($that.posTypes, function(t) { return t.id == id; });

                    // handle special fields
                    if(ONLINE_TYPES.includes(itemName)) {
                        $that.posOnline = true;                    
                    }
                    else if(item) {
                        itemName = item.name;
                        itemGroup = item.group;
                    }
                    else
                        return;  // don't process items not in POS list

                    if(fitItems[itemGroup] == null)
                        fitItems[itemGroup] = []

                    var fItem = _.find(fitItems[itemGroup], function (item) { return item.name == itemName });

                    if (fItem != null)
                        fItem.multiplier = fItem.multiplier + num;
                    else
                        fitItems[itemGroup].push({ name: itemName, id: null, multiplier: num });
                    
                }
                else {

                    // trim leading and trailing whitespace on the line and multiple spaces to one space
                    name = _.trim(name).replace(/\s+/g, ' ');

                    // match pre-number
                    var res = name.match(/^\d?[,]?\d+x /);

                    // if no number don't find and add
                    if (res != null && res.length == 1) {
                        name = name.replace(res[0], '');
                        num = res[0].replace(/,/g, '').replace('x ', ''); // this is to get the multiplier
                    }

                    // check if grouping first, otherwise a fit item
                    if (_.findIndex(FIT_GROUPS, function (item) { return item.toLowerCase() === name.toLowerCase(); }) > -1) {
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
                }

            });

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


            this.submitting = true;

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
                    planet: this.planet,
                    moon: this.moon,
                    pos_online: (this.structureType == POS_TYPE ? (this.posOnline ? 1 : 0) : 0)
                },
                dataType: "json",
                headers: ajaxHeaders
            }).done(function (data) {

                self.submitting = false;

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
