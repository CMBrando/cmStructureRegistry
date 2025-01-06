export default {
    template: '#structure-remove',
    props: ['structure_id', 'structure_name'],
    data: function () {
        return {
        };
    },
    mounted: function () {
        this.$emit('created');
    },
    methods: {
        cancelRemove: function () {
            this.$emit('structure-canceled');
        },
        removeStructure: function () {

            var self = this;

            var token = this.$root.$data.token;
            var header = this.$root.$data.header;
            var ajaxHeaders = {};
            ajaxHeaders[header] = token;

            this.showProcessing = true;

            $.ajax({
                cache: false,
                type: 'POST',
                url: "RemoveStructure",
                data: { structureID: this.structure_id },
                dataType: "json",
                headers: ajaxHeaders
            }).done(function (data) {

                if (data.success) {

                    if (toastr != null) {
                        toastr.success('Structure Removed Successfully.');
                    }
                    
                    self.$emit('structure-removed');
                }
            });
        }
    }
}