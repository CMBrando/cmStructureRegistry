export default {
    template: '#structure-add-registry',
    props: ['structure_id'],
    data: function () {
        return {
            structureName: '',
            structureType: '',
            structureTypes: [],
            corporationName: null,
            showError: false,
            errors: []
        };
    },
    created: function () {
        this.loadTypes();

        if (this.structure_id)
            this.loadStructure();
    },
    mounted: function () {
        this.$emit('created');
        this.$refs.structureName.focus();
    },
    methods: {
        loadTypes: function () {
            var self = this;

            $.get('GetStructureTypes?', function (data) {
                self.structureTypes = data;
            });
        },
        onStructureNameInput: function () {
            var regex = /\[([^\]]+)\]/;
            var match = this.structureName.match(regex);

            // if match then it's a POCO structure and can set the corporation name
            if(match) {
                this.corporationName = match[1];
                this.structureType = 18;  // POCO
            }                

            //var name = s.clean(this.structureName);
            //if (name.slice(-1) === ')') {
            //    this.structureName = name.substring(0, name.lastIndexOf(' ('));
            //    this.corporationName = name.substring(name.lastIndexOf('(') + 1, name.length - 1);
            //}
        },
        loadStructure: function () {
            var self = this;
            $.get('GetStructure?structureID=' + this.structure_id, function (data) {
                self.structureName = data.structure_name;
                self.structureType = data.structure_type_id;
                self.corporationName = data.corporation;
            });
        },
        saveStructure: function () {

            var self = this;
            this.showError = false;

            var token = this.$root.$data.token;
            var header = this.$root.$data.header;
            var ajaxHeaders = {};
            ajaxHeaders[header] = token;

            $.ajax({
                cache: false,
                type: 'POST',
                url: "SaveStructure",
                data: {
                    structure_id: this.structure_id,
                    structure_name: this.structureName,
                    structure_type_id: this.structureType === '' ? null : this.structureType,
                    corporation_name: this.corporationName
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
