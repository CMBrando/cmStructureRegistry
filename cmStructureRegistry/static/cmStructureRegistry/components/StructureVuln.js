export default {
    template: '#structure-vulnerability',
    props: ['structure_id'],
    data: function () {
        return {
            vuln: '',
            vuln_list: [],
            structure_name: ''
        };
    },
    mounted: function () {

        var arr = _.range(24);
        this.vuln_list = _.map(arr, function (a) { return ('' + a).padStart(2, '0') + '00'; });
        this.vuln_list.unshift('');

        if (this.structure_id != null)
            this.loadStructure();

        this.$emit('created');

        this.$refs.structVuln.focus();
    },
    methods: {
        loadStructure: function () {
            var me = this;

            $.get('GetStructure?structureID=' + this.structure_id + '&_t=' + (new Date()).getTime(), function (data) {
                me.structure_name = data.structure_name;
                me.vuln = data.vulnerability;
            });
        },
        addVuln: function () {

            var self = this;

            var token = this.$root.$data.token;
            var header = this.$root.$data.header;
            var ajaxHeaders = {};
            ajaxHeaders[header] = token;

            this.showProcessing = true;

            $.ajax({
                cache: false,
                type: 'POST',
                url: "SaveStructureVulnerability",
                data: { structureID: this.structure_id, vulnerability: this.vuln },
                dataType: "json",
                headers: ajaxHeaders
            }).done(function (data) {

                if (data.success) {
                    toastr.success('Vulnerability set successfully!')
                    self.$emit('vuln-modified');
                }
            });
        }
    }
}