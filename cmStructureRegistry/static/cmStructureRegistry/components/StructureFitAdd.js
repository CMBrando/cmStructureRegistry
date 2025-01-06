const fit_groups = ['High Power Slots', 'Medium Power Slots', 'Low Power Slots', 'Rig Slots', 'Service Slots', 'Charges',
    'High Power', 'Medium Power', 'Low Power', 'Rig Slot', 'Service Slot', 'Fighters'
];

export default {
    template: '#structure-fit',
    data: function () {
        return {
            market_types: [],
            fit_text: '',
            fit: null,
            structure_name: ''

        };
    },
    props: ['structure_id'],
    mounted: function () {

        if(this.structure_id != null)
            this.getStructureName();

        this.$emit('created');

        this.$refs.structFit.focus();
    },
    watch: {
        structure_id: function (value) {


        }
    },
    methods: {
        getStructureName: function () {
            var me = this;

            $.get('GetStructure?structureID=' + this.structure_id, function (data) {
                me.structure_name = data.structure_name;
            });
        },
        onPaste: function(evt) {
            var raw = evt.clipboardData.getData('text/plain');
            this.parseFits(raw);
        },
        parseFits: function (raw) {

            var $that = this;
            var names = raw.split('\n');

            var fitItems = {};
            var currGroup = null;

            _.each(names, function (name) {

                // trim leading and trailing whitespace on the line and multiple spaces to one space
                name = s.clean(name);
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

                    var subItem = _.find($that.market_types, function (obj) { return obj.name == name; });

                    if (subItem != null) {

                        // if already in list increment
                        var fItem = _.find(fitItems[currGroup], function (item) { return item.id == subItem.id; });

                        // if exists increment
                        if (fItem != null)
                            fItem.multiplier = fItem.multiplier + num;
                        else
                            fitItems[currGroup].push({ name: name, id: subItem.id, multiplier: num });
                    }
                    else { // not a market type but add anyways

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

            //console.log(fitItems);
            this.fit = fitItems;

        },
        addFit: function () {

            if (this.structure_id == null) {
                toastr.error('Please select a structure.')
                return;
            }

            if (this.fit == null) {
                toastr.error('Please paste in a valid fit to parse')
                return;
            }

            var self = this;

            var token = this.$root.$data.token;
            var header = this.$root.$data.header;
            var ajaxHeaders = {};
            ajaxHeaders[header] = token;

            $.ajax({
                cache: false,
                type: 'POST',
                url: "AddStructureFit?structureID=" + this.structure_id,
                contentType: "application/json; charset=utf-8",
                data: JSON.stringify(this.fit),
                dataType: "json",
                headers: ajaxHeaders
            }).done(function (data) {

                if (data.success) {

                    //self.structure_id = null;
                    self.fit_text = '';
                    self.fit = null;
                    //self.resetSearch();

                    toastr.success('Structure Fit added successfully!')

                    self.$emit('fit-modified');
                }
                else {
                    toastr.error(data.msgs[0])
                }
            }).fail(function () {
                toastr.error('An error occurred while trying to save the fit')
            });
        }
    }
}

